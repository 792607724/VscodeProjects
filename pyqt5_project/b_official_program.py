# coding = utf8

import os
os.path.abspath(".")

import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QPushButton, QMessageBox, QDesktopWidget, QLabel
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QCoreApplication


class B_Official_Program(QWidget):


    def __init__(self):
        super().__init__()
        self.initUI()
    
    
    # 加载父UI
    def initUI(self):
        QToolTip.setFont(QFont("Arial", 10))
        self.initChildUI()
        self.center()
        self.setToolTip("This is a <b>QWidget</b> widget")
        self.resize(750, 450)
        self.setWindowTitle("A Official Program")
        # Mac os don't need a icon, just windows worked
        self.setWindowIcon(QIcon("./ice_mirrow.jpeg"))
        self.show()


    # 加载子UI
    def initChildUI(self):
        """
            Init a button to quit
        """
        btn = QPushButton("Quit", self)
        btn.setToolTip("This is a <b>QPushButton</b> widget")
        btn.resize(btn.sizeHint())
        btn.move(self.width(), 0)
        # btn.clicked.connect(QCoreApplication.instance().quit)
        btn.clicked.connect(self.close)

        """
            Init some label to display
        """
        label1 = QLabel("Zetcode", self)
        label1.move(0, 0)


    # 重写关闭事件
    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Message", "Are you sure to quit?\n\tby Bruce",
            QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


    # 窗口显示在屏幕中心
    def center(self):
        qr = self.frameGeometry() # 获得窗口
        center_point = QDesktopWidget().availableGeometry().center() # 获取屏幕中心点
        qr.moveCenter(center_point) # 显示到屏幕中心
        self.move(qr.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = B_Official_Program()
    sys.exit(app.exec_())
    



