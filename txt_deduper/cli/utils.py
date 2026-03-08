import os

def get_file_path(prompt="请输入文件路径"):
    """获取用户输入的文件路径"""
    while True:
        file_path = input(f"{prompt} (输入 'q' 退出): ").strip()
        if file_path.lower() == 'q':
            return None
        if os.path.exists(file_path):
            return file_path
        print(f"❌ 文件不存在: {file_path}")

def get_yes_no(prompt, default='y'):
    """获取是/否的选择"""
    valid = {'y': True, 'yes': True, 'n': False, 'no': False}
    prompt_str = f"{prompt} [Y/n]: " if default == 'y' else f"{prompt} [y/N]: "
    while True:
        choice = input(prompt_str).strip().lower()
        if not choice:
            return default == 'y'
        if choice in valid:
            return valid[choice]
        print("请回答 'y' 或 'n'")

def get_output_path(source_path: str) -> str:
    """生成默认的安全输出路径"""
    dir_name, file_name = os.path.split(source_path)
    base_name, ext = os.path.splitext(file_name)
    # 对于 PDF/DOCX，这里虽然生成 _去重后.pdf 等后缀，但 Processor 会接管改成 .txt
    return os.path.join(dir_name, f"{base_name}_去重后{ext}")

def parse_subset_cols(input_str: str) -> list:
    """解析用户输入的主键列（逗号分隔）"""
    if not input_str.strip():
        return None
    return [col.strip() for col in input_str.split(',') if col.strip()]
