import os
import sys
import subprocess
import platform

def check_python():
    # 检查Python是否已安装
    try:
        python_version = sys.version
        print(f"Python已安装，版本为: {python_version}")
        return True
    except:
        return False

def install_python():
    system = platform.system().lower()
    if system == "windows":
        try:
            # 下载Python安装程序
            print("正在下载Python安装程序...")
            subprocess.run(["curl", "-o", "python_installer.exe", 
                          "https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe"], 
                         check=True)
            
            # 安装Python
            print("正在安装Python...")
            subprocess.run(["python_installer.exe", "/quiet", "InstallAllUsers=1", 
                          "PrependPath=1"], check=True)
            
            # 清理安装文件
            os.remove("python_installer.exe")
            print("Python安装成功！")
        except Exception as e:
            print(f"安装失败: {str(e)}")
            print("请访问 https://www.python.org/downloads/ 手动下载安装Python")
    else:
        print("非Windows系统，请使用系统包管理器安装Python")

if __name__ == "__main__":
    if not check_python():
        print("未检测到Python，开始安装...")
        install_python()
    else:
        print("Python检查完成，系统已安装Python")
