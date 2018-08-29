import sys, os
from PyQt5 import QtCore, QtWidgets
from widgetcontrol import *

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

X = 400
Y = 250


def scan_for_devices():
	""" search for devices """
	probe_flags = EnumerateFlags.ENUMERATE_PROBE
	devenum = lib.enumerate_devices(probe_flags, None)
	dev_count = lib.get_device_count(devenum)
	controller_name = controller_name_t()
	# make up a dictionary of found devices
	devices_list = []
	for dev_ind in range(0, dev_count):
		enum_name = lib.get_device_name(devenum, dev_ind)
		result = lib.get_enumerate_device_controller_name(devenum, dev_ind, 
														  byref(controller_name))
		if result == Result.Ok:
			devices_list.append(enum_name)
	return devices_list, dev_count


class DeviceSelect(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def generate_menu(self):
		""" creates a list widget and displays it"""
		dev_list, number = scan_for_devices()
		if number == 1:
			num_lbl_text = "1 device found."
		elif number > 0:
			num_lbl_text = "%d devices found." % number
		else:
			num_lbl_text = "No devices found."
		self.num_lbl.setFixedWidth(100)
		self.num_lbl.setText(num_lbl_text)
		
		self.dev_widget.clear()
		for i in range(number):
			if number > i:
				name = dev_list[i].decode('utf-8')
				self.dev_widget.addItem(name)

	def initUI(self):
		self.num_lbl = QtWidgets.QLabel(self)
		self.num_lbl.move(40, 20)
		self.dev_widget = QtWidgets.QListWidget(self)
		self.dev_widget.setGeometry(QtCore.QRect(40, 40, X-150, Y-60))
		self.dev_widget.setSelectionMode(4)
		# buttons
		exit_button = QtWidgets.QPushButton("Exit", self)
		exit_button.clicked.connect(QtCore.QCoreApplication.instance().quit)
		exit_button.move(X-100, Y-40)
		scan_button = QtWidgets.QPushButton("Scan", self)
		scan_button.clicked.connect(self.generate_menu)
		scan_button.move(X-100, Y-70)
		open_button = QtWidgets.QPushButton("Open selected", self)
		open_button.clicked.connect(self.generate_control_widget)
		open_button.move(X-100, 35)

		self.generate_menu()
		self.setFixedSize(X, Y)
		self.setWindowTitle('Multi-axis')
		self.show()



	def generate_control_widget(self):
		""" opening new device """
		# draw up a list of devices to open
		list_to_do = []
		for item in list(self.dev_widget.selectedItems()):
			name=self.dev_widget.item(self.dev_widget.row(item)).text()
			list_to_do.append(name)

		number = len(list_to_do)
		if number > 6:
			self.mbx = QtWidgets.QMessageBox(self)
			self.mbx.setIcon(QtWidgets.QMessageBox.Warning)
			self.mbx.setText("More than 6 devices selected")
			self.mbx.setInformativeText("Application is not supposed to" 
										"deal with this number of devices.")
			self.mbx.setStandardButtons(QtWidgets.QMessageBox.Cancel|
										QtWidgets.QMessageBox.Ok)
			self.mbx.setObjectName("Warning")
			self.mbx.show()
			return

		self.child = DeviceControl(list_to_do)
			

