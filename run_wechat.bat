@echo off
echo 正在检查并安装必要的库...
pip install itchat-uos
echo.
echo 开始运行微信消息定时发送程序...
python wechat_scheduler.py
echo.
pause
