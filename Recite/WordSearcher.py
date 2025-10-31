# words.txt         # 全部单词库（每行一个）
# learned_log.txt   # 已学习记录（脚本自动维护）
# review.txt        # 今日学习清单（可放复习内容）

import webbrowser
import random
import time
from urllib.parse import quote_plus
from pathlib import Path
import argparse

DAILY_COUNT = 30  # 每日学习单词数

parser = argparse.ArgumentParser(description="Choose search engine for word lookup", add_help=False)
parser.add_argument("-e", "--engine", choices=["bing", "google"], default="bing",
                    help="Search engine to use (bing or google). Default: bing")
args, _ = parser.parse_known_args()

SEARCH_URLS = {
    "bing": "https://www.bing.com/search?q={}",
    "google": "https://www.google.com/search?q={}"
}
SEARCH_URL = SEARCH_URLS[args.engine]

# 主要延迟和偏移延迟（秒）
MAIN_DELAY = 27.5  # 主要延迟（秒）
OFFSET_DELAY = 7.5  # 偏移/抖动（秒）

# 计算最小/最大延迟并确保非负
MIN_DELAY = max(0.0, MAIN_DELAY - OFFSET_DELAY)
MAX_DELAY = MAIN_DELAY + OFFSET_DELAY

# shared data directory (next to this script)
SHARED_DIR = Path(__file__).resolve().parent / "data"
SHARED_DIR.mkdir(parents=True, exist_ok=True)

words_file = SHARED_DIR / "words.txt"
learned_log_file = SHARED_DIR / "learned_log.txt"
review_file = SHARED_DIR / "review.txt"

def load_word_list(file_path):
    """
    Load a list of words from a text file, one word per line.

    Args:
        file_path (pathlib.Path): The path to the file containing words.

    Returns:
        list[str]: A list of non-empty, stripped words.
    """
    if not file_path.exists():
        return []
    with file_path.open(encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def save_new_words(words):
    """
    Save new words to the learned log and today's review file.

    Args:
        words (list[str]): List of words to save.
    """
    with learned_log_file.open("a", encoding="utf-8") as f:
        for w in words:
            f.write(w + "\n")
    with review_file.open("w", encoding="utf-8") as f:  # 当日复习卡
        for w in words:
            f.write(w + "\n")

def learn_daily():
    all_words = set(load_word_list(words_file))
    learned_words = set(load_word_list(learned_log_file))

    available_words = list(all_words - learned_words)

    if not available_words:
        print("🎉 All words have been learned!")
        return

    count = min(DAILY_COUNT, len(available_words))
    selected = random.sample(available_words, count)

    print("Today's words:", selected)

    for word in selected:
        url = SEARCH_URL.format(quote_plus(word))
        webbrowser.open_new_tab(url)
        print(f"Searching: {word}")

        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        time.sleep(delay)

    save_new_words(selected)
    print(f"📌 Added to learned_log.txt and review.txt")

if __name__ == "__main__":
    learn_daily()