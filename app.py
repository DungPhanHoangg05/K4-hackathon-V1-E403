"""
app.py — VLearn AI Companion backend

Chạy: 
    export GEMINI_API_KEY="..."
    pip install -r requirements.txt
    python app.py

Endpoints:
    GET  /                          -> phục vụ index.html
    GET  /api/library               -> thư viện slide THẬT, đọc từ data/vlearn-pack/slides
    GET  /api/library/refresh       -> quét lại thư mục slide (bỏ cache)
    POST /api/chat                  -> hỏi đáp / tóm tắt, có gọi Gemini với ngữ cảnh slide thật
"""

import os
import re
import json
import logging
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai

load_dotenv()  # đọc GEMINI_API_KEY (và các biến khác) từ file .env cạnh app.py

from codebase.working.slide_index import build_library, find_file, get_page, get_page_range
from flask import send_file, abort

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("vlearn")

APP_ROOT = Path(__file__).resolve().parent
WEB_ROOT = APP_ROOT / "codebase" / "working"
PROMPT_CANDIDATES = [
    APP_ROOT / "prompts" / "system_prompt.txt",
    APP_ROOT / "prompts" / "system_prompt",
]
PROMPT_PATH = next((p for p in PROMPT_CANDIDATES if p.exists()), PROMPT_CANDIDATES[0])

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")
MAX_CONTEXT_CHARS = int(os.environ.get("VLEARN_MAX_CONTEXT_CHARS", "12000"))

if not GEMINI_API_KEY:
    log.warning(
        "GEMINI_API_KEY chưa được thiết lập. Đặt biến môi trường GEMINI_API_KEY "
        "trước khi gửi câu hỏi tới /api/chat."
    )
else:
    genai.configure(api_key=GEMINI_API_KEY)

if PROMPT_PATH.exists():
    SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")
else:
    SYSTEM_PROMPT = "Bạn là trợ lý AI hỗ trợ học viên tóm tắt và giải thích nội dung slide VLearn."
    log.warning("Không tìm thấy file prompt ở %s; đang dùng prompt mặc định.", PROMPT_PATH)

app = Flask(__name__, static_folder=str(WEB_ROOT), static_url_path="")


# --------------------------------------------------------------------------
# Thư viện slide thật
# --------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(str(WEB_ROOT), "index.html")


@app.route("/api/library", methods=["GET"])
def api_library():
    lib = build_library()
    return jsonify(_public_library(lib))


@app.route("/api/library/refresh", methods=["POST", "GET"])
def api_library_refresh():
    lib = build_library(force=True)
    return jsonify(_public_library(lib))


def _public_library(lib: dict) -> dict:
    """Bỏ field nội bộ (_source_mtime) trước khi trả về client."""
    return {k: v for k, v in lib.items() if not k.startswith("_")}


@app.route("/api/file/<file_id>", methods=["GET"])
def api_file_raw(file_id):
    """Trả về file PDF gốc (bytes thật) để frontend render bằng pdf.js."""
    lib = build_library()
    _, f = find_file(lib, file_id)
    if not f:
        abort(404)
    path = Path(f["path"])
    if not path.exists():
        abort(404)
    return send_file(str(path), mimetype="application/pdf")


# --------------------------------------------------------------------------
# Lịch sử hội thoại — lưu theo từng file_id, mỗi cuộc trò chuyện 1 bản ghi.
# --------------------------------------------------------------------------

CONV_DIR = APP_ROOT / "data" / "vlearn-pack" / ".conversations"


def _conv_path(conv_id: str) -> Path:
    safe = re.sub(r"[^a-zA-Z0-9_-]", "", conv_id)[:64]
    return CONV_DIR / f"{safe}.json"


