"""
slide_index.py
----------------
Quét thư mục data/vlearn-pack/slides, đọc NỘI DUNG THẬT của từng file
.pdf theo từng trang, và dựng một "library" JSON mà frontend (index.html)
và endpoint /api/chat dùng chung.

Không có dữ liệu giả trong file này — mọi text hiển thị hoặc dùng làm
ngữ cảnh cho Gemini đều được trích trực tiếp từ file thật trên đĩa.
Nếu thư mục rỗng hoặc file không đọc được, mục đó sẽ báo lỗi rõ ràng
thay vì bịa nội dung.
"""

import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime

APP_ROOT = Path(__file__).resolve().parents[2]


def _resolve_path(value: str, default: Path) -> Path:
    p = Path(value)
    return p if p.is_absolute() else APP_ROOT / p


SLIDES_ROOT = _resolve_path(os.environ.get("VLEARN_SLIDES_DIR", "data/vlearn-pack/slides"), APP_ROOT / "data" / "vlearn-pack" / "slides")
CACHE_PATH = _resolve_path(os.environ.get("VLEARN_INDEX_CACHE", "data/vlearn-pack/.index_cache.json"), APP_ROOT / "data" / "vlearn-pack" / ".index_cache.json")


def _file_id(path: Path) -> str:
    return hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:12]


def _clean_text(t: str) -> str:
    t = re.sub(r"[ \t]+", " ", t or "")
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()

def _extract_pdf(path: Path):
    """Trả về list[str], mỗi phần tử là text thật của 1 trang PDF."""
    try:
        import pdfplumber
        pages = []
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                pages.append(_clean_text(page.extract_text() or ""))
        return pages
    except ImportError:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        return [_clean_text(p.extract_text() or "") for p in reader.pages]


def _extract_file(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(path)
    return None  # loại file không hỗ trợ -> bỏ qua, không bịa nội dung


def _title_for_page(text: str, fallback: str) -> str:
    """Lấy dòng đầu tiên có nội dung làm tiêu đề hiển thị — vẫn là text thật từ slide."""
    if not text:
        return fallback
    first_line = next((l for l in text.split("\n") if l.strip()), fallback)
    return first_line[:120]


def _bullets_for_page(text: str, max_bullets: int = 5):
    """Tách các dòng có nội dung thành gạch đầu dòng thật (không tự sinh thêm ý)."""
    if not text:
        return []
    lines = [l.strip("•-–* \t") for l in text.split("\n") if l.strip()]
    return lines[1:1 + max_bullets] if len(lines) > 1 else lines[:max_bullets]


def build_library(force: bool = False) -> dict:
    """
    Quét toàn bộ data/vlearn-pack/slides (tổ chức theo thư mục con = "buổi học",
    ví dụ slides/Day01/, slides/Day02/...), đọc nội dung thật, trả về cấu trúc:

    {
      "generated_at": "...",
      "root": "data/vlearn-pack/slides",
      "days": [
        {
          "id": "day01", "name": "Day01", "files": [
            {
              "id": "<hash>", "name": "day01_302.pdf", "path": "...",
              "page_count": N,
              "pages": [ {"page": 1, "title": "...", "text": "...", "bullets": [...]} , ... ]
            }
          ]
        }
      ],
      "errors": [ "<file>: <lý do không đọc được>", ... ]
    }
    """
    if not force and CACHE_PATH.exists():
        try:
            cached = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
            src_mtime = _dir_mtime(SLIDES_ROOT)
            if cached.get("_source_mtime") == src_mtime:
                return cached
        except Exception:
            pass

    days = []
    errors = []

    if not SLIDES_ROOT.exists():
        errors.append(
            f"Không tìm thấy thư mục {SLIDES_ROOT}. Hãy đặt slide thật vào "
            f"data/vlearn-pack/slides/<TênBuổi>/<file>.pdf"
        )
        result = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "root": str(SLIDES_ROOT),
            "days": [],
            "errors": errors,
            "_source_mtime": None,
        }
        return result

    day_dirs = sorted([d for d in SLIDES_ROOT.iterdir() if d.is_dir()])
    # Nếu không có thư mục con theo buổi, coi cả SLIDES_ROOT là 1 "buổi"
    if not day_dirs:
        day_dirs = [SLIDES_ROOT]

    for day_dir in day_dirs:
        files_entries = []
        source_files = sorted(
            [f for f in day_dir.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]
        )
        for f in source_files:
            try:
                raw_pages = _extract_file(f)
                if raw_pages is None:
                    continue
                if all(not p.strip() for p in raw_pages):
                    errors.append(f"{f}: đọc được file nhưng không trích được text (có thể là ảnh scan).")
                pages = []
                for i, text in enumerate(raw_pages, start=1):
                    pages.append({
                        "page": i,
                        "title": _title_for_page(text, f"Trang {i}"),
                        "text": text,
                        "bullets": _bullets_for_page(text),
                    })
                files_entries.append({
                    "id": _file_id(f),
                    "name": f.name,
                    "path": str(f),
                    "page_count": len(pages),
                    "pages": pages,
                })
            except Exception as e:
                errors.append(f"{f}: lỗi khi đọc file thật ({e})")

        if files_entries:
            days.append({
                "id": re.sub(r"[^a-z0-9]+", "-", day_dir.name.lower()).strip("-") or "root",
                "name": day_dir.name if day_dir != SLIDES_ROOT else "Tất cả slide",
                "files": files_entries,
            })

    if not days:
        errors.append(
            f"Không tìm thấy file .pdf nào trong {SLIDES_ROOT}. "
            f"Thư viện sẽ trống cho đến khi có slide thật."
        )

    result = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "root": str(SLIDES_ROOT),
        "days": days,
        "errors": errors,
        "_source_mtime": _dir_mtime(SLIDES_ROOT),
    }

    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    return result


def _dir_mtime(root: Path):
    if not root.exists():
        return None
    latest = 0.0
    for p in root.rglob("*"):
        if p.is_file():
            latest = max(latest, p.stat().st_mtime)
    return latest


def find_file(library: dict, file_id: str):
    for day in library.get("days", []):
        for f in day.get("files", []):
            if f["id"] == file_id:
                return day, f
    return None, None


def get_page(library: dict, file_id: str, page: int):
    _, f = find_file(library, file_id)
    if not f:
        return None
    for p in f["pages"]:
        if p["page"] == page:
            return p
    return None


def get_page_range(library: dict, file_id: str, page_from: int, page_to: int):
    _, f = find_file(library, file_id)
    if not f:
        return []
    lo, hi = min(page_from, page_to), max(page_from, page_to)
    return [p for p in f["pages"] if lo <= p["page"] <= hi]