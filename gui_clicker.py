import sys
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QTextEdit, QMessageBox, QSpinBox)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QRect, QPoint, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QScreen
from image_clicker import ImageClicker

class RegionSelector(QWidget):
    """区域选择器"""
    region_selected = pyqtSignal(tuple)
    
    def __init__(self):
        super().__init__()
        # 设置窗口标志
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |  # 保持在最顶层
            Qt.FramelessWindowHint |   # 无边框
            Qt.Tool                    # 工具窗口
        )
        # 设置窗口状态
        self.setWindowState(Qt.WindowFullScreen)
        # 设置背景色
        self.setStyleSheet("background-color: rgba(0, 0, 0, 100);")
        # 设置窗口透明度
        self.setWindowOpacity(0.7)
        
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen()
        self.screen_geometry = screen.geometry()
        self.setGeometry(self.screen_geometry)
        
        self.start_pos = None
        self.end_pos = None
        self.is_selecting = False
        
        # 显示提示信息
        self.tip_label = QLabel("按住鼠标左键拖动选择区域，按ESC取消", self)
        self.tip_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 150);
                padding: 5px;
                border-radius: 3px;
                font-size: 14px;
            }
        """)
        self.tip_label.move(10, 10)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # 绘制半透明背景
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        
        if self.is_selecting and self.start_pos and self.end_pos:
            # 计算选择区域
            x = min(self.start_pos.x(), self.end_pos.x())
            y = min(self.start_pos.y(), self.end_pos.y())
            width = abs(self.end_pos.x() - self.start_pos.x())
            height = abs(self.end_pos.y() - self.start_pos.y())
            
            # 清除选择区域的背景
            painter.eraseRect(x, y, width, height)
            
            # 绘制选择框
            pen = QPen(QColor(0, 120, 215), 2)
            painter.setPen(pen)
            painter.drawRect(x, y, width, height)
            
            # 绘制尺寸信息
            size_text = f"{width} x {height}"
            painter.setPen(QColor(0, 120, 215))
            painter.drawText(x + 5, y - 5, size_text)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.is_selecting = True
            self.tip_label.hide()
            self.update()
            
    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end_pos = event.pos()
            self.update()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.end_pos = event.pos()
            self.is_selecting = False
            
            # 计算选择区域
            x = min(self.start_pos.x(), self.end_pos.x())
            y = min(self.start_pos.y(), self.end_pos.y())
            width = abs(self.end_pos.x() - self.start_pos.x())
            height = abs(self.end_pos.y() - self.start_pos.y())
            
            # 确保选择区域有效
            if width > 10 and height > 10:
                # 发送选择区域信号
                self.region_selected.emit((x, y, width, height))
                self.close()
            else:
                self.tip_label.show()
                self.update()
                
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            
    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        self.activateWindow()  # 激活窗口
        self.raise_()         # 提升窗口层级

class RecognitionThread(QThread):
    """识别线程"""
    log_signal = pyqtSignal(str)
    
    def __init__(self, clicker, target_text, region=None, interval=10):
        super().__init__()
        self.clicker = clicker
        self.target_text = target_text
        self.region = region
        self.interval = interval
        self.is_running = False
        
    def run(self):
        self.is_running = True
        while self.is_running:
            try:
                # 执行文字识别和点击
                result = self.clicker.find_text_and_click(self.target_text, self.region)
                if result:
                    self.log_signal.emit(f"成功识别并点击文字: {self.target_text}")
                else:
                    self.log_signal.emit(f"未找到文字: {self.target_text}")
                
                # 等待指定间隔时间
                for i in range(self.interval):
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.log_signal.emit(f"发生错误: {str(e)}")
                break
                
    def stop(self):
        self.is_running = False
        self.wait()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.recognition_thread = None
        self.region_selector = None
        
    def initUI(self):
        self.setWindowTitle('图像识别点击器')
        self.setGeometry(100, 100, 600, 400)
        
        # 创建主窗口部件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        
        # Tesseract路径设置
        tesseract_layout = QHBoxLayout()
        tesseract_label = QLabel('Tesseract路径:')
        self.tesseract_path = QLineEdit()
        self.tesseract_path.setText('C:\\Program Files\\Tesseract-OCR\\tesseract.exe')
        tesseract_layout.addWidget(tesseract_label)
        tesseract_layout.addWidget(self.tesseract_path)
        layout.addLayout(tesseract_layout)
        
        # 目标文字设置
        text_layout = QHBoxLayout()
        text_label = QLabel('目标文字:')
        self.target_text = QLineEdit()
        text_layout.addWidget(text_label)
        text_layout.addWidget(self.target_text)
        layout.addLayout(text_layout)
        
        # 区域设置
        region_layout = QHBoxLayout()
        region_label = QLabel('搜索区域 (左,上,宽,高):')
        self.region_input = QLineEdit()
        self.region_input.setPlaceholderText('例如: 100,100,400,400')
        self.region_button = QPushButton('框选范围')
        self.region_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
        """)
        region_layout.addWidget(region_label)
        region_layout.addWidget(self.region_input)
        region_layout.addWidget(self.region_button)
        layout.addLayout(region_layout)
        
        # 识别间隔设置
        interval_layout = QHBoxLayout()
        interval_label = QLabel('识别间隔(秒):')
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 3600)
        self.interval_spinbox.setValue(10)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_spinbox)
        interval_layout.addStretch()
        layout.addLayout(interval_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.start_button = QPushButton('开始识别')
        self.stop_button = QPushButton('停止识别')
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)
        
        # 日志显示
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)
        
        # 设置布局
        main_widget.setLayout(layout)
        
        # 连接信号
        self.start_button.clicked.connect(self.start_recognition)
        self.stop_button.clicked.connect(self.stop_recognition)
        self.region_button.clicked.connect(self.select_region)
        
    def select_region(self):
        """打开区域选择器"""
        try:
            # 创建区域选择器
            self.region_selector = RegionSelector()
            self.region_selector.region_selected.connect(self.on_region_selected)
            
            # 使用定时器延迟显示选择器
            QTimer.singleShot(100, self.show_region_selector)
            
        except Exception as e:
            self.log(f"创建区域选择器失败: {str(e)}")
            QMessageBox.critical(self, '错误', f'创建区域选择器失败: {str(e)}')
            
    def show_region_selector(self):
        """显示区域选择器"""
        try:
            self.hide()  # 隐藏主窗口
            self.region_selector.show()
            self.region_selector.activateWindow()  # 激活窗口
            self.region_selector.raise_()         # 提升窗口层级
        except Exception as e:
            self.log(f"显示区域选择器失败: {str(e)}")
            self.show()  # 确保主窗口显示
            QMessageBox.critical(self, '错误', f'显示区域选择器失败: {str(e)}')
        
    def on_region_selected(self, region):
        """处理区域选择结果"""
        try:
            x, y, width, height = region
            self.region_input.setText(f"{x},{y},{width},{height}")
            self.show()  # 显示主窗口
            self.log(f"已选择区域: {x},{y},{width},{height}")
        except Exception as e:
            self.log(f"处理区域选择结果失败: {str(e)}")
            self.show()  # 确保主窗口显示
            QMessageBox.critical(self, '错误', f'处理区域选择结果失败: {str(e)}')
        
    def log(self, message):
        """添加日志"""
        self.log_display.append(f"[{time.strftime('%H:%M:%S')}] {message}")
        
    def parse_region(self):
        """解析区域设置"""
        if not self.region_input.text():
            return None
        try:
            left, top, width, height = map(int, self.region_input.text().split(','))
            return (left, top, width, height)
        except:
            QMessageBox.warning(self, '警告', '区域格式错误，请使用"左,上,宽,高"的格式')
            return None
            
    def start_recognition(self):
        """开始识别"""
        if not self.target_text.text():
            QMessageBox.warning(self, '警告', '请输入目标文字')
            return
            
        # 创建识别器实例
        try:
            self.clicker = ImageClicker(
                confidence=0.8,
                tesseract_path=self.tesseract_path.text()
            )
        except Exception as e:
            QMessageBox.critical(self, '错误', f'初始化识别器失败: {str(e)}')
            return
            
        # 创建并启动识别线程
        self.recognition_thread = RecognitionThread(
            self.clicker,
            self.target_text.text(),
            self.parse_region(),
            self.interval_spinbox.value()
        )
        self.recognition_thread.log_signal.connect(self.log)
        self.recognition_thread.start()
        
        # 更新按钮状态
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.log('开始识别...')
        
    def stop_recognition(self):
        """停止识别"""
        if self.recognition_thread:
            self.recognition_thread.stop()
            self.recognition_thread = None
            
        # 更新按钮状态
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.log('停止识别')
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.recognition_thread:
            self.stop_recognition()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 