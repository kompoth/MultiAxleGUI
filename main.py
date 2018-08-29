import sys, os
from PyQt5 import QtWidgets
from widgetselect import *

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	select_window = DeviceSelect()
	sys.exit(app.exec_())
