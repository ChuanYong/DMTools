import os
from tkinter import messagebox

def refresh_file_list(folder_path, listbox, file_list):
    """刷新文件列表"""
    if not folder_path or not os.path.isdir(folder_path):
        messagebox.showwarning("警告", "请先选择有效的文件夹")
        return
    
    # 清空列表
    listbox.delete(0, 'end')
    
    # 获取文件夹中的所有文件
    try:
        files = [f for f in os.listdir(folder_path) 
                if os.path.isfile(os.path.join(folder_path, f))]
        
        # 按创建时间排序
        files.sort(key=lambda x: os.path.getctime(os.path.join(folder_path, x)))
        
        # 清空并更新文件列表
        file_list.clear()
        file_list.extend(files)
        
        # 添加到列表框
        for file in files:
            listbox.insert('end', file)
            
        messagebox.showinfo("提示", f"已加载 {len(files)} 个文件")
    except Exception as e:
        messagebox.showerror("错误", f"加载文件失败: {str(e)}")

def batch_rename(folder_path, prefix, file_list, refresh_callback):
    """执行批量重命名操作"""
    if not folder_path or not os.path.isdir(folder_path):
        messagebox.showwarning("警告", "请先选择有效的文件夹")
        return
    
    if not prefix:
        messagebox.showwarning("警告", "请输入重命名前缀")
        return
    
    if not file_list:
        messagebox.showwarning("警告", "文件列表为空，请先刷新文件列表")
        return
    
    # 确认操作
    confirm = messagebox.askyesno("确认", f"确定要将 {len(file_list)} 个文件重命名为 '{prefix}1', '{prefix}2'... 吗？")
    if not confirm:
        return
    
    # 执行重命名
    success_count = 0
    fail_count = 0
    fail_files = []
    
    for i, filename in enumerate(file_list, 1):
        try:
            # 获取文件扩展名
            file_extension = os.path.splitext(filename)[1]
            
            # 构建新文件名
            new_filename = f"{prefix}{i}{file_extension}"
            
            # 构建完整路径
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_filename)
            
            # 避免文件名冲突
            if os.path.exists(new_path):
                raise Exception("新文件名已存在")
            
            # 执行重命名
            os.rename(old_path, new_path)
            success_count += 1
        except Exception as e:
            fail_count += 1
            fail_files.append(f"{filename}: {str(e)}")
    
    # 显示结果
    result_msg = f"重命名完成！\n成功: {success_count} 个文件\n失败: {fail_count} 个文件"
    if fail_files:
        result_msg += "\n\n失败详情:\n" + "\n".join(fail_files[:5])
        if len(fail_files) > 5:
            result_msg += f"\n... 还有 {len(fail_files)-5} 个失败文件"
    
    messagebox.showinfo("结果", result_msg)
    
    # 刷新文件列表
    refresh_callback()