@app.route("/api/conversations", methods=["GET"])
def api_conversations_list():
    file_id = request.args.get("file_id", "")
    CONV_DIR.mkdir(parents=True, exist_ok=True)
    out = []
    for p in sorted(CONV_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if file_id and data.get("file_id") != file_id:
            continue
        out.append({
            "id": data.get("id"),
            "title": data.get("title") or "Cuộc trò chuyện",
            "file_id": data.get("file_id"),
            "file_name": data.get("file_name"),
            "updated_at": data.get("updated_at"),
        })
    return jsonify({"conversations": out})


@app.route("/api/conversations/<conv_id>", methods=["GET"])
def api_conversations_get(conv_id):
    p = _conv_path(conv_id)
    if not p.exists():
        abort(404)
    return jsonify(json.loads(p.read_text(encoding="utf-8")))


@app.route("/api/conversations/<conv_id>", methods=["POST"])
def api_conversations_save(conv_id):
    body = request.get_json(force=True, silent=True) or {}
    CONV_DIR.mkdir(parents=True, exist_ok=True)
    from datetime import datetime as _dt
    record = {
        "id": conv_id,
        "title": body.get("title") or "Cuộc trò chuyện",
        "file_id": body.get("file_id"),
        "file_name": body.get("file_name"),
        "messages": body.get("messages") or [],
        "updated_at": _dt.utcnow().isoformat() + "Z",
    }
    _conv_path(conv_id).write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    return jsonify({"ok": True})


@app.route("/api/conversations/<conv_id>", methods=["DELETE"])
def api_conversations_delete(conv_id):
    p = _conv_path(conv_id)
    if p.exists():
        p.unlink()
    return jsonify({"ok": True})


# --------------------------------------------------------------------------
# Chat / tóm tắt — luồng chính: học viên trễ bài xin tóm tắt slide đang xem
# --------------------------------------------------------------------------

SUMMARY_KEYWORDS = ["tóm tắt", "tom tat", "summary", "summarize"]
BROAD_SUMMARY_KEYWORDS = ["buổi hôm nay", "hôm nay", "cả bài", "toàn bộ", "buổi học"]

TEST_ANSWER_PATTERNS = [
    r"đáp án (bài|đề) (kiểm tra|thi|test|quiz)",
    r"cho (mình|tôi) (đáp án|answer key)",
    r"giải (hộ|giúp) (bài kiểm tra|bài thi|đề thi)",
    r"làm hộ bài tập.*(nộp|chấm điểm)",
    r"leak(ed)? (exam|test|quiz)",
]


def _looks_like_test_answer_request(text: str) -> bool:
    low = text.lower()
    return any(re.search(p, low) for p in TEST_ANSWER_PATTERNS)


def _is_scope_ambiguous(text: str, file_id: str, page: int, page_from: int, page_to: int) -> bool:
    low = text.lower()
    wants_broad_summary = any(k in low for k in BROAD_SUMMARY_KEYWORDS)
    has_summary_intent = any(k in low for k in SUMMARY_KEYWORDS)
    if has_summary_intent and wants_broad_summary and not file_id:
        return True
    if has_summary_intent and not file_id:
        return True
    if has_summary_intent and page_from is None and page_to is None and not page:
        return True
    return False


@app.route("/api/chat", methods=["POST"])
def api_chat():
    body = request.get_json(force=True, silent=True) or {}
    message = (body.get("message") or "").strip()
    file_id = body.get("file_id")
    page = body.get("page")
    page_from = body.get("page_from")
    page_to = body.get("page_to")
    history = body.get("history") or []  # [{role: "user"|"model", text: "..."}]

    if not message:
        return jsonify({"error": "Thiếu 'message'."}), 400

    lib = build_library()

    # 1) Chặn yêu cầu đáp án bài kiểm tra / gian lận học thuật — không cần gọi model.
    if _looks_like_test_answer_request(message):
        return jsonify({
            "reply": (
                "Mình không thể cung cấp đáp án bài kiểm tra/bài thi hoặc làm hộ bài được "
                "chấm điểm — điều đó vi phạm chính sách học thuật. Mình có thể giúp bạn ôn "
                "lại khái niệm liên quan hoặc tóm tắt slide lý thuyết liên quan, bạn muốn "
                "vậy không?"
            ),
            "citations": [],
            "needs_clarification": False,
            "blocked_reason": "academic_integrity",
        })

    # 2) Phạm vi chưa rõ -> hỏi lại thay vì đoán.
    if _is_scope_ambiguous(message, file_id, page, page_from, page_to):
        clarification = _build_clarification_question(lib, message)
        return jsonify({
            "reply": clarification,
            "citations": [],
            "needs_clarification": True,
        })

    # 3) Nếu file_id không tồn tại trong thư viện thật -> báo lỗi rõ ràng, không bịa.
    if file_id:
        _, f = find_file(lib, file_id)
        if not f:
            return jsonify({
                "reply": (
                    "Mình không tìm thấy tài liệu này trong thư viện slide hiện có. "
                    "Bạn kiểm tra lại tên file hoặc chọn lại từ danh sách bên trái nhé."
                ),
                "citations": [],
                "needs_clarification": True,
            })

    # 4) Dựng ngữ cảnh slide thật cho model.
    context_pages, context_label = _gather_context(lib, file_id, page, page_from, page_to)

    if file_id and not context_pages:
        return jsonify({
            "reply": (
                "Mình không tìm thấy nội dung nào trong phạm vi trang bạn chọn của tài liệu "
                "này. Bạn thử chọn lại số trang hoặc mở rộng phạm vi nhé."
            ),
            "citations": [],
            "needs_clarification": True,
        })

    reply_text, citations = _call_gemini(message, context_pages, context_label, history)

    return jsonify({
        "reply": reply_text,
        "citations": citations,
        "needs_clarification": False,
    })


def _build_clarification_question(lib: dict, message: str) -> str:
    day_names = [d["name"] for d in lib.get("days", [])]
    if not day_names:
        return (
            "Hiện thư viện chưa có slide nào (kiểm tra thư mục data/vlearn-pack/slides). "
            "Bạn upload slide thật rồi thử lại nhé."
        )
    options = ", ".join(day_names[:6])
    return (
        f"Bạn muốn mình tóm tắt tài liệu/buổi học nào và từ trang mấy đến trang mấy? "
        f"Hiện có: {options}. Nếu chỉ muốn 1 slide đang xem, hãy chọn đúng trang hiện tại rồi hỏi lại."
    )


def _gather_context(lib, file_id, page, page_from, page_to, max_pages_no_range=1):
    """Trả về (list[page_dict], label) — TOÀN BỘ text lấy thật từ slide, không sinh thêm."""
    if not file_id:
        return [], ""

    _, f = find_file(lib, file_id)
    if not f:
        return [], ""

    if page_from and page_to:
        pages = get_page_range(lib, file_id, int(page_from), int(page_to))
        label = f"{f['name']} — trang {page_from}–{page_to}"
    elif page:
        p = get_page(lib, file_id, int(page))
        pages = [p] if p else []
        label = f"{f['name']} — trang {page}"
    else:
        pages = f["pages"][:max_pages_no_range]
        label = f"{f['name']} — trang {pages[0]['page'] if pages else '?'}"

    return pages, label


def _format_context_block(pages, label) -> str:
    if not pages:
        return "(Không có nội dung slide nào được cấp cho câu hỏi này.)"
    parts = [f"# Tài liệu: {label}"]
    total_chars = 0
    for p in pages:
        chunk = f"\n## Trang {p['page']}\n{p['text'] or '(trang không có text trích xuất được)'}"
        total_chars += len(chunk)
        if total_chars > MAX_CONTEXT_CHARS:
            parts.append("\n[...ngữ cảnh bị cắt bớt do quá dài...]")
            break
        parts.append(chunk)
    return "\n".join(parts)


def _call_gemini(message, context_pages, context_label, history):
    if not GEMINI_API_KEY:
        return (
            "Chưa cấu hình GEMINI_API_KEY trên server nên mình chưa thể trả lời qua Gemini. "
            "Vui lòng thiết lập biến môi trường GEMINI_API_KEY rồi thử lại.",
            [],
        )

    context_block = _format_context_block(context_pages, context_label)

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL_NAME,
        system_instruction=SYSTEM_PROMPT,
    )

    convo = []
    for turn in history[-10:]:
        role = "user" if turn.get("role") == "user" else "model"
        convo.append({"role": role, "parts": [turn.get("text", "")]})

    user_turn = (
        f"NGỮ CẢNH SLIDE (nội dung thật, trích từ file):\n{context_block}\n\n"
        f"CÂU HỎI CỦA HỌC VIÊN:\n{message}"
    )
    convo.append({"role": "user", "parts": [user_turn]})

    try:
        response = model.generate_content(convo)
        reply_text = (response.text or "").strip()
    except Exception as e:
        log.exception("Lỗi khi gọi Gemini API")
        return (
            f"Xin lỗi, mình gặp lỗi khi gọi mô hình AI ({e}). Bạn thử lại sau ít phút nhé.",
            [],
        )

    citations = [{"page": p["page"], "excerpt": (p["text"] or "")[:200]} for p in context_pages]
    return reply_text, citations


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")