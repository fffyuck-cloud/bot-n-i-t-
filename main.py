import os
import ssl
import json
import urllib.request
import random
import re
import unicodedata
from datetime import datetime, date
import discord
from discord.ext import commands
from keep_alive import keep_alive

# --- 🎨 BẢNG MÀU EMBED THEME (ĐEN - HỒNG - ĐỎ) ---
COLOR_BLACK     = 0x111111  # Đen Đậm
COLOR_PINK      = 0xFF69B4  # Hồng Hot Pink
COLOR_DEEP_PINK = 0xFF1493  # Hồng Neon
COLOR_RED       = 0xFF0000  # Đỏ Rực
COLOR_DARK_RED  = 0xD32F2F  # Đỏ Cảnh Báo

# Phân bổ màu chủ đạo cho các chế độ
COLOR_VI_MULTI = COLOR_BLACK      # Đen (Việt Nhiều người)
COLOR_VI_BOT   = COLOR_PINK       # Hồng (Việt 1v1 Bot)
COLOR_EN_MULTI = COLOR_DEEP_PINK  # Hồng Neon (Anh Nhiều người)
COLOR_EN_BOT   = COLOR_RED        # Đỏ (Anh 1v1 Bot)
COLOR_SUCCESS  = COLOR_PINK       # Hồng Thắng
COLOR_ERROR    = COLOR_DARK_RED   # Đỏ Lỗi

# Emoji Phản ứng
CUSTOM_TICK = "Screenshot20260812172055:1537043520790073424"
CUSTOM_CROSS = "Screenshot20260812173722:1537047895310602300"

NUMBER_EMOJIS = {
    1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣",
    6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟"
}

