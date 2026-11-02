#!/usr/bin/env python3
import json
from pathlib import Path

# 配置：定位到仓库根目录下的 test 文件夹
BASE_DIR = Path(__file__).parent.parent
TARGET_DIR = BASE_DIR / "test"
INDEX_FILE = TARGET_DIR / "hsck.json"

def aggregate():
    # 自动创建目录
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    
    all_data = []
    # 匹配文件名格式: hsck_page_*.json (去掉之前的数字4)
    files = sorted(TARGET_DIR.glob("hsck_page_*.json"), 
                   key=lambda x: int(x.stem.split('_')[-1]))
    
    print(f"📦 扫描目录: {TARGET_DIR.absolute()}")
    print(f"📦 发现 {len(files)} 个分页文件")

    for f_path in files:
        with open(f_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    all_data.extend(data)
            except Exception as e:
                print(f"❌ 读取 {f_path.name} 出错: {e}")

    # 生成全量索引
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 汇总完成！共 {len(all_data)} 条数据 -> {INDEX_FILE.name}")

if __name__ == "__main__":
    aggregate()
