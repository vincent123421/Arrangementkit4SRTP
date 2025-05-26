# Arrangementkit4SRTP


## 概述

此工具旨在自动化从南京大学 SeaTable 平台收集学期讲座信息，并将其格式化为 Markdown 和 Word (`.docx`) 报告。它能够根据指定日期范围筛选讲座，下载并处理讲座海报图片（包括 WebP 格式转换），并将所有信息整合到一个美观的文档中。

## 功能特性

*   **SeaTable 数据集成：** 通过 SeaTable API 自动获取讲座表格数据。
*   **灵活的日期筛选：** 支持指定起始和结束日期来筛选相关讲座。
*   **讲座信息格式化：** 将讲座的名称、主讲人、时间、地点、内容摘要等信息整理成清晰的文本格式。
*   **海报图片处理：** 自动下载讲座海报图片，并支持将 WebP 格式的图片转换为兼容性更好的 JPEG 格式。
*   **多格式报告输出：** 生成 Markdown (`.md`) 文件，并利用 Pandoc 工具将其转换为 Microsoft Word (`.docx`) 文档。
*   **临时文件管理：** 自动创建和清理临时图片目录，保持项目整洁。

## 项目结构

```
lecture_report_generator/
├── config.py                 # 配置文件，包含API凭证、日期范围、输出文件名等。
├── seatable_data.py          # 负责与SeaTable API交互，获取原始数据。
├── data_processor.py         # 处理原始数据，包括类型转换、日期筛选和排序。
├── image_downloader.py       # 管理图片的下载、格式转换（特别是WebP到JPG）。
├── report_generator.py       # 将处理后的数据生成Markdown，并调用Pandoc转换为Word。
├── main.py                   # 程序主入口，协调调用各个模块。
└── requirements.txt          # 项目所需的Python依赖库列表。
```

## 环境准备

在运行此工具之前，请确保您的系统满足以下要求：

### 1. Python 环境

*   **Python 3.x** (推荐 3.8+)

### 2. Python 依赖库

安装所有必需的 Python 库。在项目根目录下打开终端或命令行，运行：

```bash
pip install -r requirements.txt
```

`requirements.txt` 内容：
```
pandas
seatable-api
requests
Pillow
```

### 3. Pandoc 工具

