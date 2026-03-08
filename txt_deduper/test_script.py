import os
import pandas as pd
from core.processor import FileProcessor

csv_file = 'test_header.csv'
with open(csv_file, 'w', encoding='utf-8') as f:
    f.write('id,name\n1,alice\nid,name\n2,bob\nid,name\n')

print("--- 测试: 无表头整行去重 (首行重复是否能被删除) ---")
p = FileProcessor(csv_file)
p.process_dedupe('test_out_header.csv', subset_cols=None)

print("\n--- 输出文件内容检查 ---")
with open('test_out_header.csv', 'r', encoding='utf-8') as f:
    print(f.read())
