import cv2
import numpy as np
import pyautogui
import time
import pytesseract
from typing import Tuple, Optional, List
from PIL import Image

class ImageClicker:
    def __init__(self, confidence: float = 0.8, tesseract_path: str = None):
        """
        初始化图像点击器
        :param confidence: 匹配置信度阈值 (0-1)
        :param tesseract_path: Tesseract OCR引擎路径
        """
        self.confidence = confidence
        # 设置pyautogui的安全特性
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
        # 设置Tesseract路径（如果需要）
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def find_and_click(self, template_path: str, region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """
        查找图像并点击
        :param template_path: 模板图像路径
        :param region: 搜索区域 (left, top, width, height)
        :return: 是否找到并点击成功
        """
        try:
            # 读取模板图像
            template = cv2.imread(template_path)
            if template is None:
                print(f"无法读取模板图像: {template_path}")
                return False

            # 获取屏幕截图
            screenshot = pyautogui.screenshot(region=region)
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            # 模板匹配
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= self.confidence:
                # 计算点击位置
                h, w = template.shape[:2]
                click_x = max_loc[0] + w // 2
                click_y = max_loc[1] + h // 2

                if region:
                    click_x += region[0]
                    click_y += region[1]

                # 移动鼠标并点击
                pyautogui.click(click_x, click_y)
                print(f"成功点击图像，位置: ({click_x}, {click_y})")
                return True
            else:
                print(f"未找到匹配图像，最大匹配度: {max_val}")
                return False

        except Exception as e:
            print(f"发生错误: {str(e)}")
            return False

    def find_text_and_click(self, target_text: str, region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """
        查找文字并点击
        :param target_text: 要查找的文字
        :param region: 搜索区域 (left, top, width, height)
        :return: 是否找到并点击成功
        """
        try:
            # 获取屏幕截图
            screenshot = pyautogui.screenshot(region=region)
            
            # 转换为OpenCV格式
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # 图像预处理：灰度、二值化、反色
            gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
            # 反色（适合深底浅字）
            inv = cv2.bitwise_not(gray)
            # 二值化
            _, thresh = cv2.threshold(inv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 保存预处理图片（调试用）
            # cv2.imwrite('debug_ocr.png', thresh)
            
            # 使用Tesseract进行文字识别，优化参数
            custom_config = r'--oem 3 --psm 7'
            data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT, lang='eng', config=custom_config)
            
            # 遍历识别到的文字
            for i, text in enumerate(data['text']):
                if target_text.lower() in text.lower():
                    # 获取文字位置
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    
                    # 计算点击位置（文字中心）
                    click_x = x + w // 2
                    click_y = y + h // 2
                    
                    if region:
                        click_x += region[0]
                        click_y += region[1]
                    
                    # 移动鼠标并点击
                    pyautogui.click(click_x, click_y)
                    print(f"成功点击文字 '{text}'，位置: ({click_x}, {click_y})")
                    return True
            
            print(f"未找到文字: {target_text}")
            return False
            
        except Exception as e:
            print(f"发生错误: {str(e)}")
            return False

def main():
    # 使用示例
    clicker = ImageClicker(confidence=0.8)
    
    # 等待3秒，给用户时间切换到目标窗口
    print("程序将在3秒后开始运行...")
    time.sleep(3)
    
    # 示例1：查找并点击图像
    template_path = "template.png"
    clicker.find_and_click(template_path)
    
    # 示例2：查找并点击文字
    target_text = "点击这里"
    clicker.find_text_and_click(target_text)

if __name__ == "__main__":
    main() 