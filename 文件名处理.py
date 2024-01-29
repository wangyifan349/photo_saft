import os
import hashlib
import sqlite3
import threading
from tkinter import Tk, Label, Entry, Button, Text, END, messagebox, filedialog

# 配置
salt = 'your_salt_here'  # 加盐
db_path = 'file_hashes.db'  # SQLite数据库文件路径

# 创建SQLite数据库和表
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS file_hashes (
    original_name TEXT,
    hashed_name TEXT
)
''')
conn.commit()
conn.close()

# 计算文件名的SHA512哈希值（加盐）
def hash_filename(filename, salt):
    hasher = hashlib.sha512()
    hasher.update(salt.encode('utf-8'))
    hasher.update(filename.encode('utf-8'))
    return hasher.hexdigest()

# 批量重命名文件
def batch_rename(directory, salt):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            hashed_name = hash_filename(filename, salt)
            new_file_path = os.path.join(root, hashed_name)
            os.rename(file_path, new_file_path)
            cursor.execute('INSERT INTO file_hashes (original_name, hashed_name) VALUES (?, ?)', (filename, hashed_name))
            conn.commit()
    conn.close()
    messagebox.showinfo("完成", "文件重命名和数据库更新完成。")

# 恢复文件名
def restore_filenames(directory):
    # 连接到 SQLite 数据库，数据库路径由 `db_path` 变量提供
    conn = sqlite3.connect(db_path)
    # 创建一个游标对象，用于执行 SQL 命令
    cursor = conn.cursor()
    # 执行 SQL 查询，选取所有包含原始文件名和哈希过的文件名的记录
    cursor.execute('SELECT original_name, hashed_name FROM file_hashes')
    # 获取所有查询结果
    rows = cursor.fetchall()
    # 遍历每一行查询结果
    for row in rows:
        # 分别获取原始文件名和哈希过的文件名
        original_name, hashed_name = row
        # os.walk 遍历指定目录及其子目录
        for root, dirs, files in os.walk(directory):
            # 检查当前目录中是否有匹配的哈希文件名
            if hashed_name in files:
                # 拼接获取完整的哈希文件路径
                hashed_file_path = os.path.join(root, hashed_name)
                # 拼接获取应恢复的原始文件路径
                original_file_path = os.path.join(root, original_name)
                # 重命名文件，从哈希文件名改回原始文件名
                os.rename(hashed_file_path, original_file_path)
                # 找到文件后跳出内层循环，继续查找下一个文件
                break
    # 关闭数据库连接
    conn.close()
    # 弹出消息框，通知用户文件恢复完成
    messagebox.showinfo("完成", "文件恢复完成。")


# 搜索文件名
def search_filename():
    # 获取搜索框中的内容，并将其转换为小写
    search_keyword = entry_search.get().lower()
    # 连接到SQLite数据库
    conn = sqlite3.connect(db_path)
    # 创建游标对象以执行SQL命令
    cursor = conn.cursor()
    # 执行SQL查询，搜索包含关键字的文件名（不区分大小写）
    cursor.execute('SELECT original_name, hashed_name FROM file_hashes WHERE lower(original_name) LIKE ?', ('%' + search_keyword + '%',))
    # 获取查询结果中所有行
    rows = cursor.fetchall()
    # 关闭数据库连接
    conn.close()
    # 清空之前的搜索结果
    text_result.delete(1.0, END)
    # 如果查询结果不为空，即找到了包含关键字的文件
    if rows:
        # 遍历查询结果，将每个文件的原始文件名和对应的哈希值插入到结果显示区域
        for original_name, hashed_name in rows:
            text_result.insert(END, f"原始文件名: {original_name}\n")
            text_result.insert(END, f"对应的哈希值: {hashed_name}\n")
    else:
        # 如果没有找到包含关键字的文件，则弹出提示框通知用户
        messagebox.showinfo("结果", "没有找到包含关键字的文件。")

# 使用线程执行任务
def run_threaded(task, *args):
    threading.Thread(target=task, args=args).start()

# 选择文件夹路径
def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        entry_dir.delete(0, END)
        entry_dir.insert(END, directory)

# 创建GUI
root = Tk()
root.title("文件名哈希工具")

Label(root, text="文件夹路径:").grid(row=0, column=0, sticky="e")
entry_dir = Entry(root, width=50)
entry_dir.grid(row=0, column=1, padx=5, pady=5)
Button(root, text="选择", command=select_directory).grid(row=0, column=2, padx=5, pady=5)

Label(root, text="加盐值:").grid(row=1, column=0, sticky="e")
entry_salt = Entry(root, width=50)
entry_salt.grid(row=1, column=1, padx=5, pady=5)
entry_salt.insert(END, salt)

Button(root, text="批量重命名文件", command=lambda: run_threaded(batch_rename, entry_dir.get(), entry_salt.get())).grid(row=2, column=0, columnspan=3, pady=5)

Button(root, text="恢复文件名", command=lambda: run_threaded(restore_filenames, entry_dir.get())).grid(row=3, column=0, columnspan=3, pady=5)

Label(root, text="搜索文件名关键字:").grid(row=4, column=0, sticky="e")
entry_search = Entry(root, width=50)
entry_search.grid(row=4, column=1, padx=5, pady=5)

Button(root, text="搜索", command=search_filename).grid(row=5, column=0, columnspan=3, pady=5)

text_result = Text(root, height=10, width=50)
text_result.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

root.mainloop()
