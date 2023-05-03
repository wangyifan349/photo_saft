import os,shutil,threading
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import tkinter.messagebox as messagebox

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

        self.title("文件拷贝工具")
        self.geometry("400x200")

        self.source_disk = tk.StringVar()
        self.target_dir = tk.StringVar()

        tk.Label(self, text="源磁盘：").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(self, textvariable=self.source_disk).grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        tk.Button(self, text="浏览", command=browse_disk).grid(row=0, column=2, padx=10, pady=10)

        tk.Label(self, text="目标目录：").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(self, textvariable=self.target_dir).grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        tk.Button(self, text="浏览", command=browse_target).grid(row=1, column=2, padx=10, pady=10)

        # 将“开始拷贝”使用线程完成
        tk.Button(self, text="开始拷贝", command=start_copy_thread).grid(row=2, columnspan=3, pady=20)

        self.columnconfigure(1, weight=1)
if __name__ == "__main__":
    app = Application()
    app.mainloop()
