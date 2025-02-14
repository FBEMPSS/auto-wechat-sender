import time
from datetime import datetime
import win32gui
import win32con
import win32clipboard
import win32api  # 添加这个导入
import win32com.client  # 添加这个导入
import logging
import pyautogui
import ctypes
from ctypes import wintypes
import argparse
from tqdm import tqdm

# 配置日志显示毫秒
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s.%(msecs)03d - %(message)s', 
                   datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# 初始化Windows高精度计时器
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
QueryPerformanceCounter = kernel32.QueryPerformanceCounter
QueryPerformanceFrequency = kernel32.QueryPerformanceFrequency

def get_precise_time():
    """获取高精度时间戳"""
    counter = wintypes.LARGE_INTEGER()
    freq = wintypes.LARGE_INTEGER()
    QueryPerformanceCounter(ctypes.byref(counter))
    QueryPerformanceFrequency(ctypes.byref(freq))
    return counter.value / freq.value

def datetime_to_timestamp(dt):
    """将datetime转换为精确的时间戳"""
    return dt.timestamp()

def activate_search(hwnd):
    """激活微信搜索"""
    # 确保窗口在前台
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.2)
    
    # 使用微信的搜索快捷键 Ctrl+F
    win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl
    win32api.keybd_event(0x46, 0, 0, 0)  # F
    time.sleep(0.05)
    win32api.keybd_event(0x46, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.3)  # 等待搜索框打开
    return True

def set_clipboard_text(text):
    """设置剪贴板内容"""
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text)
    win32clipboard.CloseClipboard()

def search_and_select_friend(friend_name):
    """改进的好友搜索和选择函数"""
    try:
        hwnd = win32gui.FindWindow("WeChatMainWndForPC", None)
        if not hwnd:
            raise Exception("未找到微信窗口")

        # 确保窗口在前台
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.3)

        # 激活搜索框
        logger.info("激活搜索框...")
        win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl down
        win32api.keybd_event(0x46, 0, 0, 0)  # F down
        time.sleep(0.05)
        win32api.keybd_event(0x46, 0, win32con.KEYEVENTF_KEYUP, 0)  # F up
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl up
        time.sleep(0.3)

        # 通过剪贴板输入好友名称
        logger.info(f"搜索好友: {friend_name}")
        set_clipboard_text(friend_name)
        win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl down
        win32api.keybd_event(0x56, 0, 0, 0)  # V down
        time.sleep(0.05)
        win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)  # V up
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl up
        time.sleep(0.5)

        # 按回车选择第一个搜索结果
        win32api.keybd_event(0x0D, 0, 0, 0)  # Enter down
        win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)  # Enter up
        time.sleep(0.5)

        # 验证窗口状态
        if win32gui.GetForegroundWindow() != hwnd:
            raise Exception("聊天窗口未能正确打开")

        logger.info("成功打开聊天窗口")
        return hwnd

    except Exception as e:
        logger.error(f"搜索好友失败: {str(e)}")
        raise

def prepare_chat(friend_name):
    """准备聊天窗口"""
    for attempt in range(3):  # 最多尝试3次
        try:
            return search_and_select_friend(friend_name)
        except Exception as e:
            logger.warning(f"第 {attempt + 1} 次尝试失败: {str(e)}")
            time.sleep(0.5)
    raise Exception("无法打开聊天窗口，已重试3次")

def prepare_message(message):
    """提前准备消息到剪贴板"""
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(message)
    win32clipboard.CloseClipboard()

def precise_sleep_until(target_timestamp):
    """使用高精度计时器进行精确等待"""
    logger.info(f"当前时间: {datetime.now()}, 等待至: {datetime.fromtimestamp(target_timestamp)}")
    
    while True:
        current = time.time()
        if current >= target_timestamp:
            break
            
        remaining = target_timestamp - current
        if remaining > 1.0:
            # 如果剩余时间大于1秒，使用普通sleep
            time.sleep(0.9)  # 睡眠略少于剩余时间
        elif remaining > 0.001:
            # 如果剩余时间大于1毫秒，使用短暂sleep
            time.sleep(0.0009)
        else:
            # 最后1毫秒使用忙等待
            pass

def send_precise_message():
    """使用更可靠的方式发送消息"""
    try:
        # 确保发送窗口处于激活状态
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            raise Exception("无法获取当前窗口句柄")

        # 尝试发送消息，最多重试3次
        for attempt in range(3):
            try:
                # 模拟Ctrl+V
                win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl 按下
                win32api.keybd_event(0x56, 0, 0, 0)  # V 按下
                time.sleep(0.01)
                win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)  # V 释放
                win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl 释放
                time.sleep(0.05)

                # 发送回车
                win32api.keybd_event(0x0D, 0, 0, 0)  # Enter 按下
                win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)  # Enter 释放
                
                logger.info(f"消息发送成功 (尝试 {attempt + 1})")
                return True
            except Exception as e:
                logger.warning(f"发送失败，尝试次数 {attempt + 1}/3: {str(e)}")
                time.sleep(0.1)
                continue
        
        raise Exception("发送消息失败，已重试3次")
    except Exception as e:
        logger.error(f"发送消息时出错: {str(e)}")
        return False

def parse_datetime(datetime_str):
    """解析日期时间字符串"""
    try:
        return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise argparse.ArgumentTypeError('Invalid datetime format. Use YYYY-MM-DD HH:MM:SS')

def countdown_with_progressbar(target_timestamp, early_stop_seconds=3):
    """使用进度条显示倒计时"""
    current = time.time()
    total_wait = target_timestamp - current - early_stop_seconds
    
    if total_wait <= 0:
        return
    
    with tqdm(total=100, 
              desc="倒计时进度", 
              bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{remaining} 剩余]',
              ncols=80) as pbar:
        
        start_time = time.time()
        while time.time() < target_timestamp - early_stop_seconds:
            elapsed = time.time() - start_time
            progress = min(100, (elapsed / total_wait) * 100)
            
            # 更新进度条
            pbar.n = progress
            pbar.refresh()
            
            time.sleep(0.1)
        
        pbar.n = 100
        pbar.refresh()

def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='精确定时发送微信消息')
    parser.add_argument('friend_name', help='微信好友名称（备注名）')
    parser.add_argument('message', help='要发送的消息内容')
    parser.add_argument('target_time', type=parse_datetime, 
                       help='目标发送时间，格式：YYYY-MM-DD HH:MM:SS')
    
    args = parser.parse_args()
    
    try:
        logger.info(f"目标发送时间: {args.target_time}")
        logger.info(f"发送对象: {args.friend_name}")
        logger.info(f"发送内容: {args.message}")
        
        # 使用新的搜索函数
        hwnd = prepare_chat(args.friend_name)
        if not hwnd:
            raise Exception("无法打开聊天窗口")
            
        prepare_message(args.message)
        logger.info("窗口和消息准备完成")
        
        # 转换目标时间为时间戳
        target_timestamp = datetime_to_timestamp(args.target_time)
        
        # 使用新的进度条倒计时
        countdown_with_progressbar(target_timestamp)
        
        logger.info("进入精确等待模式...")
        precise_sleep_until(target_timestamp)
        
        # 确保窗口状态
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.05)
        
        # 发送消息并验证
        start_time = time.time()
        if not send_precise_message():
            logger.error("消息发送失败！")
            return
        end_time = time.time()
        
        logger.info(f"消息已发送，耗时: {(end_time - start_time)*1000:.3f}毫秒")
        
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()
