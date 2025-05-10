import os
import sys
import shutil
from PyInstaller.__main__ import run

def build():
    # 获取Python安装目录
    python_dir = os.path.dirname(sys.executable)
    python_dll = os.path.join(python_dir, 'python310.dll')

    # 清理旧的构建文件
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('ImageClicker.spec'):
        os.remove('ImageClicker.spec')

    # 获取Tesseract安装路径
    tesseract_path = r'C:\Program Files\Tesseract-OCR'
    if not os.path.exists(tesseract_path):
        print("警告：未找到Tesseract-OCR安装目录，请确保已正确安装Tesseract-OCR")
        tesseract_path = input("请输入Tesseract-OCR安装路径：")

    # 打包参数
    opts = [
        'gui_clicker.py',  # 主程序文件
        '--name=ImageClicker',  # 程序名称
        '--windowed',  # 使用GUI模式
        '--noconfirm',  # 不询问确认
        '--clean',  # 清理临时文件
        '--add-data=README.md;.',  # 添加README文件
        '--add-data=image_clicker.py;.',  # 添加主程序依赖文件
        f'--add-data={os.path.join(tesseract_path, "tessdata")};tessdata',  # 添加Tesseract数据文件
        f'--add-binary={os.path.join(tesseract_path, "tesseract.exe")};.',  # 添加Tesseract可执行文件
        f'--add-binary={os.path.join(tesseract_path, "*.dll")};.',  # 添加Tesseract DLL文件
        '--icon=NONE',  # 图标（如果有的话）
        '--hidden-import=PyQt5',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=cv2',
        '--hidden-import=numpy',
        '--hidden-import=pytesseract',
        '--hidden-import=PIL',
        '--hidden-import=pyautogui',
        '--collect-all=PyQt5',
        '--collect-all=cv2',
        '--collect-all=numpy',
        '--collect-all=pytesseract',
        '--collect-all=PIL',
        '--collect-all=pyautogui',
        '--runtime-hook=runtime_hook.py',  # 添加运行时钩子
        f'--add-binary={python_dll};.',  # 添加Python DLL
    ]

    # 创建运行时钩子文件
    with open('runtime_hook.py', 'w', encoding='utf-8') as f:
        f.write("""
import os
import sys

# 确保DLL搜索路径包含程序所在目录
if hasattr(sys, '_MEIPASS'):
    os.environ['PATH'] = sys._MEIPASS + os.pathsep + os.environ['PATH']
    
    # 设置Tesseract路径
    tesseract_path = os.path.join(sys._MEIPASS, 'tesseract.exe')
    if os.path.exists(tesseract_path):
        os.environ['TESSDATA_PREFIX'] = os.path.join(sys._MEIPASS, 'tessdata')
        os.environ['PATH'] = os.path.dirname(tesseract_path) + os.pathsep + os.environ['PATH']
""")

    # 运行打包命令
    run(opts)

    print("打包完成！")
    print("可执行文件位于 dist/ImageClicker 目录中")
    print("请确保目标计算机已安装Visual C++ Redistributable 2015-2022")

if __name__ == '__main__':
    build() 