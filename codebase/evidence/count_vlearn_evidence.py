"""Đếm bằng chứng cho Vấn đề 3 — Ý định "tóm tắt slide này" gần như không được phục vụ.

Giả thuyết cần kiểm chứng:
  1. "tóm tắt" là một ý định phổ biến của học viên (đếm số lượt hỏi).
  2. Tutor thường trả lời not-found / từ chối truy cập PDF cho nhóm lượt hỏi này.
  3. Nhóm lượt hỏi này có tỉ lệ citations = [] cao hơn hẳn mức nền.

Cấu trúc dữ liệu: mỗi turn_id gồm đúng 2 dòng (student + tutor), nên có thể
join thẳng câu hỏi của học viên sang câu trả lời của tutor theo turn_id.
"""

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

PATH = Path('data/vlearn-pack/chatlog/chat_history_anonymized_for_hackathon.csv')

# --- Bộ pattern ------------------------------------------------------------

# Ý định tóm tắt: metric chính bám đúng từ khoá "tóm tắt" như phát biểu vấn đề.
SUMMARY_CORE = [r'tóm tắt', r'tom tat']
# Biến thể mở rộng — dùng để kiểm tra xem con số lõi có bỏ sót ý định không.
SUMMARY_WIDE = SUMMARY_CORE + [
    r'tổng kết', r'tong ket', r'khái quát', r'khai quat',
    r'ý chính', r'y chinh', r'nội dung chính', r'noi dung chinh',
    r'summar', r'\btl;?dr\b', r'overview',
]

# Tutor trả lời "không tìm thấy" nội dung.
NOT_FOUND = [
    r'không tìm thấy', r'khong tim thay', r'không tìm được', r'khong tim duoc',
    r'không có nội dung', r'khong co noi dung', r'không thấy nội dung',
    r'không tìm ra', r'chưa có thông tin', r'chua co thong tin',
    r'không có thông tin', r'khong co thong tin',
    r"couldn't find", r"can't find", r'could not find', r'not found',
]

# Tutor từ chối vì không mở/truy cập được tài liệu.
NO_ACCESS = [
    r'không thể truy cập', r'khong the truy cap', r'không truy cập được',
    r'không thể mở', r'khong the mo', r'không thể đọc', r'khong the doc',
    r'không có quyền truy cập', r'không được cung cấp',
    r'không thể xem', r'khong the xem',
    r"can'?t access", r'cannot access', r'unable to access',
]

# Học viên nêu phạm vi cụ thể (trang / slide / đoạn bôi đen).
SCOPE_EXPLICIT = [
    r'trang\s*\d+', r'page\s*\d+', r'slide\s*\d+', r'\bp\.?\s*\d+\b',
    r'đoạn được chọn', r'doan duoc chon', r'đoạn bôi đen', r'doan boi den',
    r'highlighted',
]
# Học viên nêu phạm vi mơ hồ (cả buổi / cả slide / hôm nay).
SCOPE_VAGUE = [
    r'buổi (học|hôm nay|này)', r'buoi (hoc|hom nay|nay)',
    r'hôm nay', r'hom nay', r'cả bài', r'ca bai', r'toàn bộ', r'toan bo',
    r'cả slide', r'ca slide', r'bài giảng', r'bai giang',
]
# Nhắc tới tài liệu PDF/slide nói chung.
MENTIONS_DOC = [r'slide', r'\bpdf\b', r'tài liệu', r'tai lieu', r'bài giảng', r'bai giang']


def hit(text, regexes):
    t = (text or '').lower()
    return any(re.search(rgx, t) for rgx in regexes)


def pct(part, whole):
    return f'{100 * part / whole:.1f}%' if whole else 'n/a'


# --- Nạp dữ liệu và join theo turn_id --------------------------------------

