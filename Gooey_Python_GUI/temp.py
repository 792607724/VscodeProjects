# coding = utf8

import os
os.path.abspath(".")
"""
    Python图形化操作界面
    pip3 install Gooey
    brew install upx
    pip3 install pyinstaller

    打包应用程序：
    然后在 terminal 中依次键入:
    pyinstaller --windowed --onefile --clean --noconfirm main.py
    pyinstaller --clean --noconfirm --windowed --onefile main.spec

    其中，如果要自行设计 Mac 系统下的图标的话，那么可以替换第 1 条指令为：

    pyinstaller --windowed --onefile --icon=sat_tool_icon.icns --clean --noconfirm main.py
    其中图片转换地址为 https://iconverticons.com/online/

    而 windows 系统下的图片格式应为 .ico,如果要打包成windows运行程序，需要在windows中进行打包
    """

from gooey import Gooey, GooeyParser

@Gooey
def create_window():
    parser = GooeyParser(description="Gooey App!")
    parser.add_argument("File Name:", help="Name of file in your computer's address", widget="FileChooser")    
    parser.add_argument("Datetime", help="Choose date in today", widget="DateChooser")
    args = parser.parse_args()
    print(args) # windows下会无法解码，windows下必须用全英文

def test():
    # show_path()
    print("test" + os.getcwd())

if __name__ == '__main__':
    create_window()
    # test()
    