*   **Pandoc：** 这是一个通用的文档转换工具，用于将 Markdown 转换为 Word (`.docx`)。您需要将其安装在您的系统上，并确保它已添加到系统 PATH 中。

    *   **安装指南：** 访问 [Pandoc 官方网站](https://pandoc.org/installing.html) 下载并安装适用于您操作系统的版本。
    *   **验证安装：** 打开命令行或终端，运行 `pandoc --version`。如果显示版本信息，则表示安装成功。

## 配置指南

在运行工具之前，您需要编辑 `config.py` 文件以配置 SeaTable API 凭证、日期范围和输出文件名。

打开 `config.py` 并修改以下变量：

```python
# config.py

# --- SeaTable API 配置 ---
SERVER_URL = 'https://table.nju.edu.cn'
# 建议使用环境变量管理API TOKEN，例如：
# API_TOKEN = os.getenv('SEATABLE_API_TOKEN')
API_TOKEN = 'YOUR_SEATABLE_API_TOKEN' # <-- 替换为您的 SeaTable API Token
BASE_NAME = '讲座信息收集'           # <-- 您的Base名称
TABLE_NAME = '春季学期讲座信息收集'   # <-- 您的表格名称

# --- 筛选时间范围 ---
START_DATE_STR = '2025-05-24' # <-- 讲座筛选起始日期 (YYYY-MM-DD)
END_DATE_STR = '2025-05-31'   # <-- 讲座筛选结束日期 (YYYY-MM-DD)

# --- 输出文件配置 ---
# 这些文件名将根据日期范围自动生成，通常无需修改
OUTPUT_WORD_FILENAME = f'讲座信息_{START_DATE_STR}_至_{END_DATE_STR}.docx'
OUTPUT_MARKDOWN_FILENAME = f'讲座信息_{START_DATE_STR}_至_{END_DATE_STR}.md'
OUTPUT_CSV_FILENAME = f'讲座信息_{START_DATE_STR}_至_{END_DATE_STR}.csv'
TEMP_IMAGE_DIR = 'temp_lecture_images' # 临时图片存储目录

# --- 其他配置 ---
# 请求头，包含必要的认证信息，通常无需修改，但确保API_TOKEN已在Authorization中
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    'Referer': SERVER_URL,
    'Authorization': f'Token {API_TOKEN}' # <--- 此处API_TOKEN将从上方变量中获取
}
IMAGE_DOWNLOAD_TIMEOUT = 15 # 图片下载超时时间（秒）
```

**获取 SeaTable API Token：**
1.  登录您的 SeaTable 账户。
2.  点击右上角的头像，选择 "个人设置"。
3.  在左侧导航栏中选择 "API Token"。
4.  点击 "生成 API Token"，确保给予足够的权限（至少包括读取指定 Base 和表格的权限）。
5.  复制生成的 Token，并将其粘贴到 `config.py` 的 `API_TOKEN` 变量处。

## 运行工具

完成环境准备和配置后，您可以在项目根目录下运行 `main.py` 文件：

```bash
python main.py
```

### 运行流程

1.  程序将连接到 SeaTable 服务器并进行认证。
2.  从指定表格获取所有讲座数据。
3.  根据 `config.py` 中定义的日期范围筛选讲座。
4.  对于每个筛选出的讲座，程序将尝试下载其海报图片到 `temp_lecture_images` 临时目录。
5.  所有讲座信息（包括图片引用）将被格式化为 Markdown 文本，并保存到 `.md` 文件。
6.  Pandoc 将被调用，把 Markdown 文件及其引用的图片转换为一个 `.docx` Word 文档。
7.  程序运行结束后，`temp_lecture_images` 临时目录将被自动清理。

### 输出文件

运行成功后，您将在项目根目录下找到：

*   `讲座信息_YYYY-MM-DD_至_YYYY-MM-DD.md`：生成的 Markdown 格式讲座报告。
*   `讲座信息_YYYY-MM-DD_至_YYYY-MM-DD.docx`：生成的 Word 格式讲座报告。

## 常见问题与故障排除

*   **`AttributeError: module 'config' has no attribute '...'`：**
    *   **原因：** `config.py` 文件中缺少某个配置项，或者文件没有保存。
    *   **解决方案：** 确保您已将最新版本的 `config.py` 内容完全复制并保存到您的文件中。
*   **`FileNotFoundError: 'pandoc' command not found`：**
    *   **原因：** Pandoc 没有安装，或者没有添加到系统 PATH 中。
    *   **解决方案：** 按照 [Pandoc 官方网站](https://pandoc.org/installing.html) 的指南安装 Pandoc，并确保其可执行文件位于系统 PATH 中。
*   **`警告: 使用 SeaTable API 下载文件失败 (...)` 或 图片未显示：**
    *   **原因：**
        1.  `API_TOKEN` 无效、过期或权限不足。
        2.  网络连接问题，无法访问 SeaTable 服务器。
        3.  SeaTable 提供的图片 URL 本身有特殊访问限制。
    *   **解决方案：**
        1.  **最常见原因：** 重新生成 SeaTable API Token，并更新 `config.py`。确保 Token 拥有读取指定 Base 和表格以及下载附件的权限。
        2.  检查您的网络连接。
        3.  暂时注释掉 `main.py` 中 `finally` 块的 `image_manager.cleanup_temp_dir()`，手动运行程序，然后检查 `temp_lecture_images` 目录，看是否有下载的文件以及文件内容是否正确。

## 贡献与支持

如果您有任何问题、建议或想为项目贡献代码，请随时通过 [GitHub Issues](YOUR_GITHUB_REPO_URL/issues) 提交。

---
请将 `YOUR_GITHUB_REPO_URL` 替换为你的实际 GitHub 仓库地址（如果你有的话）。