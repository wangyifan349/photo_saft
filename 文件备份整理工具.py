import os,re
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

class FileCopierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件整理工具")
        
        # 自适应屏幕宽度
        screen_width = self.root.winfo_screenwidth()
        window_width = screen_width // 2
        self.root.geometry(f"{window_width}x200")

        # 配置界面布局
        self.setup_widgets()

    def setup_widgets(self):
        # 源目录
        self.src_label = tk.Label(self.root, text="源目录:")
        self.src_label.pack(fill='x', padx=5, pady=5)
        self.src_entry = tk.Entry(self.root)
        self.src_entry.pack(fill='x', padx=5, pady=5)
        self.src_button = tk.Button(self.root, text="选择", command=self.select_source)
        self.src_button.pack(padx=5, pady=5)

        # 目标目录
        self.dst_label = tk.Label(self.root, text="目标目录:")
        self.dst_label.pack(fill='x', padx=5, pady=5)
        self.dst_entry = tk.Entry(self.root)
        self.dst_entry.pack(fill='x', padx=5, pady=5)
        self.dst_button = tk.Button(self.root, text="选择", command=self.select_destination)
        self.dst_button.pack(padx=5, pady=5)

        # 文件扩展名
        self.ext_label = tk.Label(self.root, text="文件扩展名(用逗号分隔):")
        self.ext_label.pack(fill='x', padx=5, pady=5)
        self.ext_entry = tk.Entry(self.root)
        self.ext_entry.pack(fill='x', padx=5, pady=5)
        #默认填充一些数据
        self.ext_entry.insert(0, ".docx, .dot")

        # 开始按钮
        self.start_button = tk.Button(self.root, text="开始复制", command=self.start_copy_thread)
        self.start_button.pack(pady=20)

    def select_source(self):
        directory = filedialog.askdirectory()
        self.src_entry.delete(0, tk.END)
        self.src_entry.insert(0, directory)

    def select_destination(self):
        directory = filedialog.askdirectory()
        self.dst_entry.delete(0, tk.END)
        self.dst_entry.insert(0, directory)

    def start_copy_thread(self):
        src_dir = self.src_entry.get()
        dst_dir = self.dst_entry.get()
        # 使用正则表达式分割英文和中文逗号
        extensions = re.split(r'[，,]\s*', self.ext_entry.get())
        #extensions = [ext.strip() for ext in extensions if ext.strip()]

        
        cleaned_extensions = []  # 初始化一个空列表，用于存储处理后的扩展名

        for ext in extensions:  # 遍历原始列表中的每个元素
            stripped_ext = ext.strip()  # 去除字符串两端的空白字符
            if stripped_ext:  # 检查去除空白后的字符串是否不为空
                cleaned_extensions.append(stripped_ext)  # 如果字符串非空，就将其添加到列表中



        
        # 检查输入有效性
        if not os.path.isdir(src_dir) or not os.path.isdir(dst_dir):
            messagebox.showerror("错误", "源目录或目标目录无效。")
            return
        if not extensions:
            messagebox.showerror("错误", "请输入至少一个文件扩展名。")
            return
        
        # 在独立线程中开始复制过程
        threading.Thread(target=self.copy_files, args=(src_dir, dst_dir, extensions), daemon=True).start()

    def get_unique_filename(self, file_path):
        """
        如果目标路径中已存在文件，则生成一个唯一的文件名。
        """
        original_path = file_path
        counter = 1
        while os.path.exists(file_path):
            # 分离文件名和扩展名
            file_dir, file_fullname = os.path.split(original_path)
            file_name, file_ext = os.path.splitext(file_fullname)
            # 添加计数器到文件名
            file_path = os.path.join(file_dir, f"{file_name}_{counter}{file_ext}")
            counter += 1
        return file_path
    
    def copy_files(self, src_dir, dst_dir, extensions):
        try:
            for root, dirs, files in os.walk(src_dir):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in extensions):
                        src_file_path = os.path.join(root, file)
                        dst_file_path = os.path.join(dst_dir, file)
                        # 检查目标目录中是否存在同名文件
                        dst_file_path = self.get_unique_filename(dst_file_path)
                        shutil.copy2(src_file_path, dst_file_path)
            messagebox.showinfo("完成", "文件复制完成！")
        except Exception as e:
            messagebox.showerror("错误", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = FileCopierApp(root)
    root.mainloop()
