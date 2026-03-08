import os
from parsers.text_parser import TextParser
from parsers.tabular_parser import TabularParser
from parsers.rich_text_parser import RichTextParser
from core.engine_memory import MemoryEngine
from core.engine_stream import StreamEngine
from core.tabular_engine import TabularEngine

class FileProcessor:
    """根据文件后缀决定如何解析与调度去重引擎"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.ext = os.path.splitext(file_path)[1].lower()

    def process_dedupe(self, output_path: str, subset_cols: list = None, use_stream: bool = False):
        print(f"\n🚀 开始处理: {self.file_path}")
        
        # 1. 表格类别 (CSV, Excel)
        if self.ext in ['.csv', '.xlsx', '.xls']:
            parser = TabularParser(self.file_path)
            df = parser.read_dataframe()
            old_len = len(df)
            deduped_df = TabularEngine.deduplicate(df, subset_cols=subset_cols)
            new_len = len(deduped_df)
            
            removed_df = df[~df.index.isin(deduped_df.index)]
            
            parser.file_path = output_path # 切换写入目标
            parser.write_dataframe(deduped_df)
            print(f"✅ 处理完成。原行数: {old_len}, 去重后: {new_len}, 移除: {len(removed_df)}")
            if len(removed_df) > 0:
                print("🗑️ 被移除的重复内容预览：")
                print(removed_df.head(10).to_string(index=False))
                if len(removed_df) > 10:
                    print(f"  ... 还有 {len(removed_df) - 10} 行未显示")
        
        # 2. 富文本 (PDF, DOCX) - 强制转储为 TXT
        elif self.ext in ['.pdf', '.docx']:
            parser = RichTextParser(self.file_path)
            lines = parser.read_lines()
            kept, removed = MemoryEngine.deduplicate_single(lines)
            
            # 强制导出 txt
            out_txt = os.path.splitext(output_path)[0] + ".txt"
            writer = TextParser(out_txt)
            writer.write_lines(kept)
            print(f"✅ 已提取文本并去重，原格式未保留。输出至 {out_txt}")
            print(f"📊 保留段落: {len(kept)}, 移除重复: {len(removed)}")

        # 3. 纯文本类别 (TXT, MD, LOG 等)
        else:
            if use_stream:
                print("🌊 采用大文件流式处理模式...")
                k, r = StreamEngine.deduplicate_single(self.file_path, output_path)
                print(f"✅ 流式处理完成。保留: {k}, 移除: {r}")
            else:
                parser = TextParser(self.file_path)
                lines = parser.read_lines()
                kept, removed = MemoryEngine.deduplicate_single(lines)
                parser.file_path = output_path
                parser.write_lines(kept)
                print(f"✅ 处理完成。保留: {len(kept)}, 移除: {len(removed)}")

    def _get_all_lines(self) -> list:
        """内部辅助：获取该文件的所有纯文本行（不管原格式是什么）"""
        if self.ext in ['.csv', '.xlsx', '.xls']:
            print(f"⚠️  正在以纯文本模式读取表格文件 {self.file_path} 用于对比或合并。")
            parser = TabularParser(self.file_path)
            # 为了双文件比较，表格一律转为逗号分隔的纯文本行
            df = parser.read_dataframe()
            return df.to_csv(index=False, header=False).splitlines()
        elif self.ext in ['.pdf', '.docx']:
            parser = RichTextParser(self.file_path)
            return list(parser.read_lines())
        else:
            parser = TextParser(self.file_path)
            return list(parser.read_lines())
            
    def _save_all_lines(self, lines: list, output_path: str):
        """内部辅助：将处理后的纯文本行保存为 TXT 格式（双文件对比/合并默认降级输出 TXT）"""
        out_txt = os.path.splitext(output_path)[0] + ".txt"
        writer = TextParser(out_txt)
        writer.write_lines(lines)
        return out_txt

    def compare_with(self, other_file_path: str):
        """查看两个文件间的共同重复"""
        lines1 = self._get_all_lines()
        other_processor = FileProcessor(other_file_path)
        lines2 = other_processor._get_all_lines()
        
        common, only1, only2 = MemoryEngine.get_common_lines(lines1, lines2)
        
        print("\n📊 比较结果：")
        print(f"  - 文件1 独有行数: {len(only1)}")
        print(f"  - 文件2 独有行数: {len(only2)}")
        print(f"  - 共同重复行数: {len(common)}")

        if common:
            print(f"\n🔍 找到 {len(common)} 行重复内容")
            for line in sorted(common)[:10]:
                print(f"  - {line}")
            if len(common) > 10:
                print(f"  ... 还有 {len(common) - 10} 行未显示")

    def clean_against(self, other_file_path: str, clean_self=True, clean_other=False, out1=None, out2=None):
        """清理重复关系，可双向"""
        lines1 = self._get_all_lines()
        other_processor = FileProcessor(other_file_path)
        lines2 = other_processor._get_all_lines()
        
        if clean_self and out1:
            print(f"\n🧹 正在清理文件1（删除与文件2重复的行）...")
            kept1, removed1 = MemoryEngine.deduplicate_against_reference(lines1, lines2)
            actual_out1 = self._save_all_lines(kept1, out1)
            print(f"✅ 文件1清理完成，输出至 {actual_out1}。保留: {len(kept1)}, 删除重复: {len(removed1)}")
            
        if clean_other and out2:
            print(f"\n🧹 正在清理文件2（删除与文件1重复的行）...")
            kept2, removed2 = MemoryEngine.deduplicate_against_reference(lines2, lines1)
            actual_out2 = other_processor._save_all_lines(kept2, out2)
            print(f"✅ 文件2清理完成，输出至 {actual_out2}。保留: {len(kept2)}, 删除重复: {len(removed2)}")

    def merge_with(self, other_file_path: str, output_path: str, remove_duplicates: bool = True):
        """合并两个文件"""
        print(f"\n🔄 正在合并文件: {self.file_path} 和 {other_file_path}")
        lines1 = self._get_all_lines()
        other_processor = FileProcessor(other_file_path)
        lines2 = other_processor._get_all_lines()
        
        merged_lines = lines1 + lines2
        if remove_duplicates:
            kept, removed = MemoryEngine.deduplicate_single(merged_lines)
            actual_out = self._save_all_lines(kept, output_path)
            print(f"✅ 合并且去重完成！输出文件: {actual_out}")
            print(f"📊 最终行数: {len(kept)}, 合并过程中移除重复: {len(removed)}")
        else:
            actual_out = self._save_all_lines(merged_lines, output_path)
            print(f"✅ 直接合并完成(不去重)！输出文件: {actual_out}")
            print(f"📊 总行数: {len(merged_lines)}")
