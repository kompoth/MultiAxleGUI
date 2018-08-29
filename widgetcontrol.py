import sys, os, time, math
from ctypes import *
from PyQt5 import QtCore, QtWidgets, QtGui
from frameoneaxle import *
from frametwoaxles import *

if sys.version_info >= (3,0):
	import urllib.parse

cur_dir = os.path.abspath(os.path.dirname(__file__))
ximc_dir = os.path.join(cur_dir, "ximc")
ximc_package_dir = os.path.join(ximc_dir, "crossplatform", "wrappers", "python")
sys.path.append(ximc_package_dir)

if sys.platform in ("win32", "win64"):
	libdir = os.path.join(ximc_dir, "win")
	os.environ["Path"] = libdir + ";" + os.environ["Path"]

from pyximc import *
from pyximc import MicrostepMode


class DeviceControl(QtWidgets.QWidget):
	def __init__(self, dev_list):
		super().__init__()
		self.initUI(dev_list)

	def initUI(self, dev_list):
		self.move(0, 0)
		# atributes:
		self.dev_list = []
		self.id_list = []
		self.pos_list = []
		self.speed_list = []
		self.number = len(dev_list)

		for i in range(self.number):
			name = dev_list[i]
			dev_id = lib.open_device(bytes(name, 'utf8'))
			self.dev_list.append(name)
			self.id_list.append(dev_id)


		# UI setup
		cancel_button = QtWidgets.QPushButton("Cancel")
		cancel_button.clicked.connect(self.close)
		cancel_button.setFixedSize(QtCore.QSize(80, 20))

		# layouts
		self.greatest_layout = QtWidgets.QVBoxLayout()
		self.main_layout =  QtWidgets.QHBoxLayout()
		self.cancel_layout =  QtWidgets.QHBoxLayout()
		self.setLayout(self.greatest_layout)

		self.cancel_layout.addWidget(cancel_button)
		self.greatest_layout.addLayout(self.main_layout)
		self.greatest_layout.addLayout(self.cancel_layout)

		if self.number % 2 == 1:
			one_widget = oneWidget(self.dev_list[-1], self.id_list[-1])
			self.main_layout.addWidget(one_widget)

		if self.number >= 2:
			two_widgets_1 = twoWidgets(self.dev_list[0], self.id_list[0],
									 self.dev_list[1], self.id_list[1])
			self.main_layout.addWidget(two_widgets_1)
			if self.number >=4:
				two_widgets_2 = twoWidgets(self.dev_list[2], self.id_list[2],
									 self.dev_list[3], self.id_list[3])
				self.main_layout.addWidget(two_widgets_2)
				if self.number ==6:
					two_widgets_3 = twoWidgets(self.dev_list[4], self.id_list[4],
									 self.dev_list[5], self.id_list[5])
					self.main_layout.addWidget(two_widgets_3)

		self.setWindowTitle("Control")
		self.show()


	def closeEvent(self, event):
		""" Закрываем устройства, чтобы их можно 
			было переподключать в той же сессии """
		for i in range(self.number):
			c_id = c_int(self.id_list[i])
			res = lib.close_device(byref(c_id))
		event.accept()