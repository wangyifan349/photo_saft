import os
import shutil
import hashlib
import platform
import threading
from zipfile import ZipFile
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
def is_directory_exist(path):
    if os.path.isdir(path):
        return True
    else:
        return False
# 此函数允许用户从本机中浏览和选择一个目录
def browse_directory():
    # 在此函数中使用全局变量'image_directory'
    global image_directory 
    # 打开一个对话框，让用户选择一个目录，并将其路径存储在'image_directory'中
    image_directory = filedialog.askdirectory()
    # 更新标签(widget)的文本为所选目录的路径
    directory_label.config(text=image_directory)
    # 删除条目(widget)中当前存在的任何文本
    directory_entry.delete(0, 'end')
    # 将所选目录的路径插入到条目(widget)中
    directory_entry.insert(0, image_directory)


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
# 查找指定目录下所有符合条件的文件（即指定扩展名的文件）并返回列表
def find_files_with_extensions(path, extensions):
    result = []
    for root, dirs, files in os.walk(path): # 遍历目录树
        for file in files:
            if file.lower().endswith(extensions): # 判断文件名是否以指定扩展名结尾
                result.append(os.path.join(root, file)) # 将符合条件的文件的路径添加到结果列表中
    return result
def start_copy_thread():
    # 使用线程进行文件拷贝，以防止GUI阻塞
    copy_thread = threading.Thread(target=start_copy)
    copy_thread.start()
# 在指定目录下创建一个以给定扩展名命名的子目录，并返回该子目录路径
def create_subfolder_by_extension(target_dir, extension):
    subfolder = os.path.join(target_dir, extension.lstrip(".")) # 将给定扩展名转换为目录名，并将其与目标目录连接起来
    os.makedirs(subfolder, exist_ok=True) # 创建子目录（若不存在）
    return subfolder

def copy_files_to_directory(files, target_dir, extensions):
    os.makedirs(target_dir, exist_ok=True)
    extension_to_subfolder = {}
    for extension in extensions:
        subfolder = create_subfolder_by_extension(target_dir, extension)
        extension_to_subfolder[extension] = subfolder

    for file in files:
        file_basename = os.path.basename(file)
        file_extension = os.path.splitext(file_basename)[1].lower()

        # 获取文件的修改时间
        file_mtime = os.path.getmtime(file)
        file_date = datetime.fromtimestamp(file_mtime)
        year = file_date.year
        month = file_date.month

        # 根据文件扩展名确定目标子文件夹
        target_subfolder = extension_to_subfolder[file_extension]
        target_year_subfolder = os.path.join(target_subfolder, str(year))
        target_month_subfolder = os.path.join(target_year_subfolder, f"{month:02d}")

        # 确保目标子文件夹存在
        os.makedirs(target_month_subfolder, exist_ok=True)

        # 复制文件到目标子文件夹
        target_file_path = os.path.join(target_month_subfolder, file_basename)
        counter = 1
        while os.path.exists(target_file_path):
            name, ext = os.path.splitext(file_basename)
            target_file_path = os.path.join(target_month_subfolder, f"{name}_{counter}{ext}")
            counter += 1
        try:
            shutil.copy(file, target_file_path)
            #print(file,target_file_path)
        except:
            print("无法拷贝:", file)

# 弹出文件选择对话框，获取源磁盘路径
def browse_disk():
    disk = filedialog.askdirectory()
    disk = disk.replace("\\", "/")  # 将 '\' 替换为 '/'
    app.source_disk.set(disk)

# 弹出文件选择对话框，获取目标目录路径
def browse_target():
    target = filedialog.askdirectory()
    target = target.replace("\\", "/")  # 将 '\' 替换为 '/'
    app.target_dir.set(target)

# 开始拷贝操作
def start_copy():
    extensions = ('.jpg', '.jpeg','.png','.docx','.doc','.xls') # 指定需要拷贝的文件类型
    files = find_files_with_extensions(app.source_disk.get(), extensions) # 获取符合条件的文件列表
    copy_files_to_directory(files, app.target_dir.get(), extensions) # 将文件拷贝到目标目录中
    messagebox.showinfo("完成", "文件拷贝已完成！") # 弹出消息框通知用户
class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("文件工具箱")
        self.geometry("400x400")

        self.source_disk = tk.StringVar()
        self.target_dir = tk.StringVar()

        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        part1_frame = tk.LabelFrame(main_frame, text="文件去重工具")
        part1_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=10)

        directory_label = tk.Label(part1_frame, text="目录路径：")
        directory_label.pack(side=tk.LEFT, padx=5)

        directory_entry = tk.Entry(part1_frame)
        directory_entry.pack(fill=tk.X, expand=True, padx=5)

        browse_button = tk.Button(part1_frame, text="选择目录", command=lambda: browse_button_callback(directory_entry, text_widget))
        browse_button.pack(side=tk.LEFT, padx=5)

        start_button = tk.Button(part1_frame, text="开始", command=lambda: start_button_callback(directory_entry, text_widget))
        start_button.pack(side=tk.LEFT, padx=5)

        part2_frame = tk.LabelFrame(main_frame, text="文件拷贝整理")
        part2_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=10)

        tk.Label(part2_frame, text="源磁盘：").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(part2_frame, textvariable=self.source_disk).grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        tk.Button(part2_frame, text="浏览", command=browse_disk).grid(row=0, column=2, padx=10, pady=10)

        tk.Label(part2_frame, text="目标目录：").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(part2_frame, textvariable=self.target_dir).grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        tk.Button(part2_frame, text="浏览", command=browse_target).grid(row=1, column=2, padx=10, pady=10)
        tk.Button(part2_frame, text="开始拷贝", command=start_copy_thread).grid(row=2, columnspan=3, pady=20)

        part2_frame.columnconfigure(1, weight=1)

        text_widget = tk.Text(main_frame, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(main_frame, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)

if __name__ == "__main__":
    app = Application()
    app.mainloop()

