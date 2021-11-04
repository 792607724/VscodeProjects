# coding = utf8

import os
os.path.abspath(".")

import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import QtCore

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    w = QWidget()
    w.setFixedSize(250, 150)
    # w.move(300, 300)
    # 无法控制mac os的最大化按钮，windows是OK的
    w.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.ApplicationHidden)
    w.setWindowTitle("Hi Bruce")
    w.show()

    sys.exit(app.exec_())
    

