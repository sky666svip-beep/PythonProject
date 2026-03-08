from typing import Iterator, Tuple, List, Set, Iterable

class MemoryEngine:
    """基于内存的快速去重引擎，适用于能全部加载进内存的纯文本文件"""

    @staticmethod
    def deduplicate_single(lines: Iterator[str], keep_first: bool = True) -> Tuple[List[str], List[str]]:
        """
        单文件去重
        返回: (保留的行列表, 删除的重复行列表)
        """
        all_lines = list(lines)
        seen = set()
        kept = []
        removed = []
        
        if keep_first:
            for line in all_lines:
                if line and line not in seen:
                    kept.append(line)
                    seen.add(line)
                elif line:
                    removed.append(line)
        else:
            # 保留最后出现的行，则逆向遍历
            for line in reversed(all_lines):
                if line and line not in seen:
                    kept.append(line)
                    seen.add(line)
                elif line:
                    removed.append(line)
            kept.reverse()
            removed.reverse()
            
        return kept, removed

    @staticmethod
    def get_common_lines(lines1: Iterator[str], lines2: Iterator[str]) -> Tuple[Set[str], Set[str], Set[str]]:
        """
        找出共同行
        返回: (两者都有的行, 仅1有的行, 仅2有的行)
        """
        set1 = set([l for l in lines1 if l])
        set2 = set([l for l in lines2 if l])
        return set1 & set2, set1 - set2, set2 - set1

    @staticmethod
    def deduplicate_against_reference(source_lines: Iterator[str], ref_lines: Iterable[str]) -> Tuple[List[str], List[str]]:
        """
        参照参考文件进行去重：删除source中在ref里出现过的行
        返回: (保留的行, 删除的行)
        """
        ref_set = set([l for l in ref_lines if l])
        kept = []
        removed = []
        for line in source_lines:
            if not line:
                kept.append(line)
            elif line not in ref_set:
                kept.append(line)
            else:
                removed.append(line)
        return kept, removed