with PATH.open('r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

turns = defaultdict(dict)
for row in rows:
    turns[row['turn_id']][row['role']] = row

# Chỉ giữ turn đủ cặp student + tutor.
pairs = [(tid, t['student'], t['tutor'])
         for tid, t in turns.items() if 'student' in t and 'tutor' in t]

print('=== Quy mô dữ liệu ===')
print('rows:', len(rows))
print('turns (đủ cặp student+tutor):', len(pairs), '/', len(turns))

# --- Mức nền (baseline) toàn bộ hội thoại ----------------------------------

n_all = len(pairs)
base_empty_cit = sum(1 for _, _, tu in pairs if tu['citations'].strip() == '[]')
base_not_found = sum(1 for _, _, tu in pairs if hit(tu['content'], NOT_FOUND))
base_no_access = sum(1 for _, _, tu in pairs if hit(tu['content'], NO_ACCESS))
base_fail = sum(1 for _, _, tu in pairs if hit(tu['content'], NOT_FOUND + NO_ACCESS))
base_down = sum(1 for _, _, tu in pairs if tu['rating'] == 'down')

print('\n=== Mức nền toàn bộ (n = %d turn) ===' % n_all)
print(f'citations = []           : {base_empty_cit:4d}  ({pct(base_empty_cit, n_all)})')
print(f'tutor trả lời not-found  : {base_not_found:4d}  ({pct(base_not_found, n_all)})')
print(f'tutor từ chối truy cập   : {base_no_access:4d}  ({pct(base_no_access, n_all)})')
print(f'not-found HOẶC từ chối   : {base_fail:4d}  ({pct(base_fail, n_all)})')
print(f'rating = down            : {base_down:4d}  ({pct(base_down, n_all)})')

# --- Nhóm ý định "tóm tắt" -------------------------------------------------

summary_core = [p for p in pairs if hit(p[1]['content'], SUMMARY_CORE)]
summary_wide = [p for p in pairs if hit(p[1]['content'], SUMMARY_WIDE)]

n = len(summary_core)
print('\n=== Ý định tóm tắt (student hỏi) ===')
print(f'chứa "tóm tắt"                    : {n:4d}  ({pct(n, n_all)} tổng số turn)')
print(f'mở rộng (tổng kết/ý chính/summar) : {len(summary_wide):4d}  ({pct(len(summary_wide), n_all)})')

s_empty_cit = sum(1 for _, _, tu in summary_core if tu['citations'].strip() == '[]')
s_not_found = sum(1 for _, _, tu in summary_core if hit(tu['content'], NOT_FOUND))
s_no_access = sum(1 for _, _, tu in summary_core if hit(tu['content'], NO_ACCESS))
s_fail = sum(1 for _, _, tu in summary_core if hit(tu['content'], NOT_FOUND + NO_ACCESS))
s_down = sum(1 for _, _, tu in summary_core if tu['rating'] == 'down')
s_up = sum(1 for _, _, tu in summary_core if tu['rating'] == 'up')

print('\n=== Tutor phục vụ ý định này ra sao (n = %d) ===' % n)
print(f'citations = []           : {s_empty_cit:4d}  ({pct(s_empty_cit, n)})   [nền {pct(base_empty_cit, n_all)}]')
print(f'trả lời not-found        : {s_not_found:4d}  ({pct(s_not_found, n)})   [nền {pct(base_not_found, n_all)}]')
print(f'từ chối truy cập tài liệu: {s_no_access:4d}  ({pct(s_no_access, n)})   [nền {pct(base_no_access, n_all)}]')
print(f'not-found HOẶC từ chối   : {s_fail:4d}  ({pct(s_fail, n)})   [nền {pct(base_fail, n_all)}]')
print(f'rating = down            : {s_down:4d}  ({pct(s_down, n)})   [nền {pct(base_down, n_all)}]')
print(f'rating = up              : {s_up:4d}  ({pct(s_up, n)})')

# --- Phạm vi học viên nêu ra ------------------------------------------------

sc_explicit = [p for p in summary_core if hit(p[1]['content'], SCOPE_EXPLICIT)]
sc_vague = [p for p in summary_core if not hit(p[1]['content'], SCOPE_EXPLICIT)
            and hit(p[1]['content'], SCOPE_VAGUE)]
sc_none = [p for p in summary_core if not hit(p[1]['content'], SCOPE_EXPLICIT)
           and not hit(p[1]['content'], SCOPE_VAGUE)]
sc_doc = [p for p in summary_core if hit(p[1]['content'], MENTIONS_DOC)]

print('\n=== Phạm vi học viên nêu trong câu hỏi tóm tắt ===')
for label, group in (('phạm vi rõ (trang/slide N/đoạn chọn)', sc_explicit),
                     ('phạm vi mơ hồ (buổi/hôm nay/toàn bộ)', sc_vague),
                     ('không nêu phạm vi', sc_none),
                     ('có nhắc slide/pdf/tài liệu', sc_doc)):
    fail = sum(1 for _, _, tu in group if hit(tu['content'], NOT_FOUND + NO_ACCESS))
    print(f'{label:38s}: {len(group):4d}  → thất bại {fail:3d} ({pct(fail, len(group))})')

# --- Phân bố theo ngày / hội thoại ------------------------------------------

print('\n=== Phân bố lượt hỏi tóm tắt ===')
print('số học viên khác nhau  :', len({st["user_id"] for _, st, _ in summary_core}))
print('số hội thoại khác nhau :', len({st["conversation_id"] for _, st, _ in summary_core}))
print('top day_code:', Counter(st['day_code'] for _, st, _ in summary_core).most_common(5))

# --- Ví dụ trích dẫn --------------------------------------------------------

def show(tid, st, tu, width=200):
    q = ' '.join(st['content'].split())
    a = ' '.join(tu['content'].split())
    tag = f"rating={tu['rating'] or '-'} citations={tu['citations'] or '-'} move={tu['move_used'] or '-'}"
    print(f'\n[{tid}] {tag}')
    print(f'  HV : {q[:width]}')
    print(f'  AI : {a[:width]}')


print('\n=== Ví dụ: hỏi tóm tắt → tutor không phục vụ được ===')
failed = [p for p in summary_core if hit(p[2]['content'], NOT_FOUND + NO_ACCESS)]
# Ưu tiên các turn bị rating down (bằng chứng mạnh nhất).
failed.sort(key=lambda p: (p[2]['rating'] != 'down', p[0]))
for tid, st, tu in failed[:8]:
    show(tid, st, tu)

print('\n=== Ví dụ đối chứng: hỏi tóm tắt CÓ trích dẫn trang ===')
good = [p for p in summary_core
        if p[2]['citations'].strip() not in ('', '[]')
        and not hit(p[2]['content'], NOT_FOUND + NO_ACCESS)]
for tid, st, tu in good[:3]:
    show(tid, st, tu)

# --- Kiểm chứng ví dụ nêu trong phát biểu vấn đề ----------------------------

print('\n=== Kiểm chứng turn được nêu đích danh ===')
for tid in ('T0519',):
    t = turns.get(tid)
    if not t or 'student' not in t or 'tutor' not in t:
        print(f'{tid}: KHÔNG có trong dữ liệu')
        continue
    show(tid, t['student'], t['tutor'], width=300)
