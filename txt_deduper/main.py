import sys
from cli.menus import show_main_menu, handle_single_file_menu, handle_two_files_menu, handle_merge_menu
# 启动程序
def main():
    while True:
        show_main_menu()
        choice = input("\n请输入选项编号: ").strip()

        if choice == '1':
            handle_single_file_menu()
        elif choice == '2':
            handle_two_files_menu()
        elif choice == '3':
            handle_merge_menu()
        elif choice == '0':
            print("\n👋 感谢使用，再见！")
            break
        else:
            print("❌ 无效选项，请重新选择")

        input("\n按 Enter 键继续...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断，再见！")
    except Exception as e:
        print(f"\n❌ 致命错误: {e}")
        sys.exit(1)
