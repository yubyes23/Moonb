#!/usr/bin/env python3
import json
import logging
from pathlib import Path
from datetime import datetime

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# 输入输出目录
BASE_DIR = Path(__file__).parent.parent / "test"
OUTPUT_DIR = BASE_DIR
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def convert_file(input_file: Path):
    """转换单个 hsck4_page_x.json 文件为统一格式"""
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [
            {
                "address": item["m3u8"],
                "img": item["image_url"],
                "title": item["title"],
            }
            for item in data
            if "m3u8" in item and "title" in item and "image_url" in item
        ]

    except Exception as e:
        logging.error(f"转换 {input_file} 失败: {e}")
        return []

def merge_files():
    """合并所有 hsck4_page_x.json，每100个合并为 Q100、Q200，其余生成 n003"""
    all_files = sorted(BASE_DIR.glob("hsck4_page_*.json"),
                       key=lambda p: int(p.stem.split("_")[-1]))

    if not all_files:
        logging.warning("未找到任何 hsck4_page_x.json 文件")
        return

    merged = []
    seen = set()   # 用于去重
    batch_num = 1
    file_count = 0
    total_raw = 0
    total_unique = 0

    for idx, file in enumerate(all_files, 1):
        logging.info(f"处理文件 {idx}/{len(all_files)}: {file.name}")
        items = convert_file(file)
        total_raw += len(items)

        # 去重
        new_items = []
        for item in items:
            if item["address"] not in seen:
                seen.add(item["address"])
                new_items.append(item)

        merged.extend(new_items)
        total_unique += len(new_items)
        file_count += 1

        # 每 100 个文件合并一次
        if file_count == 100:
            out_name = f"Q{batch_num * 100}.json"
            out_path = OUTPUT_DIR / out_name
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump({"zhubo": merged, "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                          f, ensure_ascii=False, indent=2)
            logging.info(f"✅ 已生成 {out_name} (共 {len(merged)} 条，去重后)")
            
            # 重置
            merged = []
            file_count = 0
            batch_num += 1

    # 剩余的生成 Q000.json
    if merged:
        out_path = OUTPUT_DIR / "Q000.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({"zhubo": merged, "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                      f, ensure_ascii=False, indent=2)
        logging.info(f"✅ 已生成 Q000.json (共 {len(merged)} 条，去重后)")

    logging.info(f"任务完成：原始 {total_raw} 条，去重后 {total_unique} 条")

if __name__ == "__main__":
    merge_files()
