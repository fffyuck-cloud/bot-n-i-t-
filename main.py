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

# --- 🎨 BẢNG MÀU THEME (VIP EDITION) ---
COLOR_BLACK     = 0x2B2D31 # Màu nền xám đen chuẩn Discord UI
COLOR_PINK      = 0xFF69B4 # Hồng cánh sen
COLOR_DEEP_PINK = 0xFF1493 # Hồng đậm
COLOR_RED       = 0xFF4747 # Đỏ pastel
COLOR_SUCCESS   = 0x57F287 # Xanh lá chuẩn Discord
COLOR_ERROR     = 0xED4245 # Đỏ lỗi chuẩn Discord

# --- THIẾT LẬP EMOJI & RÀNG BUỘC ---
NUMBER_EMOJIS = {
    1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣",
    6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟"
}

def norm(text: str) -> str:
    if not text: return ""
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
    for word in text_clean.split():
        if word in BAD_WORDS: return True
    return text_clean in BAD_WORDS

def is_dead_end_word(word):
    word_clean = norm(word)
    syllables = word_clean.split()
    return len(syllables) == 2 and syllables[-1] in DEAD_END_WORDS

# --- 📚 NẠP TỪ ĐIỂN ---
def prepare_dictionaries():
    ctx = ssl._create_unverified_context()
    words_vi = set(norm(w) for w in EASY_VI_WORDS)
    urls_vi = [
        "https://raw.githubusercontent.com/duyvuleo/VNcoreNLP/master/words.txt",
        "https://raw.githubusercontent.com/NguyenAnhTuan1997/Vietnamese-Dictionary/master/words.txt"
    ]
    for url in urls_vi:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                for line in response.read().decode('utf-8', errors='ignore').splitlines():
                    word = norm(line.replace("_", " "))
                    if word and len(word.split()) == 2 and not contains_bad_word(word):
                        words_vi.add(word)
        except: pass

    words_en = set()
    try:
        url_en = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
        req = urllib.request.Request(url_en, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            for line in response.read().decode('utf-8', errors='ignore').splitlines():
                w = line.strip().lower()
                if len(w) >= 2 and w.isalpha(): words_en.add(w)
    except: pass

    print(f"✅ NẠP DATA: {len(words_vi):,} từ VN | {len(words_en):,} từ EN.")
    return words_vi, words_en

dictionary_vi, dictionary_en = prepare_dictionaries()
VN_CHARS_REGEX = re.compile(r'^[a-zàáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]+$')

def is_valid_vietnamese_word(text):
    text_clean = norm(text)
    return len(text_clean.split()) == 2 and VN_CHARS_REGEX.match(text_clean) and text_clean in dictionary_vi

def is_valid_english_word(text):
    return text.strip().lower() in dictionary_en

def pick_random_vi_word(prefix=None, used_words=None):
    used_words = {norm(w) for w in used_words} if used_words else set()
    prefix_norm = norm(prefix) if prefix else None
    all_w = [w for w in dictionary_vi if (not prefix_norm or norm(w).startswith(prefix_norm + " ")) and norm(w) not in used_words and not is_dead_end_word(w)]
    return random.choice(all_w) if all_w else None

def pick_random_en_word(letter=None, used_words=None):
    used_words = {w.lower() for w in used_words} if used_words else set()
    letter = letter.lower() if letter else None
    all_candidates = [w for w in dictionary_en if (not letter or w.startswith(letter)) and w not in used_words]
    return random.choice(all_candidates) if all_candidates else None

# --- 💾 DATABASE STATS ---
STATS_FILE = "user_stats.json"

def load_json():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

user_stats = load_json()

def save_json():
    with open(STATS_FILE, "w", encoding="utf-8") as f: json.dump(user_stats, f, ensure_ascii=False, indent=4)

def update_user_stats(user_id, added_words=0, win=False, loss=False):
    u_id = str(user_id)
    if u_id not in user_stats: user_stats[u_id] = {"wins": 0, "losses": 0, "total_words": 0}
    user_stats[u_id]["total_words"] += added_words
    if win: user_stats[u_id]["wins"] += 1
    if loss: user_stats[u_id]["losses"] += 1
    save_json()

def make_progress_bar(val, total=100, length=10):
    if total <= 0: return "⬜" * length
    percent = min(1.0, max(0.0, val / total))
    filled = int(round(length * percent))
    return "🟩" * filled + "⬜" * (length - filled)

def get_user_title(total_words):
    if total_words >= 1000: return "🌟 CHÚA TỂ NGÔN TỪ"
    if total_words >= 500: return "👑 BẬC THẦY GIAO TIẾP"
    if total_words >= 200: return "🔥 CAO THỦ NỐI TỪ"
    if total_words >= 50: return "✨ TAY CHƠI TRIỂN VỌNG"
    return "🐣 TÂN THỦ NHẬP MÔN"

# --- 🎨 EMBED BUILDER (BẢN ĐẸP) ---
def build_game_embed(game, title, color, author_user=None, last_player_name=None):
    embed = discord.Embed(color=color, timestamp=datetime.now())
    embed.set_author(name=f"🎮 {title}", icon_url="https://cdn-icons-png.flaticon.com/512/1374/1374128.png")
    
    used_list = list(game.get("history_list", []))
    recent_list = used_list[-5:]
    history_str = " ➔ ".join([w.upper() for w in recent_list])
    
    # Định dạng Markdown siêu đẹp
    embed.add_field(
        name="📜 **Chuỗi Từ Gần Đây**",
        value=f"```yaml\n{history_str}\n
