import os
from .utils import get_file_path, get_yes_no, get_output_path, parse_subset_cols
from core.processor import FileProcessor

def show_main_menu():
    print("\n" + "=" * 60)
    print("          🌟 多格式文件处理工具 (Pro版) 🌟")
    print("=" * 60)
    print("支持格式: TXT, LOG, MD, CSV, XLSX/XLS, PDF, DOCX")
    print("\n请选择功能大类:")
    print(" 1️⃣  单个文件操作 (查看/删除重复行)")
    print(" 2️⃣  两个文件操作 (对比共同重复/跨文件清理)")
    print(" 3️⃣  合并文件 (合并并去重)")
    print(" 0️⃣  退出程序")
    print("-" * 60)

def handle_single_file_menu():
    print("\n" + "-" * 40)
    print("📁 单个文件操作")
    print("-" * 40)
    print("1. 查看文件内的重复行 (直接扫描并反馈)")
    print("2. 删除文件内的重复行 (另存为新文件或覆盖)")
    print("3. 返回主菜单")
    
    choice = input("\n请选择操作: ").strip()
    if choice not in ['1', '2']:
        return
        
    file_path = get_file_path("请输入要检查/处理的文件路径")
    if not file_path:
        return
        
    processor = FileProcessor(file_path)
    
    if choice == '1':
        print("\n🔍 正在查看文件重复行...")
        lines = processor._get_all_lines()
        from core.engine_memory import MemoryEngine
        # 为了查看重复，我们可以复用 engine 中的方法或者简单手写一个寻找 duplicate_positions 的逻辑
        line_dict = {}
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped:
                if stripped in line_dict:
                    line_dict[stripped].append(i)
                else:
                    line_dict[stripped] = [i]
        duplicates = {k: v for k, v in line_dict.items() if len(v) > 1}
        
        if duplicates:
            print(f"\n🔍 找到 {len(duplicates)} 组重复行：")
            for line, pos in sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
                print(f"📌 内容: {line[:50]}{'...' if len(line)>50 else ''} | 次数: {len(pos)} | 行号: {pos[:5]}")
            if len(duplicates) > 10:
                print(f"   ... 还有 {len(duplicates) - 10} 组重复未显示")
        else:
            print("✅ 文件中没有发现重复行！")
            
    elif choice == '2':
        ext = processor.ext
        subset_cols = None
        use_stream = False
        
        if ext in ['.csv', '.xlsx', '.xls']:
            print("\n⚙️  检测到结构化表格数据...")
            if get_yes_no("是否按 [指定列] 去重？(选 n 将按[整行完全相同]去重)", 'n'):
                cols_input = input("请输入作为主键的列名(逗号分隔): ")
                subset_cols = parse_subset_cols(cols_input)
        elif ext in ['.txt', '.log', '.md']:
            if os.path.getsize(file_path) / (1024 * 1024) > 200:
                print("\n⚠️  检测到大文件，建议使用流式处理。")
                use_stream = get_yes_no("是否开启低内存流式处理模式？", 'y')
                
        output_path = get_output_path(file_path)
        try:
            processor.process_dedupe(output_path, subset_cols=subset_cols, use_stream=use_stream)
        except Exception as e:
            print(f"\n❌ 处理时发生错误: {str(e)}")

def handle_two_files_menu():
    print("\n" + "-" * 40)
    print("📁📁 两个文件操作")
    print("-" * 40)
    print("1. 查看两个文件间的重复行")
    print("2. 清理文件1 (删除文件1中与文件2重复的行)")
    print("3. 清理文件2 (删除文件2中与文件1重复的行)")
    print("4. 同时清理两个文件 (删除各自与对方重复的行)")
    print("5. 返回主菜单")
    
    choice = input("\n请选择操作: ").strip()
    if choice not in ['1', '2', '3', '4']:
        return
        
    print("\n请选择第一个文件：")
    file1 = get_file_path()
    if not file1: return
    
    print("\n请选择第二个文件：")
    file2 = get_file_path()
    if not file2: return
    
    processor = FileProcessor(file1)
    
    if choice == '1':
        processor.compare_with(file2)
    elif choice == '2':
        out1 = get_output_path(file1)
        processor.clean_against(file2, clean_self=True, clean_other=False, out1=out1)
    elif choice == '3':
        out2 = get_output_path(file2)
        processor.clean_against(file2, clean_self=False, clean_other=True, out2=out2)
    elif choice == '4':
        out1 = get_output_path(file1)
        out2 = get_output_path(file2)
        processor.clean_against(file2, clean_self=True, clean_other=True, out1=out1, out2=out2)

def handle_merge_menu():
    print("\n" + "-" * 40)
    print("🔄 合并文件")
    print("-" * 40)
    
    file1 = get_file_path("请输入第一个文件")
    if not file1: return
    file2 = get_file_path("请输入第二个文件")
    if not file2: return
    
    out_dir = os.path.dirname(file1)
    default_out = os.path.join(out_dir, "合并输出_去重后.txt")
    output_path = input(f"\n请输入输出文件路径 [{default_out}]: ").strip()
    if not output_path:
        output_path = default_out
        
    remove_dup = get_yes_no("是否在合并时去除重复行？", 'y')
    processor = FileProcessor(file1)
    processor.merge_with(file2, output_path, remove_duplicates=remove_dup)
