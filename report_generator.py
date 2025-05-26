# report_generator.py

import os
import subprocess
import pandas as pd
from image_downloader import ImageManager # 需要导入以使用其方法和属性

class ReportGenerator:
    def __init__(self, output_md_filename, output_word_filename, image_manager: ImageManager):
        self.output_md_filename = output_md_filename
        self.output_word_filename = output_word_filename
        self.image_manager = image_manager # 传入ImageManager实例

    def generate_markdown(self, filtered_df):
        """
        根据筛选后的DataFrame生成Markdown内容。
        """
        markdown_output = []

        if filtered_df.empty:
            print("没有筛选后的数据可供生成 Markdown。")
            full_markdown_content = "# 讲座信息\n\n无可用讲座信息。\n"
        else:
            for index, row in filtered_df.iterrows():
                讲座名称 = row.get('讲座名称（全称）', 'N/A')
                报告人_职称 = row.get('讲座报告人+职称', 'N/A')
                讲座时间 = row.get('讲座时间')
                具体时间 = row.get('具体时间（例：14:00-15:00）', '')
                讲座地点 = row.get('讲座地点', 'N/A')
                讲座内容 = row.get('讲座内容（摘要）', '无摘要')

                formatted_time = "N/A"
                if pd.notna(讲座时间):
                    formatted_time = 讲座时间.strftime('%Y年%m月%d日')
                if 具体时间:
                    formatted_time = f"{formatted_time} {具体时间}"

                lecture_md = []
                lecture_md.append(f"# {讲座名称}")
                lecture_md.append(f"\n**主讲人：** {报告人_职称}")
                lecture_md.append(f"\n**时间：** {formatted_time}")
                lecture_md.append(f"\n**地点：** {讲座地点}")
                lecture_md.append(f"\n**内容摘要：** {讲座内容}\n")

                # 调用 ImageManager 下载图片
                final_image_path = self.image_manager.download_and_convert_image(row, index)

                if final_image_path:


                    markdown_image_filename = os.path.basename(final_image_path)

                    lecture_md.append(f"![{讲座名称}海报]({markdown_image_filename})\n")
                else:
                    lecture_md.append(f"<!-- 讲座 '{讲座名称}' 没有找到有效海报图片 -->\n") # 添加一个注释，方便调试

                markdown_output.append("\n".join(lecture_md))
                markdown_output.append("\n---\n")

            full_markdown_content = "\n".join(markdown_output)

        with open(self.output_md_filename, 'w', encoding='utf-8') as f:
            f.write(full_markdown_content)
        print(f"\nMarkdown 内容已保存到 '{self.output_md_filename}' 文件中。")
        return full_markdown_content

    def convert_markdown_to_word(self):
        """
        使用Pandoc将Markdown文件转换为Word文档。
        """
        print(f"正在使用 Pandoc 将 '{self.output_md_filename}' 转换为 '{self.output_word_filename}'...")
        try:
            subprocess.run(
                ['pandoc', self.output_md_filename, '-o', self.output_word_filename,
                 '--standalone', f'--resource-path={self.image_manager.temp_dir}'],
                check=True,
                encoding='utf-8'
            )
            print(f"\n成功生成 Word 文档: '{self.output_word_filename}'")
        except FileNotFoundError:
            print("错误: Pandoc 命令未找到。请确保 Pandoc 已安装并添加到系统 PATH。")
            print("安装指南: https://pandoc.org/installing.html")
        except subprocess.CalledProcessError as e:
            print(f"错误: Pandoc 转换失败。命令 '{' '.join(e.cmd)}' 返回了非零退出码 {e.returncode}。")
            print(f"标准输出:\n{e.stdout}")
            print(f"标准错误:\n{e.stderr}")
            print("请检查 Markdown 文件内容或 Pandoc 安装。")
        except Exception as e:
            print(f"转换 Word 文档时发生意外错误: {e}")

