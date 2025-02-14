import itchat
import time
from datetime import datetime

# 使用UOS协议热登录
itchat.auto_login(hotReload=True, enableCmdQR=2)

def send_scheduled_message():
    # 设置目标时间（2月9日15:00:00）
    target_time = datetime(2025, 2, 14, 1, 31, 0)
    
    # 可以通过以下三种方式之一查找好友：
    # 1. 备注名
    friend = itchat.search_friends(remarkName='陈文武')
    # 2. 微信号
    # friend = itchat.search_friends(wechatAccount='微信号')
    # 3. 昵称
    # friend = itchat.search_friends(nickName='好友的昵称')
    
    if not friend:
        print("未找到好友，请确认：")
        print("1. 备注名是否正确（在你的通讯录中显示的名字）")
        print("2. 或者尝试使用对方的微信号（微信号不是昵称）")
        print("3. 或者使用对方的昵称（对方自己设置的名字）")
        return
    
    # 等待直到目标时间
    while datetime.now() < target_time:
        time.sleep(0.1)
    
    # 发送消息
    itchat.send_msg("你好", friend[0]['UserName'])
    print(f"消息已发送，时间：{datetime.now()}")

if __name__ == "__main__":
    try:
        send_scheduled_message()
    finally:
        itchat.logout()
