import os
import sys
import subprocess
import platform

def check_tkinter():
    try:
        import tkinter
        print("tkinter 已安装!")
        return True
    except ImportError:
        print("tkinter 未安装!")
        return False

def install_tkinter():
    system = platform.system().lower()
    if system == "windows":
        try:
            # 获取Python安装路径
            python_path = sys.executable
            python_dir = os.path.dirname(python_path)
            
            print("正在安装 tkinter...")
            # 使用 Python 安装程序修复安装
            command = f'start "" "{python_dir}/python.exe" -m pip install --upgrade pip'
            os.system(command)
            
            print("请按照以下步骤手动安装 tkinter：")
            print("1. 打开控制面板")
            print("2. 找到'程序和功能'")
            print("3. 找到 Python 安装")
            print("4. 选择'修改'")
            print("5. 在组件列表中确保选中 'tcl/tk and IDLE'")
            print("6. 完成安装")
            
            input("按回车键打开 Python 下载页面...")
            os.system('start https://www.python.org/downloads/')
            
        except Exception as e:
            print(f"安装过程出错: {str(e)}")
    else:
        if platform.system().lower() == "linux":
            print("在 Linux 上安装 tkinter：")
            print("Ubuntu/Debian: sudo apt-get install python3-tk")
            print("Fedora: sudo dnf install python3-tkinter")
            print("CentOS: sudo yum install python3-tkinter")
        else:
            print("在 macOS 上安装 tkinter：")
            print("brew install python-tk")

if __name__ == "__main__":
    if not check_tkinter():
        print("未检测到 tkinter，开始安装流程...")
        install_tkinter()
    else:
        # 检查 tkcalendar
        try:
            import tkcalendar
            print("tkcalendar 已安装!")
        except ImportError:
            print("正在安装 tkcalendar...")
            subprocess.run([sys.executable, "-m", "pip", "install", "tkcalendar"])
            print("tkcalendar 安装完成!")
