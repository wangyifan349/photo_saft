import os
import hashlib
import platform
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
print("可以遍历指定目录下的所有文件和子目录，计算每个文件的哈希值，并移除重复的文件，从而帮助您节省存储空间。\n该程序通过BLAKE2b算法计算文件的哈希值，可以在Windows、Linux和MacOS等多个操作系统中运行。\n只需要输入目录路径，程序即可自动遍历目录，并删除重复的文件，非常方便实用。")
def traverse_directory(root_dir):
    """遍历目录下所有文件和子目录下的文件"""
    files = []
    # 使用os.walk函数遍历目录下所有文件和子目录
    for root, directories, filenames in os.walk(root_dir):
        # 遍历所有文件
        for filename in filenames:
            # 拼接出完整的文件路径
            file_path = os.path.join(root, filename)
            # 如果拥有读取该文件的权限，则将其加入到列表中
            if os.access(file_path, os.R_OK):
                files.append(file_path)
    return files
def remove_duplicates_in_directory_thread(directory_path, text_widget):
    def remove_duplicates_thread():
        remove_duplicates_in_directory(directory_path, text_widget)
    t = threading.Thread(target=remove_duplicates_thread)
    t.start()

def browse_button_callback(directory_entry, text_widget):
    directory_path = filedialog.askdirectory()
    directory_entry.delete(0, tk.END)
    directory_entry.insert(0, directory_path)
    confirm = messagebox.askyesno("确认", f"您确定要在目录 {directory_path} 下删除重复文件吗？")
    if confirm:
        remove_duplicates_in_directory_thread(directory_path, text_widget)
def start_button_callback(directory_entry, text_widget):
    directory_path = directory_entry.get()
    confirm = messagebox.askyesno("确认", f"您确定要在目录 {directory_path} 下删除重复文件吗？")
    if confirm:
        remove_duplicates_in_directory_thread(directory_path, text_widget)
def calculate_file_hash(file_path, block_size=65536):
    """计算文件的BLAKE2b哈希值"""
    # 初始化一个BLAKE2b哈希对象
    hash_func = hashlib.blake2b()
    # 以二进制只读方式打开文件
    with open(file_path, 'rb') as f:
        while True:
            # 循环读取文件内容，直到全部读取完毕
            data = f.read(block_size)
            if not data:
                break
            # 更新哈希对象
            hash_func.update(data)
    # 返回哈希值的16进制表示
    return hash_func.hexdigest()
def remove_duplicates_in_directory(directory_path, text_widget):
    # 验证路径是否存在
    if not os.path.exists(directory_path):
        print(f"目录不存在：{directory_path}")
        return

    # 遍历目录下所有文件和子目录下的文件
    files = traverse_directory(directory_path)

    # 计算每个文件的哈希值，存入字典中
    hash_dict = {}
    for file_path in files:
        # 计算文件的哈希值
        file_hash = calculate_file_hash(file_path)
        if file_hash not in hash_dict:
            # 如果哈希值不存在，则将其加入到字典中，以备后续查询
            hash_dict[file_hash] = file_path
        else:
            # 如果哈希值已存在，则说明该文件是重复的，直接删除
            if os.access(file_path, os.W_OK):
                try:
                    # 以二进制写模式打开文件，并清空文件内容
                    with open(file_path, 'wb'):
                         pass
                    os.remove(file_path)  # 删除文件
                    message = f"已删除重复文件：{file_path}"
                    print(message)
                    text_widget.insert(tk.END, message + "\n")
                except:
                    print("删除文件失败", file_path)
            else:
                # 如果没有写权限，则无法删除该文件
                print(f"无法写入文件：{file_path}")
# 定义获取目录路径的函数
def get_directory_path():
    system_type = platform.system()  # 获取当前操作系统类型
    if system_type == "Windows": 
        example_path = "C:\\Users\\本机用户1\\文档\\学校的论文" 
        separator = "\\"  #分隔符
    elif system_type == "Linux" or system_type == "Darwin":
        example_path = "/home/username/Documents/my_folder"
        separator = "/"
    else:
        example_path = "/home/用户名/Pictures" 
        separator = "/"#分隔符
    while True:
        directory_path = input("请输入目录路径（例如：{}）：".format(example_path))
        # 提示用户输入目录路径
        if os.path.exists(directory_path): 
            return directory_path 
        else:
            print("目录路径不存在，请重新输入！")
def create_gui():
    root = tk.Tk()
    root.title("文件去重工具")
    root.geometry("600x400")

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    top_frame = tk.Frame(main_frame)
    top_frame.pack(fill=tk.X, side=tk.TOP)

    directory_label = tk.Label(top_frame, text="目录路径：")
    directory_label.pack(side=tk.LEFT, padx=5)

    directory_entry = tk.Entry(top_frame)
    directory_entry.pack(fill=tk.X, expand=True, padx=5)

    browse_button = tk.Button(top_frame, text="选择目录", command=lambda: browse_button_callback(directory_entry, text_widget))
    browse_button.pack(side=tk.LEFT, padx=5)

    start_button = tk.Button(top_frame, text="开始", command=lambda: start_button_callback(directory_entry, text_widget))
    start_button.pack(side=tk.LEFT, padx=5)

    text_widget = tk.Text(main_frame, wrap=tk.WORD)
    text_widget.pack(fill=tk.BOTH, expand=True)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
