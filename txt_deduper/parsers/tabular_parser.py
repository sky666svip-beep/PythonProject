import pandas as pd
from typing import Iterator, List, Optional, Union

class TabularParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._is_csv = self.file_path.lower().endswith('.csv')
    
    def read_dataframe(self) -> pd.DataFrame:
        if self._is_csv:
            return pd.read_csv(self.file_path, encoding='utf-8', header=None)
        else:
            return pd.read_excel(self.file_path, header=None)
    
    def write_dataframe(self, df: pd.DataFrame) -> None:
        if self._is_csv:
            df.to_csv(self.file_path, index=False, header=False)
        else:
            df.to_excel(self.file_path, index=False, header=False)
            
    # 如果基于流式降级读取大 CSV，可支持 Chunk 迭代
    def read_chunks(self, chunk_size: int = 10000) -> Iterator[pd.DataFrame]:
        if self._is_csv:
            for chunk in pd.read_csv(self.file_path, chunksize=chunk_size):
                yield chunk
        else:
            # Excel 并不天然支持高效的 stream 分块，这部分可全量读或按一定边界切割。
            # 为了内存安全，返回整个 df 作为一个 chunk
            yield pd.read_excel(self.file_path)
