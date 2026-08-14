import os
import ssl
import urllib.request
import random
import re
import unicodedata
from datetime import datetime
import discord
from discord.ext import commands
from keep_alive import keep_alive

# --- 🎨 CẤU HÌNH GIAO DIỆN ---
COLOR_THEME = 0xFF1493 # Hồng Cyberpunk

# Custom Emoji của bạn
EMOJI_TICK = "<:Screenshot20260812172055:1537043520790073424>"
EMOJI_CROSS = "<:Screenshot20260812173722:1537047895310602300>"

def norm(text: str) -> str:
    if not text: return ""
    text = unicodedata.normalize('NFC', str(text).lower().strip())
    return re.sub(r'\s+', ' ', text)

FALLBACK_VI_WORDS = [
    "đá banh", "đá bóng", "bàn học", "học sinh", "sinh viên", "viên bi", "bi ao",
    "ao cá", "cá chép", "chép phạt", "phạt góc", "học bài", "thể thao", "bóng đá",
    "ao làng", "làng quê", "quê hương", "hương thơm", "thơm ngon", "ngon ngọt",
    "ngon lành", "lành lặn", "lặn lội", "lội nước", "nước trong", "trong xanh"
]

# --- 📚 TẢI TỪ ĐIỂN ---
def prepare_dictionaries():
    ctx = ssl._create_unverified_context()
    words_vi = set(norm(w) for w in FALLBACK_VI_WORDS)
    
    for attempt in range(3):
        try:
            req = urllib.request.Request("https://raw.githubusercontent.com/NguyenAnhTuan1997/Vietnamese-Dictionary/master/words.txt", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
                for line in response.read().decode('utf-8', errors='ignore').splitlines():
                    word = norm(line.replace("_", " "))
                    if word and len(word.split()) == 2: 
                        words_vi.add(word)
            print(f"✅ Đã nạp {len(words_vi):,} từ Tiếng Việt thành công!")
            break 
        except Exception as e:
            print(f"⚠️ Lần {attempt + 1} tải từ điển TV bị lỗi mạng: {e}")

    words_en = set()
    for attempt in range(2):
        try:
            req = urllib.request.Request("https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
                for line in response.read().decode('utf-8', errors='ignore').splitlines():
                    w = line.strip().lower()
                    if len(w) >= 2 and w.isalpha(): 
                        words_en.add(w)
            print(f"✅ Đã nạp {len(words_en):,} từ Tiếng Anh thành công!")
            break
        except Exception as e:
            print(f"⚠️ Lỗi tải từ điển Anh lần {attempt + 1}: {e}")
            
    return words_vi, words_en

dictionary_vi, dictionary_en = prepare_dictionaries()
VN_CHARS_REGEX = re.compile(r'^[a-zàáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]+$')

def is_valid_vietnamese_word(text):
    text_clean = norm(text)
    return len(text_clean.split()) == 2 and bool(VN_CHARS_REGEX.match(text_clean))

def is_valid_english_word(text):
    return text.strip().lower() in dictionary_en

def pick_random_vi_word(prefix=None, used_words=None):
    used_words = {norm(w) for w in used_words} if used_words else set()
    prefix_norm = norm(prefix) if prefix else None
    all_w = [w for w in dictionary_vi if (not prefix_norm or norm(w).startswith(prefix_norm + " ")) and norm(w) not in used_words]
    return random.choice(all_w) if all_w else None

def pick_random_en_word(letter=None, used_words=None):
    used_words = {w.lower() for w in used_words} if used_words else set()
    letter = letter.lower() if letter else None
    all_candidates = [w for w in dictionary_en if (not letter or w.startswith(letter)) and w not in used_words]
    return random.choice(all_candidates) if all_candidates else None

# --- 💎 HÀM TẠO EMBEDS ---
def build_game_embeds(game, title, last_player_name=None):
    embed = discord.Embed(color=COLOR_THEME, timestamp=datetime.now())
    embed.set_author(name=f"❖ {title} ❖", icon_url="https://cdn-icons-png.flaticon.com/512/8066/8066804.png")
    
    used_list = list(game.get("history_list", []))
    history_str = " ➔ ".join([w.upper() for w in used_list[-5:]])
    history_box = "```fix\n" + history_str + "\n
