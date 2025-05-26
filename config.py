# config.py

import os
import datetime

# --- SeaTable API 配置 ---
SERVER_URL = 'https://table.nju.edu.cn'
# API_TOKEN = os.getenv('SEATABLE_API_TOKEN', 'YOUR_DEFAULT_API_TOKEN')
API_TOKEN = '895abfe18ac0f35568788a864515782011c160fc'
BASE_NAME = '讲座信息收集'
TABLE_NAME = '春季学期讲座信息收集'

# --- 筛选时间范围 ---
START_DATE_STR = '2025-05-24'
END_DATE_STR = '2025-05-31'

# --- 输出文件配置 ---
OUTPUT_WORD_FILENAME = f'讲座信息_{START_DATE_STR}_至_{END_DATE_STR}.docx'
OUTPUT_MARKDOWN_FILENAME = f'讲座信息_{START_DATE_STR}_至_{END_DATE_STR}.md'
OUTPUT_CSV_FILENAME = f'讲座信息_{START_DATE_STR}_至_{END_DATE_STR}.csv' # 确保这行存在！
TEMP_IMAGE_DIR = 'temp_lecture_images'

# --- 其他配置 ---
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    'Referer': SERVER_URL
}
IMAGE_DOWNLOAD_TIMEOUT = 15
