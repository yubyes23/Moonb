#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import time
import random
from pathlib import Path
from urllib.parse import urljoin
import sys

# ====================== 配置区 ======================
base_url = "https://497e.qae.qzz.io"
OUTPUT_DIR = Path("test")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": base_url
}

def fetch_details(url):
    """进入子网页抓取 m3u8"""
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')
        
        m3u8 = "None"
        source = soup.select_one('source#mp4m3u8')
        if source and source.get('src'):
            m3u8 = source['src']
        else:
            img_tag = soup.select_one('img#video_img')
            if img_tag and 'm3u8' in img_tag.get('src', '').lower():
                m3u8 = img_tag['src']
        return m3u8
    except:
        return "None"

def scrape_page(page_num):
    """处理指定页码，不设终止 URL 检查"""
    url = f"{base_url}/?type=ry&p={page_num}"
    print(f"::group::正在处理第 {page_num} 页")
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        items = soup.select('.stui-vodlist__thumb.lazyload')
        if not items:
            print(f"⚠️ 第 {page_num} 页没有发现视频内容，可能已到末尾。")
            return "EMPTY"

        page_data = []
        for a_tag in items:
            raw_href = a_tag.get('href', '')
            full_url = urljoin(base_url, raw_href)
            
            # 提取标题和图片
            parent_node = a_tag.find_parent('li') or a_tag.find_parent('div')
            detail_a = parent_node.select_one('.stui-vodlist__detail .title a')
            video_title = (detail_a.get('title') or detail_a.get_text() if detail_a else a_tag.get('title') or "未知标题").strip()
            image_url = a_tag.get('data-original') or a_tag.get('src')

            print(f"  🎬 发现视频: {video_title}")
            m3u8_link = fetch_details(full_url)

            page_data.append({
                "url": full_url,
                "m3u8": m3u8_link,
                "title": video_title,
                "image_url": image_url
            })
            time.sleep(random.uniform(0.3, 0.6))

        if page_data:
            file_path = OUTPUT_DIR / f"hsck_page_{page_num}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(page_data, f, ensure_ascii=False, indent=2)
            print(f"💾 已保存 {len(page_data)} 条数据至 {file_path}")

        print("::endgroup::")
        return "SUCCESS"
    except Exception as e:
        print(f"❌ 页面 {page_num} 处理出错: {e}")
        return "ERROR"

if __name__ == "__main__":
    # 从命令行获取起始和结束页码
    # 运行方式: python range_scraper.py 1 10
    if len(sys.argv) >= 3:
        start = int(sys.argv[1])
        end = int(sys.argv[2])
    else:
        start = 1
        end = 1

    print(f"🚀 开始任务: 从第 {start} 页到第 {end} 页")
    for p in range(start, end + 1):
        status = scrape_page(p)
        # 这里可以发送 RESULT 给 Action 触发 Push
        print(f"PAGE_STATUS_{p}={status}")
