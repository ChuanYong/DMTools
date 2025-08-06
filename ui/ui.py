import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from functions.renameFunc import refresh_file_list, batch_rename
from functions.unzipFunc import browse_zip_file, browse_unzip_folder, start_unzip

class FileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件批量处理工具")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # 变量初始化
        self.folder_path = tk.StringVar()
        self.prefix_text = tk.StringVar(value="2025_")
        self.file_list = []
        self.zip_file_path = tk.StringVar()
        self.unzip_folder_path = tk.StringVar()
        self.progress_var = tk.DoubleVar()  # 用于进度条
        
        # 设置中文字体支持
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TEntry", font=("SimHei", 10))
        
        # 创建界面
        self.create_widgets()
    
    def create_widgets(self):
        # 创建标签页
        tab_control = ttk.Notebook(self.root)
        
        # 重命名标签页
        self.rename_tab = ttk.Frame(tab_control)
        tab_control.add(self.rename_tab, text="批量重命名")
        
        # 解压缩标签页
        self.unzip_tab = ttk.Frame(tab_control)
        tab_control.add(self.unzip_tab, text="解压缩文件")
        
        tab_control.pack(expand=1, fill="both")
        
        # 重命名标签页内容
        self.create_rename_tab()
        
        # 解压缩标签页内容
        self.create_unzip_tab()
    
    def create_rename_tab(self):
        # 文件夹选择区域
        folder_frame = ttk.Frame(self.rename_tab, padding="10")
        folder_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(folder_frame, text="目标文件夹:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(folder_frame, text="浏览...", command=self.browse_folder).pack(side=tk.LEFT, padx=5)
        
        # 前缀设置区域
        prefix_frame = ttk.Frame(self.rename_tab, padding="10")
        prefix_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(prefix_frame, text="重命名前缀:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(prefix_frame, textvariable=self.prefix_text, width=20).pack(side=tk.LEFT, padx=5)
        
        # 文件列表区域
        list_frame = ttk.Frame(self.rename_tab, padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(list_frame, text="文件列表:").pack(anchor=tk.W, padx=5)
        
        # 创建滚动条和列表框
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("SimHei", 10))
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=5)
        
        scrollbar.config(command=self.file_listbox.yview)
        
        # 按钮区域
        button_frame = ttk.Frame(self.rename_tab, padding="10")
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="刷新文件列表", command=self.refresh_file_list).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="批量重命名", command=self.batch_rename).pack(side=tk.RIGHT, padx=10)
    
    def create_unzip_tab(self):
        # 压缩文件选择区域
        zip_file_frame = ttk.Frame(self.unzip_tab, padding="10")
        zip_file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(zip_file_frame, text="压缩文件:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(zip_file_frame, textvariable=self.zip_file_path, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(zip_file_frame, text="浏览...", command=self.browse_zip_file).pack(side=tk.LEFT, padx=5)
        
        # 解压目标文件夹区域
        unzip_folder_frame = ttk.Frame(self.unzip_tab, padding="10")
        unzip_folder_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(unzip_folder_frame, text="解压到:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(unzip_folder_frame, textvariable=self.unzip_folder_path, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(unzip_folder_frame, text="浏览...", command=self.browse_unzip_folder).pack(side=tk.LEFT, padx=5)
        
        # 进度条区域
        progress_frame = ttk.Frame(self.unzip_tab, padding="10")
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5)
        
        self.progress_label = ttk.Label(progress_frame, text="准备就绪")
        self.progress_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # 解压按钮区域
        unzip_button_frame = ttk.Frame(self.unzip_tab, padding="10")
        unzip_button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(unzip_button_frame, text="开始解压", command=self.start_unzip).pack(side=tk.RIGHT, padx=10)
        
        # 支持格式说明
        from functions.unzipFunc import support_7z
        support_note = "支持格式: ZIP"
        if support_7z:
            support_note += ", 7Z"
        else:
            support_note += " (7Z格式需要安装py7zr库: pip install py7zr)"
        
        ttk.Label(self.unzip_tab, text=support_note, foreground="gray").pack(side=tk.BOTTOM, pady=10)
    
    # 重命名相关回调方法
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.refresh_file_list()
    
    def refresh_file_list(self):
        refresh_file_list(
            self.folder_path.get(), 
            self.file_listbox, 
            self.file_list
        )
    
    def batch_rename(self):
        batch_rename(
            self.folder_path.get(),
            self.prefix_text.get(),
            self.file_list,
            self.refresh_file_list
        )
    
    # 解压缩相关回调方法
    def browse_zip_file(self):
        browse_zip_file(self.zip_file_path, self.unzip_folder_path)
    
    def browse_unzip_folder(self):
        browse_unzip_folder(self.unzip_folder_path)
    
    def start_unzip(self):
        start_unzip(
            self.zip_file_path.get(),
            self.unzip_folder_path.get(),
            self.update_progress,
            self.root
        )
    
    def update_progress(self, value, message):
        """更新进度条和状态文本"""
        self.progress_var.set(value)
        self.progress_label.config(text=message)
        self.root.update_idletasks()  # 刷新界面

def create_main_window(root):
    """创建主窗口并返回应用实例"""
    return FileManagerApp(root)
