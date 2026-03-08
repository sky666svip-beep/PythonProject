import os
import hashlib
from typing import Iterator, Tuple

class StreamEngine:
    """适用于无法完全放入内存的大文件，边读边 Hash 并写入临时文件"""

    @staticmethod
    def deduplicate_single(file_path: str, temp_output_path: str) -> Tuple[int, int]:
        """
        边读边写，仅在内存中维护 MD5/SHA hash 的去重引擎。
        返回 (保留行数, 移除行数)
        """
        seen_hashes = set()
        kept_count = 0
        removed_count = 0
        
        with open(file_path, 'r', encoding='utf-8') as f_in, \
             open(temp_output_path, 'w', encoding='utf-8') as f_out:
            
            for line in f_in:
                stripped = line.strip()
                if not stripped:
                    # 空行直接写回
                    f_out.write(line)
                    continue
                
                # 使用 hash 以节省内存 (比存原始字符串更省)
                line_hash = hash(stripped)
                
                if line_hash not in seen_hashes:
                    f_out.write(line)
                    seen_hashes.add(line_hash)
                    kept_count += 1
                else:
                    removed_count += 1
                    
        return kept_count, removed_count
