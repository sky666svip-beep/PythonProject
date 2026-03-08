import pandas as pd
from typing import Optional, List

class TabularEngine:
    """处理 Pandas DataFrame 结构化数据的去重引擎"""

    @staticmethod
    def deduplicate(df: pd.DataFrame, subset_cols: Optional[List[str]] = None, keep: str = 'first') -> pd.DataFrame:
        """
        根据指定的列（主键）进行去重。
        如果 subset_cols 为空，则全列比对。
        """
        # 如果提供了特定列，需要处理字符串与数字索引的兼容问题
        if subset_cols:
            valid_cols = []
            for col in subset_cols:
                if col in df.columns:
                    valid_cols.append(col)
                elif col.isdigit() and int(col) in df.columns:
                    valid_cols.append(int(col))
                    
            if not valid_cols:
                print(f"⚠️ 指定的主键列 {subset_cols} 均不存在，将按整行比对。")
                subset_cols = None
            else:
                subset_cols = valid_cols

        return df.drop_duplicates(subset=subset_cols, keep=keep)
