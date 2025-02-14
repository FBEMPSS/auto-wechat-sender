import itchat
from datetime import datetime
import time
import win32gui
import win32con
import win32clipboard
import win32api
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# 设置登录状态保存路径
HOT_RELOAD_FILE = os.path.join(os.path.expanduser("~"), "Documents", "code", "itchat.pkl")

def send_keys(hwnd, message):
    # 将消息写入剪贴板
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(message)
    win32clipboard.CloseClipboard()
    
    # 发送Ctrl+V和回车
    win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_CONTROL, 0)
    win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN, ord('V'), 0)
    win32gui.SendMessage(hwnd, win32con.WM_KEYUP, ord('V'), 0)
    win32gui.SendMessage(hwnd, win32con.WM_KEYUP, win32con.VK_CONTROL, 0)
    time.sleep(0.01)  # 小延迟确保粘贴完成
    win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    win32gui.SendMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)

def precise_sleep(target_time):
    while True:
        now = datetime.now()
        if now >= target_time:
            break
        remaining = (target_time - now).total_seconds()
        if remaining > 0.1:
            time.sleep(remaining - 0.1)
        else:
            # 使用忙等待进行最后的精确控制
            pass

def main():
    # 目标时间：2025年2月15日12:00:00
    target_time = datetime(2025, 2, 15, 12, 0, 0)
    message = "抢号"  # 你要发送的消息

    # 使用新的登录方式
    logger.info("正在检查登录状态...")
    itchat.auto_login(hotReload=True, 
                     statusStorageDir=HOT_RELOAD_FILE,
                     enableCmdQR=2,
                     loginCallback=lambda: logger.info("登录成功！"),
                     exitCallback=lambda: logger.info("已退出登录"))
    
    # 验证登录状态
    if not itchat.check_login():
        logger.error("登录失败，请重试！")
        return

    # 提前获取好友信息
    friend = itchat.search_friends(remarkName='陈文武')[0]
    
    # 提前发送一条测试消息以打开聊天窗口
    itchat.send("测试消息", friend['UserName'])
    logger.info("已发送测试消息，请确保微信窗口保持打开和活动状态")
    
    # 等待直到目标时间前5秒
    while (target_time - datetime.now()).total_seconds() > 5:
        time.sleep(0.5)
    
    logger.info("开始精确等待...")
    precise_sleep(target_time)
    
    # 查找微信窗口
    hwnd = win32gui.FindWindow("WeChatMainWndForPC", None)
    if hwnd:
        # 发送消息
        send_keys(hwnd, message)
        logger.info(f"消息已发送，时间：{datetime.now()}")
    else:
        logger.error("未找到微信窗口！")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")
    finally:
        if itchat.check_login():
            itchat.logout()