# --- 🛠️ CHUẨN HÓA UNICODE & BỘ LỌC TỪ CẤM ---
def norm(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize('NFC', str(text).lower().strip())
    return re.sub(r'\s+', ' ', text)

BAD_WORDS = {norm("ỉa")}
DEAD_END_WORDS = {
    norm(w) for w in [
        "vậy", "sao", "mà", "thì", "là", "nhé", "à", "nhỉ", "nè", "đâu", "đó",
        "nào", "đấy", "ư", "hử", "nha", "nghen", "ha", "kìa", "này", "chứ", "rồi"
    ]
}

EASY_VI_WORDS = [
    "đá banh", "đá bóng", "bàn học", "học sinh", "sinh viên", "viên bi", "bi ao", "ao cá", "cá chép", 
    "chép phạt", "phạt góc", "học bài", "học tập", "học hành", "bài học", "bài tập", "tập viết", 
    "viết sách", "sách vở", "vở kịch", "kịch bản", "bản đồ", "đồ chơi", "chơi game", "góc sân", 
    "sân trường", "trường học", "góc nhỏ", "phạt đền", "góc nhìn", "thể thao", "bóng đá", "cầu thủ"
]

easy_en_words_set = set([
    "apple", "banana", "cat", "dog", "elephant", "fish", "giraffe", "house",
    "ice", "jungle", "kite", "lemon", "monkey", "nest", "orange", "paper",
    "queen", "rabbit", "sun", "tree", "umbrella", "van", "water", "yellow", "zebra"
])

def contains_bad_word(text):
    text_clean = norm(text)
    words = text_clean.split()
    for word in words:
        if word in BAD_WORDS: return True
    return text_clean in BAD_WORDS

def is_dead_end_word(word):
    word_clean = norm(word)
    syllables = word_clean.split()
    return len(syllables) == 2 and syllables[-1] in DEAD_END_WORDS

# --- 📚 NẠP TỪ ĐIỂN SIÊU FULL (VIỆT + ANH) ---
def prepare_dictionaries():
    ctx = ssl._create_unverified_context()
    
    # 1. Từ điển Tiếng Việt Full (Kết hợp 4 nguồn mở lớn nhất)
    words_vi = set(norm(w) for w in EASY_VI_WORDS)
    urls_vi = [
        "https://raw.githubusercontent.com/vinhjaxt/vietnamese-words/master/vietnamese-words.txt",
        "https://raw.githubusercontent.com/undertheseanlp/nlp/master/underthesea/word_tokenize/dicts/words.txt",
        "https://raw.githubusercontent.com/VietAI/vietnamese-wordlist/master/words.txt",
        "https://raw.githubusercontent.com/duyvuleo/VNcoreNLP/master/words.txt"
    ]
    for url in urls_vi:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
                for line in content.splitlines():
                    word = norm(line.replace("_", " "))
                    if word and len(word.split()) == 2 and not contains_bad_word(word):
                        words_vi.add(word)
        except Exception as e:
            print(f"Lỗi nạp nguồn Tiếng Việt ({url}): {e}")

    # 2. Từ điển Tiếng Anh Full (DWYL 370k + Scrabble Official + Google Common)
    words_en = set()
    urls_en_full = [
        "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt",
        "https://raw.githubusercontent.com/raun/Scrabble/master/words.txt",
        "https://raw.githubusercontent.com/redbo/scrabble/master/dictionary.txt"
    ]
    for url in urls_en_full:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
                for line in content.splitlines():
                    w = line.strip().lower()
                    if len(w) >= 2 and w.isalpha():
                        words_en.add(w)
        except Exception as e:
            print(f"Lỗi nạp nguồn Tiếng Anh ({url}): {e}")

    # Nạp từ thông dụng Tiếng Anh
    try:
        url_common = "https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-no-swears.txt"
        req = urllib.request.Request(url_common, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
            for line in content.splitlines():
                w = line.strip().lower()
                if len(w) >= 2 and w.isalpha():
                    easy_en_words_set.add(w)
                    words_en.add(w)
    except Exception as e:
        print(f"Lỗi nạp từ phổ thông Tiếng Anh: {e}")

    print(f"✅ NẠP THÀNH CÔNG: {len(words_vi):,} từ Tiếng Việt | {len(words_en):,} từ Tiếng Anh.")
    return words_vi, words_en

dictionary_vi, dictionary_en = prepare_dictionaries()
VN_CHARS_REGEX = re.compile(r'^[a-zàáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]+$')

def is_valid_vietnamese_word(text):
    text_clean = norm(text)
    words = text_clean.split()
    return len(words) == 2 and VN_CHARS_REGEX.match(text_clean) and text_clean in dictionary_vi

def is_valid_english_word(text):
    return text.strip().lower() in dictionary_en

def pick_random_vi_word(prefix=None, used_words=None):
    used_words = {norm(w) for w in used_words} if used_words else set()
    prefix_norm = norm(prefix) if prefix else None

    easy = [w for w in EASY_VI_WORDS if (not prefix_norm or norm(w).startswith(prefix_norm + " ")) and norm(w) not in used_words and not is_dead_end_word(w) and not contains_bad_word(w)]
    all_w = [w for w in dictionary_vi if (not prefix_norm or norm(w).startswith(prefix_norm + " ")) and norm(w) not in used_words and not is_dead_end_word(w) and not contains_bad_word(w)]

    if not all_w: return None
    return random.choice(easy) if (random.random() < 0.75 and easy) else random.choice(all_w)

def pick_random_en_word(letter=None, used_words=None):
    used_words = {w.lower() for w in used_words} if used_words else set()
    letter = letter.lower() if letter else None

    easy_candidates = [w for w in easy_en_words_set if (not letter or w.startswith(letter)) and w not in used_words]
    all_candidates = [w for w in dictionary_en if (not letter or w.startswith(letter)) and w not in used_words]

    if not all_candidates: return None
    return random.choice(easy_candidates) if (random.random() < 0.75 and easy_candidates) else random.choice(all_candidates)

# --- DATABASE STATS ---
STATS_FILE = "user_stats.json"

def load_json(file_path, default_data):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f: return json.load(f)
        except Exception: return default_data
    return default_data

def save_json(file_path, data):
    try:
        with open(file_path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e: print(f"Lỗi lưu JSON: {e}")

user_stats = load_json(STATS_FILE, {})

def update_user_stats(user_id, added_words=0, win=False, loss=False):
    u_id = str(user_id)
    if u_id not in user_stats:
        user_stats[u_id] = {"wins": 0, "losses": 0, "total_words": 0}
    user_stats[u_id]["total_words"] += added_words
    if win: user_stats[u_id]["wins"] += 1
    if loss: user_stats[u_id]["losses"] += 1
    save_json(STATS_FILE, user_stats)

def make_progress_bar(val, total=100, length=10):
    if total <= 0: return "░" * length
    percent = min(1.0, max(0.0, val / total))
    filled = int(round(length * percent))
    return "█" * filled + "░" * (length - filled)

def get_user_title(total_words):
    if total_words >= 500: return "👑 Bậc Thầy Ngôn Ngữ"
    if total_words >= 200: return "🔥 Cao Thủ Nối Từ"
    if total_words >= 50: return "✨ Tay Chơi Triển Vọng"
    return "🐣 Tân Thủ Nối Từ"

# --- 🎨 THIẾT KẾ EMBED SIÊU CẤP ĐẸP & TRỰC QUAN ---
def build_game_embed(game, title, color, author_user=None, last_player_name=None):
    embed = discord.Embed(
        title=title,
        color=color,
        timestamp=datetime.now()
    )
    
    if author_user:
        embed.set_author(name=f"🎮 Trận đấu bắt đầu bởi {author_user.display_name}", icon_url=author_user.display_avatar.url)

    # 1. Khung lịch sử chuỗi từ thiết kế Box Codeblock
    used_list = list(game.get("history_list", []))
    recent_list = used_list[-5:]
    history_box = " ➔ ".join([w.upper() for w in recent_list])
    embed.add_field(
        name="📜 DÒNG CHẢY TỪ NỐI (Lịch sử)",
        value=f"```yaml\n{history_box}\n
