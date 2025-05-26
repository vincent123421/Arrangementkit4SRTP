import csv
import os
import pypandoc  # 推荐使用，需要 pip install pypandoc
import tempfile
import requests
import uuid

def download_image_and_get_markdown(image_url, temp_img_dir, alt_text="图片"):
    """
    下载图片到临时目录，并返回 Markdown 格式的图片链接。
    如果下载失败，返回一个错误提示文本。
    """
    if not image_url:
        return ""  # 如果没有URL，返回空字符串

    try:
        # 设置请求超时
        response = requests.get(image_url, stream=True, timeout=10)
        response.raise_for_status()  # 检查HTTP响应状态码，如果不是200会抛出HTTPError

        # 从Content-Type获取文件扩展名
        content_type = response.headers.get('Content-Type', '').split(';')[0]
        extension_map = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/bmp': '.bmp',
            'image/webp': '.webp',
            'image/svg+xml': '.svg'  # SVG图片可能需要特殊的pandoc版本或配置来嵌入
        }
        ext = extension_map.get(content_type, '.bin')  # 默认为.bin，防止未知类型

        # 生成唯一的本地文件名
        unique_filename = f"{uuid.uuid4()}{ext}"
        local_img_path = os.path.join(temp_img_dir, unique_filename)

        with open(local_img_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Downloaded: {image_url} to {local_img_path}")
        # 返回 Markdown 图片语法
        # 注意：Markdown语法中图片路径需要是相对路径或绝对路径，
        # 且在Pandoc转换时，该路径必须是Pandoc能访问到的本地文件
        # 这里使用绝对路径，Pandoc会处理
        return f"![{alt_text}]({local_img_path})"

    except requests.exceptions.Timeout:
        print(f"Warning: Image download from {image_url} timed out.")
        return f"[图片下载超时：{image_url}]"
    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not download image from {image_url}: {e}")
        return f"[图片下载失败：{image_url}]"
    except Exception as e:
        print(f"Warning: An unexpected error occurred during image download/save from {image_url}: {e}")
        return f"[图片处理错误：{image_url}]"
def csv_to_markdown_to_word(csv_filepath, output_word_filepath):
    """
    读取CSV文件，转换为Markdown格式，然后生成Word文档。

    Args:
        csv_filepath (str): 输入的CSV文件路径。
        output_word_filepath (str): 输出的Word文件路径 (例如 'output.docx')。
    """
    md_content = []

    try:
        with open(csv_filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)  # 读取表头

            # --- 1. 生成 Markdown 表头 ---
            # 确保每个单元格内容中的管道符 | 被转义，否则会破坏Markdown表格结构
            escaped_headers = [header.replace('|', '\\|') for header in headers]
            md_content.append(f"| {' | '.join(escaped_headers)} |")

            # --- 2. 生成 Markdown 分隔线 ---
            md_content.append(f"|{'-' * 3}{'|' + '-' * 3 * len(headers)}|")
            # 简化版：md_content.append(f"|{'---' * len(headers)}|")
            # 确保分隔线长度与列数匹配，且格式正确
            md_content.append(f"|{'---' * len(headers)}|")

            # --- 3. 生成 Markdown 行数据 ---
            for row in reader:
                # 确保每个单元格内容中的管道符 | 被转义
                escaped_row = [cell.replace('|', '\\|') for cell in row]
                md_content.append(f"| {' | '.join(escaped_row)} |")

        markdown_text = "\n".join(md_content)
        print("--- Generated Markdown Content ---")
        print(markdown_text)
        print("----------------------------------")

        # --- 将Markdown内容保存到临时文件 ---
        # 使用 tempfile 确保临时文件创建和清理的健壮性
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.md', encoding='utf-8') as temp_md_file:
            temp_md_file.write(markdown_text)
            temp_md_path = temp_md_file.name

        print(f"Markdown content saved to temporary file: {temp_md_path}")

        # --- 使用 pypandoc 将 Markdown 转换为 Word ---
        print(f"Converting '{temp_md_path}' to Word document '{output_word_filepath}' using Pandoc...")
        try:
            # `extra_args` 可以添加额外的 Pandoc 参数，例如样式文件
            # pypandoc.convert_file(temp_md_path, 'docx', outputfile=output_word_filepath, extra_args=['--reference-doc=path/to/your/template.docx'])
            pypandoc.convert_file(temp_md_path, 'docx', outputfile=output_word_filepath)
            print(f"Successfully created Word document: {output_word_filepath}")
        except Exception as e:
            print(f"Error during Pandoc conversion: {e}")
            print("Please ensure Pandoc is installed and accessible in your system's PATH.")
            print("You can verify by running 'pandoc --version' in your terminal.")

    except FileNotFoundError:
        print(f"Error: CSV file not found at '{csv_filepath}'")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # --- 清理临时文件 ---
        if 'temp_md_path' in locals() and os.path.exists(temp_md_path):
            os.remove(temp_md_path)
            print(f"Cleaned up temporary Markdown file: {temp_md_path}")


