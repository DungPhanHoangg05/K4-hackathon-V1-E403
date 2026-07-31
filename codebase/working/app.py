"""
app.py — VLearn AI Companion backend

Chạy từ thư mục gốc dự án:
    export GEMINI_API_KEY="..."
    pip install -r requirements.txt
    python codebase/working/app.py

Hoặc chạy trực tiếp từ codebase/working:
    python app.py

Endpoints:
    GET  /                         -> phục vụ index.html
    GET  /api/library              -> thư viện slide THẬT, đọc từ data/vlearn-pack/slides
    GET  /api/library/refresh      -> quét lại thư mục slide (bỏ cache)
    POST /api/chat                 -> hỏi đáp / tóm tắt, có gọi Gemini với ngữ cảnh slide thật
"""

import os
import re
import json
import logging
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory, send_file, abort
import google.generativeai as genai

# Định vị thư mục:
# WORKING_DIR = codebase/working
# PROJECT_ROOT = thư mục gốc dự án (chứa prompts/, data/, ...)
WORKING_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = WORKING_DIR.parent.parent

# Load .env từ gốc dự án hoặc thư mục làm việc
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(WORKING_DIR / ".env")

# Import module slide_index nằm cùng thư mục codebase/working
from slide_index import build_library, find_file, get_page, get_page_range

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("vlearn")

WEB_ROOT = WORKING_DIR

