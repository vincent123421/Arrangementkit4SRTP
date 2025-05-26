# main.py

import os
import pandas as pd
import subprocess
from seatable_data import SeaTableDataManager
from data_processor import process_and_filter_lectures
from image_downloader import ImageManager
from report_generator import ReportGenerator
import config

def main():
    image_manager = None

    try:
        # 1. 连接SeaTable并获取数据
        seatable_manager = SeaTableDataManager(
            config.SERVER_URL,
            config.API_TOKEN,
            config.BASE_NAME,
            config.TABLE_NAME
        )
        if not seatable_manager.authenticate():
            print("SeaTable 认证失败，程序退出。")
            return

        seatable_api_instance = seatable_manager.get_api_instance()

        # 2. 初始化图片管理器并设置临时目录
        image_manager = ImageManager(
            config.TEMP_IMAGE_DIR,
            config.REQUEST_HEADERS,
            config.IMAGE_DOWNLOAD_TIMEOUT,
            seatable_api_instance # 传递 SeaTableAPI 实例
        )
        image_manager.setup_temp_dir()

        raw_rows = seatable_manager.get_lecture_rows()

        # 3. 处理和筛选数据
        filtered_df = process_and_filter_lectures(
            raw_rows,
            config.START_DATE_STR,
            config.END_DATE_STR
        )

        # 4. 初始化报告生成器
        reporter = ReportGenerator(
            config.OUTPUT_MARKDOWN_FILENAME,
            config.OUTPUT_WORD_FILENAME,
            image_manager # 传递 image_manager 实例
        )

        # 5. 生成Markdown内容 (此步骤会触发图片下载)
        markdown_content = reporter.generate_markdown(filtered_df)

        # 6. 将Markdown转换为Word文档
        if markdown_content.strip(): # 检查是否有实际内容 (非空字符串或仅包含空格和换行符)
            reporter.convert_markdown_to_word()
        else:
            print("Markdown内容为空，未生成Word文档。")

    except Exception as e:
        print(f"程序执行过程中发生意外错误: {e}")
    finally:
        # 7. 清理临时图片目录 (正式运行时，取消注释这行)
        # if image_manager:
        #     try:
        #         image_manager.cleanup_temp_dir()
        #     except Exception as e:
        #         print(f"清理临时图片目录失败: {e}")
        print("\n程序执行完毕。")

if __name__ == '__main__':
    # 确保必要的库已安装
    try:
        import pandas as pd
        import requests
        from PIL import Image
        from seatable_api import SeaTableAPI
    except ImportError as e:
        print(f"错误：缺少必要的库。请运行 'pip install pandas requests Pillow seatable-api' 安装。")
        exit(1)
    # 确保 Pandoc 已安装
    try:
        subprocess.run(['pandoc', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("错误: Pandoc 命令未找到。请确保 Pandoc 已安装并添加到系统 PATH。")
        print("安装指南: https://pandoc.org/installing.html")
        exit(1)
    except Exception as e:
        print(f"检查 Pandoc 时发生错误: {e}")
        exit(1)
    main()
