# data_processor.py

import pandas as pd

def process_and_filter_lectures(raw_rows, start_date_str, end_date_str):
    """
    将原始SeaTable数据转换为DataFrame，并根据日期范围进行筛选和排序。

    Args:
        raw_rows (list): 从SeaTable获取的原始行数据。
        start_date_str (str): 起始日期字符串 (YYYY-MM-DD)。
        end_date_str (str): 结束日期字符串 (YYYY-MM-DD)。

    Returns:
        pd.DataFrame: 筛选并排序后的讲座信息DataFrame。
    """
    if not raw_rows:
        print("没有数据可供处理。")
        return pd.DataFrame()

    df = pd.DataFrame(raw_rows)

    if '讲座时间' not in df.columns:
        print(f"错误：DataFrame 中不存在名为 '讲座时间' 的列。请检查SeaTable列名是否正确。可用列: {df.columns.tolist()}")
        return pd.DataFrame()

    # 转换 '讲座时间' 列为 datetime 对象
    df['讲座时间'] = pd.to_datetime(df['讲座时间'], errors='coerce')
    # 如果存在时区信息，移除它以便与纯日期比较
    if df['讲座时间'].dt.tz is not None:
        df['讲座时间'] = df['讲座时间'].dt.tz_localize(None)

    # 转换筛选日期为 datetime.date 对象
    start_date_dt = pd.to_datetime(start_date_str).date()
    end_date_dt = pd.to_datetime(end_date_str).date()

    # 筛选掉 '讲座时间' 为 NaT 的行，然后按日期范围筛选
    filtered_df = df[df['讲座时间'].notna()].copy()
    print(f"去除无效 '讲座时间' 后行数: {len(filtered_df)}")
    print(f"正在筛选日期范围: {start_date_str} 至 {end_date_str}")

    filtered_df = filtered_df[
        (filtered_df['讲座时间'].dt.date >= start_date_dt) &
        (filtered_df['讲座时间'].dt.date <= end_date_dt)
    ].copy()

    print(f"最终筛选后行数: {len(filtered_df)} 条")

    if not filtered_df.empty:
        print("筛选后的 DataFrame 头部预览:")
        print(filtered_df.head())
        # 按讲座时间排序
        filtered_df = filtered_df.sort_values(by='讲座时间').reset_index(drop=True)
    else:
        print(f"在 '{start_date_str}' 到 '{end_date_dt}' 范围内没有找到讲座信息。")

    return filtered_df
