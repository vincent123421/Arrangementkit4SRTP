import requests
import pandas as pd
import json # 用于在调试时查看JSON结构

# --- 新的爬取函数，针对API请求和JSON数据 ---
def scrape_nju_api_data(api_url, headers, column_mapping=None):
    """
    爬取指定API URL的JSON数据，并转换为DataFrame。
    如果提供了 column_mapping，则根据映射筛选和重命名列。
    此版本已更新以处理数据在 `data['tables'][0]['rows']` 结构中的情况。

    Args:
        api_url (str): 目标API的URL。
        headers (dict): 包含认证信息（如Cookie）的请求头。
        column_mapping (dict, optional): 字典，键是API返回的原始列名（或ID），
                                          值是你想重命名成的中文名。
                                          例如: {"8Y7q": "标题", "3EYP": "主讲人"}。
                                          默认为None，表示不进行列筛选和重命名。

    Returns:
        pandas.DataFrame: 包含爬取数据的DataFrame，如果失败则返回None。
    """
    print(f"正在尝试从 API: {api_url} 爬取数据...")

    try:
        # 发送HTTP GET请求获取API数据
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功

        # 解析JSON响应
        data = response.json()

        # 打印原始JSON数据（用于调试，了解数据结构）
        print("\n--- API 响应数据预览（前1000字符） ---")
        print(json.dumps(data, indent=2)[:1000])
        print("--- API 响应数据预览结束 ---\n")

        df = None # 初始化 DataFrame

        # --- 新的数据提取逻辑 ---
        # 尝试从 data['tables'][0]['rows'] 中提取数据
        if 'tables' in data and isinstance(data['tables'], list) and len(data['tables']) > 0:
            first_table = data['tables'][0]
            if 'rows' in first_table and isinstance(first_table['rows'], list):
                df = pd.DataFrame(first_table['rows'])
                print(f"成功从API爬取 {len(first_table['rows'])} 条数据 (来自 tables[0]['rows'])。")
            else:
                print("错误：API响应的 'tables' 键中第一个元素未找到 'rows' 键或其不是列表结构。")
                return None
        # 兼容性检查：如果数据直接在 'rows' 键下（虽然根据你的描述不太可能，但保留）
        elif 'rows' in data and isinstance(data['rows'], list):
            df = pd.DataFrame(data['rows'])
            print(f"成功从API爬取 {len(data['rows'])} 条原始数据 (来自 'rows' 键)。")
        else:
            print("错误：API响应中未找到预期的讲座数据结构 ('tables'[0]['rows'] 或 'rows')。")
            return None

        if df is None: # 如果以上任何情况都没成功提取数据
            return None

        # --- 应用列筛选和重命名 (这部分逻辑保持不变) ---
        if column_mapping:
            # 获取DataFrame中实际存在的列名
            df_columns = set(df.columns)

            # 过滤出column_mapping中那些在df_columns中存在的键
            valid_columns_to_map = {
                api_col: display_name
                for api_col, display_name in column_mapping.items()
                if api_col in df_columns
            }

            if not valid_columns_to_map:
                print("警告：提供的column_mapping中没有键与API响应的列名匹配。未进行列筛选和重命名。")
                return df # 返回原始DataFrame，因为它没有匹配的列

            # 1. 筛选列：只保留我们需要的列
            selected_columns = list(valid_columns_to_map.keys())
            df_filtered = df[selected_columns].copy() # 使用.copy()避免SettingWithCopyWarning

            # 2. 重命名列
            df_renamed = df_filtered.rename(columns=valid_columns_to_map)

            print(f"根据映射筛选并重命名了 {len(valid_columns_to_map)} 列。")
            return df_renamed
        else:
            print("未提供 column_mapping，返回所有原始列。")
            return df

    except requests.exceptions.RequestException as e:
        print(f"请求API错误：{e}")
        return None
    except json.JSONDecodeError:
        print("错误：API响应不是有效的JSON格式。")
        print(f"响应内容（非JSON）：{response.text[:500]}...")
        return None
    except Exception as e:
        print(f"发生未知错误：{e}")
        return None