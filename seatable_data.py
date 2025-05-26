# seatable_data.py

from seatable_api import SeaTableAPI
import pandas as pd

class SeaTableDataManager:
    def __init__(self, server_url, api_token, base_name, table_name):
        self.api = SeaTableAPI(api_token, server_url) # SeaTableAPI 实例
        self.base_name = base_name
        self.table_name = table_name
        self.server_url = server_url

    def authenticate(self):

        try:
            self.api.auth()
            print(f"成功连接到 SeaTable 服务器: {self.server_url}")
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False

    def get_lecture_rows(self):

        print(f"\n从 SeaTable 获取数据 (表: '{self.table_name}')...")
        try:
            rows = self.api.list_rows(self.table_name)
            print(f"获取到原始行数: {len(rows)} 条")
            if not rows:
                print("警告: 从 SeaTable 获取到的数据为空。请检查 BASE_NAME 和 TABLE_NAME 或 API Token。")
            return rows
        except Exception as e:
            print(f"从 SeaTable 获取数据失败: {e}")
            return []

    def get_api_instance(self):

        return self.api
