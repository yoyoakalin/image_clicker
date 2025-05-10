
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
