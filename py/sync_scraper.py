#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
import urllib.parse

# 配置
BASE_DIR = Path(__file__).parent.parent
TARGET_DIR = BASE_DIR / "test"
INDEX_FILE = TARGET_DIR / "hsck.json"
BASE_URL = "https://2bfc.yuba.cloudns.be"
PAGE_SIZE = 40
START_PAGE_NUM = 1 
COMPARE_LIMIT = 80 

HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": BASE_URL}

def fetch_detail(url, img):
    """抓取详情页 m3u8"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        m3u8 = ""
        src = soup.select_one("img#video_img, source#mp4m3u8")
        if src: m3u8 = src.get("src", "")
        title_elem = soup.find("title")
        title = title_elem.text.strip().replace(" - 黄色仓库 - hsck123.com", "") if title_elem else "未知"
        return {"url": url, "m3u8": m3u8, "title": title, "image_url": img}
    except: return None

def fetch_web_latest():
    """抓取网页首页最新内容"""
    url = f"{BASE_URL}/?type=qp&p=1"
    results = []
    print(f"🌐 访问首页: {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.select('a[href*="/view/?id="][data-original]')
        
        print(f"🎬 发现 {len(links)} 个条目，开始解析...")
        for link in links:
            href = urllib.parse.urljoin(BASE_URL, link["href"])
            img = link.get("data-original", "")
            detail = fetch_detail(href, img)
            if detail: 
                results.append(detail)
                print(f"  ✅ 抓取: {detail['title'][:15]}...")
            time.sleep(0.3)
        return results
    except Exception as e:
        print(f"❌ 抓取首页失败: {e}")
        return []

def sync():
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 抓取
    new_items = fetch_web_latest()
    if not new_items: return

    # 2. 读取旧数据
    history_data = []
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            try:
                history_data = json.load(f)
            except: history_data = []

    # 3. 比对前 80 条去重
    recent_urls = {item['url'] for item in history_data[:COMPARE_LIMIT]}
    truly_new = []
    for it in new_items:
        if it['url'] not in recent_urls:
            truly_new.append(it)
        else: break
    
    if not truly_new and history_data:
        print("✅ 已经是最新，无需挤压更新。")
        return

    print(f"🔥 发现 {len(truly_new)} 条新内容，执行挤压重排...")
    total_data = truly_new + history_data

    # 4. 重新保存分页文件 (文件名: hsck_page_*.json)
    for i in range(0, len(total_data), PAGE_SIZE):
        page_idx = START_PAGE_NUM + (i // PAGE_SIZE)
        chunk = total_data[i : i + PAGE_SIZE]
        # ⭐ 这里修正了文件名格式
        file_path = TARGET_DIR / f"hsck_page_{page_idx}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(chunk, f, ensure_ascii=False, indent=2)
            
    print(f"✨ 同步完成！当前总条数: {len(total_data)}")

if __name__ == "__main__":
    sync()
