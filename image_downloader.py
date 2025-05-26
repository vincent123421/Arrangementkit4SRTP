# image_downloader.py

import os
import shutil
import requests
import mimetypes
from PIL import Image
# from urllib.parse import urljoin
from seatable_api import SeaTableAPI


class ImageManager:
    def __init__(self, temp_dir, request_headers, timeout, seatable_api_instance: SeaTableAPI):
        self.temp_dir = temp_dir
        self.request_headers = request_headers
        self.timeout = timeout
        self.seatable_api = seatable_api_instance

    def setup_temp_dir(self):
        # ... (unchanged) ...
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"已清空: {self.temp_dir}")
        os.makedirs(self.temp_dir, exist_ok=True)
        print(f"图片将下载到: {os.path.abspath(self.temp_dir)}")

    def cleanup_temp_dir(self):
        # ... (unchanged) ...
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                print(f"\n已清理临时图片目录: {self.temp_dir}")
            except Exception as e:
                print(f"清理临时图片目录失败: {e}")

    def _get_image_url(self, image_field_value):
        # ... (unchanged) ...
        if isinstance(image_field_value, list) and image_field_value:
            first_item = image_field_value[0]
            if isinstance(first_item, dict) and 'url' in first_item:
                return first_item['url']
            elif isinstance(first_item, str):
                return first_item
        elif isinstance(image_field_value, str):
            return image_field_value
        return None

    def download_and_convert_image(self, row_data, index):
        image_field_value = row_data.get('讲座海报照片')
        initial_image_url = self._get_image_url(image_field_value)

        讲座名称 = row_data.get('讲座名称（全称）', f'讲座_{index}')

        if initial_image_url:
            try:
                unified_base_name = f"lecture_poster_{index}"

                _, url_ext = os.path.splitext(initial_image_url.split('?')[0])
                original_ext_lower = url_ext.lower() if url_ext else ".jpg"

                temp_download_path = os.path.join(self.temp_dir, f"{unified_base_name}{original_ext_lower}")

                print(
                    f"正在使用 SeaTable API 下载图片: URL={initial_image_url} 到 {temp_download_path} for '{讲座名称}'...")

                download_success = self.seatable_api.download_file(initial_image_url, temp_download_path)



                print(f"原始图片已下载到: {temp_download_path}")

                final_image_path_for_md = temp_download_path  # 默认路径

                # 验证下载的文件是否存在且是有效的图像文件
                if not os.path.exists(temp_download_path):
                    print(f"错误: 文件 {temp_download_path} 不存在，尽管 download_file 报告成功。")
                    print("DEBUG: 下载的文件不存在，将返回 None。")  # DEBUG: 2
                    return None

                try:

                    img = Image.open(temp_download_path)
                    img_format = img.format.lower()  # 获取实际文件格式，如 'jpeg', 'png', 'webp'
                    img.close()

                    if img_format == 'jpeg':
                        current_ext = '.jpg'
                    elif img_format == 'png':
                        current_ext = '.png'
                    elif img_format == 'webp':
                        current_ext = '.webp'
                    # 添加其他常见格式判断，如 'gif', 'bmp' 等
                    else:
                        print(f"警告: 无法识别的图片格式: {img_format} for {temp_download_path}")
                        current_ext = original_ext_lower


                    if current_ext != original_ext_lower:
                        new_temp_download_path = os.path.join(self.temp_dir, f"{unified_base_name}{current_ext}")
                        os.rename(temp_download_path, new_temp_download_path)
                        print(f"重命名文件从 {temp_download_path} 到 {new_temp_download_path} (格式匹配)")
                        temp_download_path = new_temp_download_path
                        original_ext_lower = current_ext

                    final_image_path_for_md = temp_download_path  # 更新为重命名后的路径

                except Exception as e:
                    print(f"警告: 无法打开或验证下载的图片文件 {temp_download_path}: {e}。可能不是有效图片。")
                    print("DEBUG: 无法验证图片文件，将返回 None。")  # DEBUG: 3
                    return None

                # 处理WebP转换
                if original_ext_lower == '.webp':
                    print(f"检测到 WebP 图像，尝试转换为 JPEG...")
                    try:
                        img = Image.open(temp_download_path)
                        converted_jpg_path = os.path.join(self.temp_dir, f"{unified_base_name}.jpg")
                        img.save(converted_jpg_path, "JPEG")
                        print(f"WebP 图像已成功转换为 JPEG: {converted_jpg_path}")
                        os.remove(temp_download_path)
                        print(f"已删除原始 WebP 文件: {temp_download_path}")
                        final_image_path_for_md = converted_jpg_path
                    except Exception as e:
                        print(f"警告: WebP 图像转换失败 ({temp_download_path}): {e}。将尝试使用原始 WebP 文件。")


                print(f"DEBUG: 最终返回的图片路径: {final_image_path_for_md}")  # DEBUG: 4
                return final_image_path_for_md

            except Exception as e:
                print(f"警告: 处理图片时发生未知错误 ({initial_image_url}) for '{讲座名称}': {e}")
                print("DEBUG: 捕获到未知异常，将返回 None。")  # DEBUG: 5
                return None
        else:
            print(f"INFO: 讲座 '{讲座名称}' 没有提供海报图片。")
            print("DEBUG: initial_image_url 为空，将返回 None。")  # DEBUG: 6
            return None

