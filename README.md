# 图像识别点击器

这是一个基于 PyQt5 和 Tesseract OCR 的图像识别点击工具。它可以自动识别屏幕上的文字并进行点击操作。

## 功能特点

- 支持屏幕区域选择
- 文字识别和自动点击
- 可配置识别间隔时间
- 实时日志显示
- 友好的图形用户界面

## 系统要求

- Python 3.6+
- PyQt5
- Tesseract OCR
- 其他依赖项（见 requirements.txt）

## 安装步骤

1. 克隆仓库：
```bash
git clone [您的仓库URL]
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 安装 Tesseract OCR：
- Windows: 从 [Tesseract 官网](https://github.com/UB-Mannheim/tesseract/wiki) 下载安装
- Linux: `sudo apt-get install tesseract-ocr`
- Mac: `brew install tesseract`

## 使用方法

1. 运行程序：
```bash
python gui_clicker.py
```

2. 在界面中设置：
   - Tesseract 路径
   - 目标文字
   - 搜索区域
   - 识别间隔时间

3. 点击"开始识别"按钮开始运行

## 注意事项

- 确保 Tesseract OCR 已正确安装并配置
- 建议使用管理员权限运行程序
- 识别准确度受屏幕分辨率和文字清晰度影响

## 许可证

MIT License 