import os
import zipfile
import threading
import os
from tkinter import filedialog, messagebox

# 尝试导入7z解压库，如果没有则只支持ZIP
try:
    import py7zr
    support_7z = True
except ImportError:
    support_7z = False
print(f"7z支持状态: {support_7z}")
# 尝试导入rar解压库，如果没有则不支持RAR
try:
    import rarfile
    support_rar = True
except ImportError:
    support_rar = False
print(f"rar支持状态: {support_rar}")

def browse_zip_file(zip_path_var, unzip_folder_var):
    """选择压缩文件"""
    # 支持的文件类型
    file_types = [("压缩文件", "*.zip")]
    if support_7z:
        file_types.append(("7Z压缩文件", "*.7z"))
    if support_rar:
        file_types.append(("RAR压缩文件", "*.rar"))
    
    file_path = filedialog.askopenfilename(
        title="选择压缩文件",
        filetypes=file_types
    )
    
    if file_path:
        zip_path_var.set(file_path)
        # 自动建议解压文件夹（与压缩文件同目录，同名文件夹）
        zip_dir = os.path.dirname(file_path)
        zip_name = os.path.splitext(os.path.basename(file_path))[0]
        unzip_folder_var.set(os.path.join(zip_dir, zip_name))

def browse_unzip_folder(unzip_folder_var):
    """选择解压目标文件夹"""
    folder = filedialog.askdirectory(title="选择解压目标文件夹")
    if folder:
        unzip_folder_var.set(folder)

def update_progress(root, progress_callback, value, message):
    """在主线程中更新进度"""
    root.after(0, lambda: progress_callback(value, message))

def perform_unzip(zip_path, unzip_path, progress_callback, root):
    """执行解压操作（在后台线程中运行）"""
    try:
        # 创建目标文件夹
        os.makedirs(unzip_path, exist_ok=True)
        
        # 根据文件扩展名判断压缩类型
        if zip_path.lower().endswith('.zip'):
            unzip_zip(zip_path, unzip_path, progress_callback, root)
        elif zip_path.lower().endswith('.7z') and support_7z:
            unzip_7z(zip_path, unzip_path, progress_callback, root)
        elif zip_path.lower().endswith('.rar') and support_rar:
            unzip_rar(zip_path, unzip_path, progress_callback, root)
        else:
            raise Exception("不支持的文件格式")
        
        # 解压完成
        update_progress(root, progress_callback, 100, "解压完成！")
        root.after(0, lambda: messagebox.showinfo("成功", f"文件已成功解压到:\n{unzip_path}"))
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("错误", f"解压失败: {str(e)}"))
    finally:
        # 恢复状态
        root.after(0, lambda: progress_callback(0, "准备就绪"))

def unzip_zip(zip_path, unzip_path, progress_callback, root):
    """解压ZIP文件"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        total_files = len(file_list)
        
        for i, file in enumerate(file_list):
            # 更新进度
            progress = (i + 1) / total_files * 100
            update_progress(root, progress_callback, progress, f"正在解压: {os.path.basename(file)}")
            
            # 解压文件
            zip_ref.extract(file, unzip_path)

def unzip_7z(zip_path, unzip_path, progress_callback, root):
    """解压7Z文件"""
    with py7zr.SevenZipFile(zip_path, mode='r') as z:
        file_list = z.getnames()
        total_files = len(file_list)
        
        for i, file in enumerate(file_list):
            # 更新进度
            progress = (i + 1) / total_files * 100
            update_progress(root, progress_callback, progress, f"正在解压: {os.path.basename(file)}")
        
        # 7z库解压
        z.extractall(unzip_path)

def unzip_rar(zip_path, unzip_path, progress_callback, root):
    """解压RAR文件"""
    with rarfile.RarFile(zip_path, 'r') as rar_ref:
        file_list = rar_ref.namelist()
        total_files = len(file_list)
        
        for i, file in enumerate(file_list):
            # 更新进度
            progress = (i + 1) / total_files * 100
            update_progress(root, progress_callback, progress, f"正在解压: {os.path.basename(file)}")
            
            # 解压文件
            rar_ref.extract(file, unzip_path)

def start_unzip(zip_path, unzip_path, progress_callback, root):
    """开始解压（启动后台线程）"""
    # 验证输入
    if not zip_path or not os.path.isfile(zip_path):
        messagebox.showwarning("警告", "请选择有效的压缩文件")
        return
    
    if not unzip_path:
        messagebox.showwarning("警告", "请选择解压目标文件夹")
        return
    
    # 检查文件格式
    if not (zip_path.lower().endswith('.zip') or 
            (zip_path.lower().endswith('.7z') and support_7z) or
            (zip_path.lower().endswith('.rar') and support_rar)):
        messagebox.showwarning("警告", "不支持的文件格式")
        return
    
    # 启动后台线程执行解压，避免界面卡顿
    progress_callback(0, "准备解压...")
    thread = threading.Thread(
        target=perform_unzip,
        args=(zip_path, unzip_path, progress_callback, root),
        daemon=True
    )
    thread.start()
