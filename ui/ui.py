import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
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

        # 一键解压缩标签页
        self.batch_unzip_tab = ttk.Frame(tab_control)
        tab_control.add(self.batch_unzip_tab, text="一键解压缩")

        tab_control.pack(expand=1, fill="both")
        
        # 重命名标签页内容
        self.create_rename_tab()
        
        # 解压缩标签页内容
        self.create_unzip_tab()

        # 一键解压缩标签页内容
        self.create_batch_unzip_tab()
    
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
    
    def create_batch_unzip_tab(self):
        # 源文件夹选择区域
        source_frame = ttk.Frame(self.batch_unzip_tab, padding="10")
        source_frame.pack(fill=tk.X, padx=10, pady=5)

        # 源文件夹选择和按钮区域
        source_frame = ttk.Frame(self.batch_unzip_tab, padding="10")
        source_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(source_frame, text="源文件夹:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.batch_source_folder = tk.StringVar()
        ttk.Entry(source_frame, textvariable=self.batch_source_folder, width=50).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        source_frame.grid_columnconfigure(1, weight=1)
        ttk.Button(source_frame, text="浏览...", command=self.browse_batch_source_folder).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(source_frame, text="开始批量解压", command=self.start_batch_unzip).grid(row=1, column=2, padx=5, pady=5, sticky=tk.E)

        # 状态区域 - 分为左右两栏
        status_frame = ttk.Frame(self.batch_unzip_tab, padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 左侧：压缩包文件列表
        left_frame = ttk.LabelFrame(status_frame, text="压缩包文件列表", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 列表框和滚动条
        self.batch_file_listbox = tk.Listbox(left_frame, font=('SimHei', 10), selectmode=tk.EXTENDED)
        self.batch_file_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 移除按钮
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(button_frame, text="移除选中文件", command=self.remove_selected_files).pack(side=tk.RIGHT)
        file_scrollbar = ttk.Scrollbar(self.batch_file_listbox, command=self.batch_file_listbox.yview)
        file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.batch_file_listbox.config(yscrollcommand=file_scrollbar.set)

        # 右侧：状态信息
        right_frame = ttk.LabelFrame(status_frame, text="解压状态", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.batch_status_text = tk.Text(right_frame, width=40, font=('SimHei', 10))
        self.batch_status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        status_scrollbar = ttk.Scrollbar(self.batch_status_text, command=self.batch_status_text.yview)
        status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.batch_status_text.config(yscrollcommand=status_scrollbar.set)

        # 进度条区域 - 放在最底部
        progress_frame = ttk.Frame(self.batch_unzip_tab, padding="10")
        progress_frame.pack(fill=tk.X, padx=10, pady=5)

        self.batch_progress_var = tk.DoubleVar()
        self.batch_progress_bar = ttk.Progressbar(progress_frame, variable=self.batch_progress_var, maximum=100)
        self.batch_progress_bar.pack(fill=tk.X, padx=5)

        self.batch_progress_label = ttk.Label(progress_frame, text="准备就绪")
        self.batch_progress_label.pack(anchor=tk.W, padx=5, pady=5)

        # 支持格式说明
        from functions.unzipFunc import support_7z, support_rar
        support_note = "支持格式: ZIP"
        if support_7z:
            support_note += ", 7Z"
        else:
            support_note += " (7Z格式需要安装py7zr库: pip install py7zr)"
        if support_rar:
            support_note += ", RAR"
        else:
            support_note += " (RAR格式需要安装rarfile库: pip install rarfile)"

        ttk.Label(self.batch_unzip_tab, text=support_note, foreground="gray").pack(side=tk.BOTTOM, pady=10)

    def browse_batch_source_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.batch_source_folder.set(folder)
            self.batch_status_text.insert(tk.END, f"已选择源文件夹: {folder}\n")
            
            # 清空列表框
            self.batch_file_listbox.delete(0, tk.END)
            
            # 扫描目录中的压缩文件
            from functions.unzipFunc import support_7z, support_rar
            supported_extensions = ['.zip']
            if support_7z:
                supported_extensions.append('.7z')
            if support_rar:
                supported_extensions.append('.rar')
            
            try:
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    if os.path.isfile(file_path):
                        _, ext = os.path.splitext(filename.lower())
                        if ext in supported_extensions:
                            self.batch_file_listbox.insert(tk.END, filename)
                
                file_count = self.batch_file_listbox.size()
                self.batch_status_text.insert(tk.END, f"找到 {file_count} 个支持的压缩文件\n")
            except Exception as e:
                self.batch_status_text.insert(tk.END, f"扫描文件出错: {str(e)}\n")

    def remove_selected_files(self):
        # 获取选中的项
        selected_indices = self.batch_file_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("提示", "请先选择要移除的文件")
            return

        # 从后往前删除，避免索引变化问题
        for i in sorted(selected_indices, reverse=True):
            self.batch_file_listbox.delete(i)

        self.batch_status_text.insert(tk.END, f"已移除 {len(selected_indices)} 个选中的文件\n")

    def start_batch_unzip(self):
        from functions.unzipFunc import batch_unzip
        source_folder = self.batch_source_folder.get()
        if not source_folder:
            messagebox.showwarning("警告", "请选择源文件夹")
            return

        # 获取列表框中的所有文件
        file_count = self.batch_file_listbox.size()
        if file_count == 0:
            messagebox.showwarning("警告", "没有找到可解压的文件")
            return

        selected_files = [self.batch_file_listbox.get(i) for i in range(file_count)]

        self.batch_status_text.insert(tk.END, f"开始批量解压 {file_count} 个文件...\n")
        self.batch_progress_var.set(0)
        self.batch_progress_label.config(text="准备中...")

        # 启动后台线程执行批量解压
        thread = threading.Thread(
            target=batch_unzip,
            args=(source_folder, self.update_batch_progress, self.append_batch_status, selected_files),
            daemon=True
        )
        thread.start()

    def update_batch_progress(self, value, message):
        """更新批量解压进度条和状态文本"""
        self.root.after(0, lambda: self._update_batch_progress(value, message))

    def _update_batch_progress(self, value, message):
        self.batch_progress_var.set(value)
        self.batch_progress_label.config(text=message)
        self.root.update_idletasks()

    def append_batch_status(self, message):
        """追加状态信息"""
        self.root.after(0, lambda: self._append_batch_status(message))

    def _append_batch_status(self, message):
        self.batch_status_text.insert(tk.END, message + "\n")
        self.batch_status_text.see(tk.END)  # 滚动到最后一行

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
