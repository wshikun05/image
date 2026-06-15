import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import cv2
import os
import threading
from pathlib import Path

class ImageStitcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("自动全景图片拼接工具")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # 设置样式
        self.root.configure(bg='#f0f0f0')
        style = ttk.Style()
        style.theme_use('clam')
        
        self.selected_images = []
        self.stitched_image = None
        self.stitched_image_path = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置 UI 界面"""
        # 主容器
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🖼️ 自动全景图片拼接工具", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # ========== 左侧：控制面板 ==========
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10)
        
        # 按钮区域
        button_frame = ttk.LabelFrame(left_frame, text="操作", padding=10)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="📁 选择图片", command=self.select_images,
                  width=20).pack(pady=5)
        ttk.Button(button_frame, text="🗑️ 清除列表", command=self.clear_images,
                  width=20).pack(pady=5)
        ttk.Button(button_frame, text="🔗 开始拼接", command=self.start_stitching,
                  width=20).pack(pady=5)
        ttk.Button(button_frame, text="💾 保存结果", command=self.save_result,
                  width=20).pack(pady=5)
        
        # 图片列表区域
        list_frame = ttk.LabelFrame(left_frame, text="已选择图片", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 列表框
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.image_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                        width=30, height=15)
        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.image_listbox.yview)
        
        # ========== 右侧：预览和日志 ==========
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(right_frame, text="预览", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.preview_label = ttk.Label(preview_frame, background='#e0e0e0',
                                      text="拼接结果预览\n（选择图片后点击'开始拼接'）")
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # 进度条
        progress_frame = ttk.LabelFrame(right_frame, text="进度", padding=10)
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="就绪", foreground='green')
        self.status_label.pack()
        
        # 日志区域
        log_frame = ttk.LabelFrame(right_frame, text="日志信息", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=50,
                                                 state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def log_message(self, message):
        """添加日志信息"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def select_images(self):
        """选择图片"""
        files = filedialog.askopenfilenames(
            title="选择要拼接的图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")]
        )
        
        if files:
            self.selected_images = list(files)
            self.update_image_list()
            self.log_message(f"✓ 已选择 {len(files)} 张图片")
    
    def update_image_list(self):
        """更新图片列表显示"""
        self.image_listbox.delete(0, tk.END)
        for i, img_path in enumerate(self.selected_images, 1):
            filename = os.path.basename(img_path)
            self.image_listbox.insert(tk.END, f"{i}. {filename}")
    
    def clear_images(self):
        """清除图片列表"""
        if messagebox.askyesno("确认", "确定要清除所有已选择的图片吗？"):
            self.selected_images = []
            self.image_listbox.delete(0, tk.END)
            self.log_message("已清除所有图片")
    
    def start_stitching(self):
        """开始拼接（在单独线程中运行）"""
        if not self.selected_images:
            messagebox.showwarning("警告", "请先选择至少2张图片")
            return
        
        if len(self.selected_images) < 2:
            messagebox.showwarning("警告", "至少需要2张图片才能拼接")
            return
        
        # 在单独线程中运行，避免 UI 冻结
        thread = threading.Thread(target=self._stitch_images_thread, daemon=True)
        thread.start()
    
    def _stitch_images_thread(self):
        """在线程中执行拼接"""
        try:
            self.status_label.config(text="正在拼接中...", foreground='orange')
            self.progress_var.set(0)
            self.root.update()
            
            self.log_message("\n" + "="*50)
            self.log_message("开始拼接过程...")
            self.log_message(f"图片数量: {len(self.selected_images)}")
            
            # 读取所有图片
            self.log_message("\n[步骤 1/4] 读取图片中...")
            images = []
            for i, path in enumerate(self.selected_images, 1):
                img = cv2.imread(path)
                if img is None:
                    self.log_message(f"✗ 无法读取: {os.path.basename(path)}")
                    return
                images.append(img)
                self.log_message(f"  ✓ 已读取: {os.path.basename(path)} "
                               f"({img.shape[1]}x{img.shape[0]})")
                self.progress_var.set(10 + i * 5)
                self.root.update()
            
            # 创建拼接器
            self.log_message("\n[步骤 2/4] 初始化拼接器...")
            stitcher = cv2.Stitcher_create()
            self.progress_var.set(40)
            self.root.update()
            
            # 执行拼接
            self.log_message("\n[步骤 3/4] 执行全景拼接（可能需要几秒钟）...")
            status, stitched = stitcher.stitch(images)
            
            self.progress_var.set(80)
            self.root.update()
            
            # 检查结果
            self.log_message("\n[步骤 4/4] 处理结果...")
            if status == cv2.Stitcher_OK:
                self.stitched_image = stitched
                self.log_message("✓ 拼接成功！")
                
                # 显示拼接结果
                self.show_preview(stitched)
                
                self.status_label.config(text="拼接成功！", foreground='green')
                self.log_message("="*50)
            else:
                error_messages = {
                    1: "需要更多图片或图片不够重叠",
                    2: "无法估计单应矩阵（图片特征不匹配）",
                    3: "相机参数调整失败"
                }
                error_msg = error_messages.get(status, f"未知错误 ({status})")
                self.log_message(f"✗ 拼接失败: {error_msg}")
                self.status_label.config(text="拼接失败", foreground='red')
                messagebox.showerror("拼接失败", 
                                    f"拼接过程出错:\n{error_msg}\n\n"
                                    "建议:\n"
                                    "1. 确保图片有足够的重叠（建议30-50%）\n"
                                    "2. 按照拍摄顺序排列图片\n"
                                    "3. 尝试使用更清晰的图片")
            
            self.progress_var.set(100)
            self.root.update()
            
        except Exception as e:
            self.log_message(f"✗ 发生错误: {str(e)}")
            self.status_label.config(text="发生错误", foreground='red')
            messagebox.showerror("错误", f"拼��过程中发生错误:\n{str(e)}")
    
    def show_preview(self, image):
        """显示拼接结果预览"""
        # 调整图片大小以适应预览窗口
        height, width = image.shape[:2]
        max_width, max_height = 450, 400
        
        if width > max_width or height > max_height:
            scale = min(max_width / width, max_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image_resized = cv2.resize(image, (new_width, new_height))
        else:
            image_resized = image
        
        # 转换为 PIL 图片
        image_rgb = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        # 转换为 PhotoImage
        photo = ImageTk.PhotoImage(pil_image)
        
        # 更新预览
        self.preview_label.config(image=photo, text="")
        self.preview_label.image = photo
    
    def save_result(self):
        """保存拼接结果"""
        if self.stitched_image is None:
            messagebox.showwarning("警告", "请先完成拼接")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG 图片", "*.jpg"), ("PNG 图片", "*.png"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                cv2.imwrite(file_path, self.stitched_image)
                self.stitched_image_path = file_path
                self.log_message(f"✓ 已保存到: {file_path}")
                messagebox.showinfo("成功", f"图片已保存到:\n{file_path}")
            except Exception as e:
                self.log_message(f"✗ 保存失败: {str(e)}")
                messagebox.showerror("错误", f"保存失败:\n{str(e)}")

def main():
    root = tk.Tk()
    app = ImageStitcherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
