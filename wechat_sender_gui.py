import tkinter as tk
from tkinter import ttk, scrolledtext
from tkcalendar import DateEntry
import time
from datetime import datetime
import win32gui
import win32con
import win32clipboard
import win32api
import pyautogui  # 添加这个导入
import logging
from threading import Thread
import queue
import sys

# 检查并安装必要的依赖
def check_dependencies():
    required_packages = ['pyautogui', 'tkcalendar', 'pywin32']
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"正在安装 {package}...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package} 安装完成！")

# 在程序开始时检查依赖
check_dependencies()

# 导入之前实现的关键函数
def prepare_chat(friend_name):
    """准备聊天窗口"""
    try:
        hwnd = win32gui.FindWindow("WeChatMainWndForPC", None)
        if not hwnd:
            raise Exception("未找到微信窗口")
        
        # 确保窗口可见且处于前台
        if (win32gui.IsIconic(hwnd)):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(1.0)
        
        # 使用Ctrl+F打开搜索框
        logging.info("打开搜索框...")
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(1.0)
        
        # 直接使用剪贴板输入好友名称
        logging.info(f"输入好友名称: {friend_name}")
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(friend_name)
        win32clipboard.CloseClipboard()
        
        # 粘贴好友名称到搜索框
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1.0)  # 等待名称输入完成
        
        logging.info("等待搜索结果...")
        time.sleep(2.0)  # 等待搜索结果显示
        
        # 按回车选择搜索结果
        pyautogui.press('enter')
        time.sleep(1.0)
        
        # 修改验证逻辑
        # 检查是否找到并进入聊天窗口
        current_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        logging.info(f"当前窗口标题: {current_title}")
        
        # 只要窗口标题不是搜索框的标题就认为进入了聊天窗口
        if "搜索" in current_title:
            raise Exception("未能进入聊天窗口")
        
        logging.info("成功进入聊天窗口")
        
        # 点击输入框
        rect = win32gui.GetWindowRect(hwnd)
        input_x = rect[0] + (rect[2] - rect[0]) // 2
        input_y = rect[3] - 100
        pyautogui.click(input_x, input_y)
        time.sleep(0.5)
        
        return hwnd
        
    except Exception as e:
        logging.error(f"准备聊天窗口失败: {str(e)}")
        raise

def is_chat_window_active(hwnd):
    """检查是否成功进入聊天窗口"""
    try:
        # 获取当前窗口标题
        title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        # 检查窗口标题是否包含微信相关文字
        return "微信" in title and hwnd == win32gui.GetForegroundWindow()
    except:
        return False

def prepare_message(message):
    """准备发送的消息"""
    

    

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(message)
    win32clipboard.CloseClipboard()

def send_precise_message():
    """发送消息"""
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            raise Exception("无法获取窗口句柄")
        
        # 确保在输入框区域点击一下
        rect = win32gui.GetWindowRect(hwnd)
        input_x = rect[0] + (rect[2] - rect[0]) // 2
        input_y = rect[3] - 50
        pyautogui.click(input_x, input_y)
        time.sleep(0.1)
        
        # Ctrl+V粘贴消息
        win32api.keybd_event(0x11, 0, 0, 0)
        win32api.keybd_event(0x56, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        
        # 发送回车
        win32api.keybd_event(0x0D, 0, 0, 0)
        win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)
        return True
        
    except Exception as e:
        logging.error(f"发送消息失败: {str(e)}")
        return False

def datetime_to_timestamp(dt):
    """转换datetime为时间戳"""
    return dt.timestamp()

class WeChatSenderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("微信定时发送助手")
        self.root.geometry("600x500")
        self.message_queue = queue.Queue()
        self.setup_logging()
        self.create_widgets()
        self.running = False
        self.paused = False  # 添加暂停状态标志
        
    def setup_logging(self):
        """设置日志处理"""
        class QueueHandler(logging.Handler):
            def __init__(self, queue):
                super().__init__()
                self.queue = queue

            def emit(self, record):
                self.queue.put(self.format(record))

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        queue_handler = QueueHandler(self.message_queue)
        queue_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logger.addHandler(queue_handler)
        
    def create_widgets(self):
        """创建GUI组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 输入区域
        ttk.Label(main_frame, text="好友名称:").grid(row=0, column=0, sticky=tk.W)
        self.friend_name = ttk.Entry(main_frame, width=40)
        self.friend_name.grid(row=0, column=1, columnspan=2, pady=5)
        
        ttk.Label(main_frame, text="发送内容:").grid(row=1, column=0, sticky=tk.W)
        self.message = ttk.Entry(main_frame, width=40)
        self.message.grid(row=1, column=1, columnspan=2, pady=5)
        
        # 时间选择
        ttk.Label(main_frame, text="发送日期:").grid(row=2, column=0, sticky=tk.W)
        self.date_picker = DateEntry(main_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2)
        self.date_picker.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 时间输入框
        ttk.Label(main_frame, text="发送时间:").grid(row=3, column=0, sticky=tk.W)
        time_frame = ttk.Frame(main_frame)
        time_frame.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        self.hour_var = tk.StringVar(value="00")
        self.minute_var = tk.StringVar(value="00")
        self.second_var = tk.StringVar(value="00")
        
        # 时分秒输入
        self.hour_entry = ttk.Entry(time_frame, textvariable=self.hour_var, width=2)
        self.hour_entry.pack(side=tk.LEFT)
        ttk.Label(time_frame, text=":").pack(side=tk.LEFT)
        self.minute_entry = ttk.Entry(time_frame, textvariable=self.minute_var, width=2)
        self.minute_entry.pack(side=tk.LEFT)
        ttk.Label(time_frame, text=":").pack(side=tk.LEFT)
        self.second_entry = ttk.Entry(time_frame, textvariable=self.second_var, width=2)
        self.second_entry.pack(side=tk.LEFT)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        # 开始按钮
        self.start_button = ttk.Button(button_frame, text="开始任务", command=self.start_task)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # 暂停按钮
        self.pause_button = ttk.Button(button_frame, text="暂停任务", command=self.pause_task, state='disabled')
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.progress.grid(row=5, column=0, columnspan=3, pady=5)
        
        # 日志显示区域
        self.log_area = scrolledtext.ScrolledText(main_frame, width=60, height=15)
        self.log_area.grid(row=6, column=0, columnspan=3, pady=5)
        
        # 开始更新日志显示
        self.update_log_display()
    
    def get_target_datetime(self):
        """获取用户选择的目标时间"""
        selected_date = self.date_picker.get_date()
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            second = int(self.second_var.get())
            
            if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
                raise ValueError("时间格式无效")
                
            return datetime.combine(selected_date, 
                                 datetime.strptime(f"{hour}:{minute}:{second}", 
                                                 "%H:%M:%S").time())
        except ValueError as e:
            raise ValueError("请输入有效的时间格式 (时:分:秒)")
    
    def start_task(self):
        """开始发送任务"""
        if self.running:
            return
            
        try:
            target_time = self.get_target_datetime()
            if target_time <= datetime.now():
                logging.error("目标时间必须在当前时间之后")
                return
                
            self.running = True
            self.paused = False
            self.start_button.config(state='disabled')
            self.pause_button.config(state='normal')
            
            # 获取输入
            friend_name = self.friend_name.get()
            message = self.message.get()
            
            # 在新线程中运行任务
            Thread(target=self.run_task, 
                  args=(friend_name, message, target_time), 
                  daemon=True).start()
                  
        except Exception as e:
            logging.error(f"启动任务失败: {str(e)}")
            self.running = False
            self.start_button.config(state='normal')
            self.pause_button.config(state='disabled')
    
    def pause_task(self):
        """暂停或恢复任务"""
        if not self.running:
            return
            
        self.paused = not self.paused
        if self.paused:
            self.pause_button.config(text="继续任务")
            logging.info("任务已暂停")
        else:
            self.pause_button.config(text="暂停任务")
            logging.info("任务已继续")
        
    def update_log_display(self):
        """更新日志显示"""
        while True:
            try:
                message = self.message_queue.get_nowait()
                self.log_area.insert(tk.END, message + '\n')
                self.log_area.see(tk.END)
            except queue.Empty:
                break
        self.root.after(100, self.update_log_display)
        
    def run_task(self, friend_name, message, target_time):
        """运行发送任务"""
        try:
            logging.info(f"准备发送消息给: {friend_name}")
            logging.info(f"发送内容: {message}")
            logging.info(f"目标时间: {target_time}")
            
            # 准备聊天窗口
            hwnd = prepare_chat(friend_name)
            prepare_message(message)
            
            # 等待发送时间
            target_timestamp = datetime_to_timestamp(target_time)
            self.countdown(target_timestamp)
            
            # 如果是暂停状态，不发送消息
            if not self.paused and self.running:
                # 发送消息
                if send_precise_message():
                    logging.info("消息发送成功！")
                else:
                    logging.error("消息发送失败！")
                
        except Exception as e:
            logging.error(f"发生错误: {str(e)}")
        finally:
            self.running = False
            self.paused = False
            self.root.after(0, lambda: self.start_button.config(state='normal'))
            self.root.after(0, lambda: self.pause_button.config(state='disabled', text="暂停任务"))
            
    def countdown(self, target_timestamp):
        """倒计时并更新进度条"""
        start_time = time.time()
        elapsed_time = 0
        total_wait = target_timestamp - start_time
        
        while time.time() < target_timestamp:
            if not self.running:
                break
                
            if self.paused:
                # 暂停时更新起始时间和总等待时间
                start_time = time.time() - elapsed_time
                total_wait = target_timestamp - start_time
                time.sleep(0.1)
                continue
                
            elapsed_time = time.time() - start_time
            progress = min(100, (elapsed_time / total_wait) * 100)
            self.root.after(0, lambda p=progress: self.progress.configure(value=p))
            time.sleep(0.1)

def main():
    root = tk.Tk()
    app = WeChatSenderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    # 添加当前目录到系统路径
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    main()