PROMPT_CANDIDATES = [
    PROJECT_ROOT / "prompts" / "system_prompt.txt",
    PROJECT_ROOT / "prompts" / "system_prompt",
    WORKING_DIR / "prompts" / "system_prompt.txt",
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

CONV_DIR = PROJECT_ROOT / "data" / "vlearn-pack" / ".conversations"


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


PAGE_RANGE_PATTERNS = [
    r"(?:từ\s*)?(?:trang|slide|page|tr\.?)\s*(\d+)\s*(?:-|–|—|đến|den|tới|toi|->|to)\s*(?:trang|slide|page|tr\.?)?\s*(\d+)",
    r"\b(\d+)\s*(?:-|–|—)\s*(\d+)\b",
]
PAGE_SINGLE_PATTERN = r"(?:trang|slide|page|tr\.?)\s*(\d+)"
WHOLE_DOC_KEYWORDS = ["toàn bộ", "toan bo", "cả bài", "ca bai", "cả file", "ca file",
                      "tất cả", "tat ca", "whole", "entire", "all pages", "cả tài liệu"]


def _parse_page_scope(text: str):
    low = (text or "").lower()

    for pattern in PAGE_RANGE_PATTERNS:
        m = re.search(pattern, low)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            return min(a, b), max(a, b), False

    m = re.search(PAGE_SINGLE_PATTERN, low)
    if m:
        p = int(m.group(1))
        return p, p, False

    if any(k in low for k in WHOLE_DOC_KEYWORDS):
        return None, None, True

    return None, None, False


def _is_scope_ambiguous(text: str, file_id: str) -> bool:
    has_summary_intent = any(k in (text or "").lower() for k in SUMMARY_KEYWORDS)
    return has_summary_intent and not file_id


@app.route("/api/chat", methods=["POST"])
def api_chat():
    body = request.get_json(force=True, silent=True) or {}
    message = (body.get("message") or "").strip()
    file_id = body.get("file_id")
    page = body.get("page")
    page_from = body.get("page_from")
    page_to = body.get("page_to")
    history = body.get("history") or []

    if not message:
        return jsonify({"error": "Thiếu 'message'."}), 400

    lib = build_library()

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

    if _is_scope_ambiguous(message, file_id):
        clarification = _build_clarification_question(lib, message)
        return jsonify({
            "reply": clarification,
            "citations": [],
            "needs_clarification": True,
        })

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

    context_pages, context_label = _gather_context(
        lib, file_id, page, page_from, page_to, message=message
    )

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


MAX_PAGES_FALLBACK = int(os.environ.get("VLEARN_MAX_PAGES_FALLBACK", "40"))


def _gather_context(lib, file_id, page, page_from, page_to, message=""):
    if not file_id:
        return [], ""

    _, f = find_file(lib, file_id)
    if not f:
        return [], ""

    if not page_from and not page_to and not page:
        page_from, page_to, _ = _parse_page_scope(message)

    if page_from and page_to:
        pages = get_page_range(lib, file_id, int(page_from), int(page_to))
        label = f"{f['name']} — trang {page_from}–{page_to}"
    elif page_from or page_to:
        only = int(page_from or page_to)
        p = get_page(lib, file_id, only)
        pages = [p] if p else []
        label = f"{f['name']} — trang {only}"
    elif page:
        p = get_page(lib, file_id, int(page))
        pages = [p] if p else []
        label = f"{f['name']} — trang {page}"
    else:
        pages = f["pages"][:MAX_PAGES_FALLBACK]
        if pages:
            label = f"{f['name']} — trang {pages[0]['page']}–{pages[-1]['page']}"
            if len(f["pages"]) > len(pages):
                label += f" (toàn bộ {f['page_count']} trang, đã giới hạn {len(pages)} trang đầu)"
        else:
            label = f["name"]

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


# --------------------------------------------------------------------------
# Quiz — sinh bộ câu hỏi trắc nghiệm từ tóm tắt nội dung slide
# --------------------------------------------------------------------------

QUIZ_NUM_QUESTIONS = int(os.environ.get("VLEARN_QUIZ_QUESTIONS", "5"))
QUIZ_NUM_OPTIONS = 4

QUIZ_INSTRUCTION = """
Nhiệm vụ lần này: soạn một BỘ CÂU HỎI TRẮC NGHIỆM để kiểm tra xem học viên đã
hiểu bài chưa.

Cách làm:
1. Trước hết hãy tóm tắt trong đầu các ý chính của TOÀN BỘ ngữ cảnh slide được cấp.
2. Từ các ý chính đó, soạn đúng {n} câu hỏi trắc nghiệm, mỗi câu {k} lựa chọn.
3. Câu hỏi phải trải đều các phần khác nhau của tài liệu, không dồn hết vào một trang.

Ràng buộc bắt buộc:
- CHỈ dùng thông tin có thật trong NGỮ CẢNH SLIDE. Không hỏi kiến thức ngoài slide.
- Mỗi câu phải có ĐÚNG 1 đáp án đúng; 3 phương án còn lại phải sai rõ ràng nhưng
  hợp lý (không phải đáp án "bẫy" vô nghĩa như "không có đáp án nào đúng").
- Mỗi câu phải ghi "page" = số trang slide chứa thông tin để trả lời câu đó.
- "explanation" giải thích ngắn (1-2 câu) vì sao đáp án đó đúng, dựa trên slide.
- Viết bằng tiếng Việt.

CHỈ trả về JSON hợp lệ theo đúng schema sau, không kèm markdown, không kèm lời dẫn:
{{
  "questions": [
    {{
      "question": "nội dung câu hỏi",
      "options": ["phương án A", "phương án B", "phương án C", "phương án D"],
      "answer_index": 0,
      "explanation": "vì sao đáp án này đúng",
      "page": 4
    }}
  ]
}}
"""


def _extract_json(raw: str):
    if not raw:
        return None
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*(.+?)\s*```", text, re.S)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except Exception:
            return None
    return None


def _normalize_answer_index(value, options):
    if isinstance(value, str):
        v = value.strip()
        if len(v) == 1 and v.upper() in "ABCD":
            return ord(v.upper()) - ord("A")
        try:
            value = int(v)
        except ValueError:
            return None
    if not isinstance(value, int):
        return None
    if 0 <= value < len(options):
        return value
    if 1 <= value <= len(options):
        return value - 1
    return None


def _validate_quiz(data, valid_pages):
    if not isinstance(data, dict):
        return []
    raw_questions = data.get("questions")
    if not isinstance(raw_questions, list):
        return []

    cleaned = []
    for q in raw_questions:
        if not isinstance(q, dict):
            continue
        text = (q.get("question") or "").strip()
        options = q.get("options")
        if not text or not isinstance(options, list):
            continue
        options = [str(o).strip() for o in options if str(o).strip()]
        if len(options) != QUIZ_NUM_OPTIONS or len(set(options)) != QUIZ_NUM_OPTIONS:
            continue
        idx = _normalize_answer_index(q.get("answer_index"), options)
        if idx is None:
            continue
        page = q.get("page")
        try:
            page = int(page)
        except (TypeError, ValueError):
            page = None
        if page not in valid_pages:
            page = None
        cleaned.append({
            "question": text,
            "options": options,
            "answer_index": idx,
            "explanation": (q.get("explanation") or "").strip(),
            "page": page,
        })
    return cleaned


def _generate_quiz(context_pages, context_label, num_questions):
    if not GEMINI_API_KEY:
        return None, (
            "Chưa cấu hình GEMINI_API_KEY trên server nên mình chưa tạo được quiz. "
            "Vui lòng thiết lập biến môi trường GEMINI_API_KEY rồi thử lại."
        )

    context_block = _format_context_block(context_pages, context_label)
    instruction = QUIZ_INSTRUCTION.format(n=num_questions, k=QUIZ_NUM_OPTIONS)

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL_NAME,
        system_instruction=SYSTEM_PROMPT,
    )

    user_turn = (
        f"NGỮ CẢNH SLIDE (nội dung thật, trích từ file):\n{context_block}\n\n"
        f"{instruction}"
    )

    try:
        response = model.generate_content(
            [{"role": "user", "parts": [user_turn]}],
            generation_config={"response_mime_type": "application/json"},
        )
        raw = (response.text or "").strip()
    except Exception as e:
        log.exception("Lỗi khi gọi Gemini API để tạo quiz")
        return None, f"Xin lỗi, mình gặp lỗi khi tạo quiz ({e}). Bạn thử lại sau ít phút nhé."

    parsed = _extract_json(raw)
    valid_pages = {p["page"] for p in context_pages}
    questions = _validate_quiz(parsed, valid_pages)

    if not questions:
        log.warning("Quiz trả về không dùng được. Raw: %s", raw[:500])
        return None, (
            "Mình chưa tạo được bộ câu hỏi hợp lệ từ nội dung slide này. "
            "Bạn thử lại, hoặc chọn phạm vi trang có nhiều nội dung chữ hơn nhé."
        )

    return questions[:num_questions], None


@app.route("/api/quiz", methods=["POST"])
def api_quiz():
    body = request.get_json(force=True, silent=True) or {}
    file_id = body.get("file_id")
    page = body.get("page")
    page_from = body.get("page_from")
    page_to = body.get("page_to")

    try:
        num_questions = int(body.get("num_questions") or QUIZ_NUM_QUESTIONS)
    except (TypeError, ValueError):
        num_questions = QUIZ_NUM_QUESTIONS
    num_questions = max(1, min(num_questions, 10))

    if not file_id:
        return jsonify({
            "error": "Bạn hãy chọn một tài liệu trong thư viện trước khi tạo quiz nhé.",
        }), 400

    lib = build_library()
    _, f = find_file(lib, file_id)
    if not f:
        return jsonify({
            "error": "Mình không tìm thấy tài liệu này trong thư viện slide hiện có.",
        }), 404

    context_pages, context_label = _gather_context(lib, file_id, page, page_from, page_to)

    if not context_pages:
        return jsonify({
            "error": "Không có nội dung nào trong phạm vi trang đã chọn để tạo quiz.",
        }), 400

    if not any((p.get("text") or "").strip() for p in context_pages):
        return jsonify({
            "error": (
                "Các trang trong phạm vi này không trích được text (có thể là ảnh scan), "
                "nên mình chưa tạo được quiz."
            ),
        }), 400

    questions, error = _generate_quiz(context_pages, context_label, num_questions)
    if error:
        return jsonify({"error": error}), 502

    return jsonify({
        "quiz": {"questions": questions},
        "label": context_label,
        "file_name": f["name"],
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")