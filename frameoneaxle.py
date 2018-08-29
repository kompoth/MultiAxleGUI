import sys, os, time, math
from ctypes import *
from PyQt5 import QtCore, QtWidgets, QtGui

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



class oneWidget(QtWidgets.QFrame):
	def __init__(self, device, dev_id):
		super().__init__()
		self.initUI(device, dev_id)

	def initUI(self, device, dev_id):
		self.id = dev_id
		self.name = device
		self.b_name = bytes(self.name, 'utf8')
		print(self.name)
		print(self.id)

		# UI setup
		self.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)

		zero_button = QtWidgets.QPushButton("Zero")
		zero_button.clicked.connect(self.zero)
		stop_button = QtWidgets.QPushButton("Stop")
		stop_button.clicked.connect(self.stop_motion)
		move_button = QtWidgets.QPushButton("Move to")
		move_button.clicked.connect(self.move_to)

		self.up_button = QtWidgets.QPushButton("Up")
		self.up_button.pressed.connect(self.start_motion)
		self.up_button.released.connect(self.stop_motion)
		self.down_button = QtWidgets.QPushButton("Down")
		self.down_button.pressed.connect(self.start_motion)
		self.down_button.released.connect(self.stop_motion)
		self.draw_space = drawSpace()

		name_lbl = QtWidgets.QLabel(self)
		name_lbl.setFixedWidth(100)
		name_lbl.setText(str(self.name))
		# current position display
		pos_title = QtWidgets.QLabel()
		pos_title.setText("Position: ")
		self.pos_lbl = QtWidgets.QLabel(self)
		self.pos_lbl.setFixedWidth(100)
		# current speed display
		speed_title = QtWidgets.QLabel()
		speed_title.setText("Speed: ")
		self.speed_lbl = QtWidgets.QLabel(self)
		self.speed_lbl.setFixedWidth(100)

		self.new_pos_line = QtWidgets.QLineEdit()
		self.new_pos_line.setText("0")
		self.new_pos_line.setFixedSize(QtCore.QSize(100, 16777215))

		self.one_axle_layout =  QtWidgets.QVBoxLayout(self)
		upper_layout = QtWidgets.QGridLayout()

		upper_layout.addWidget(name_lbl, 0, 0, 1, 1)
		upper_layout.addWidget(zero_button, 1, 0, 1, 1)
		upper_layout.addWidget(move_button, 2, 0, 1, 1)
		upper_layout.addWidget(stop_button, 3, 0, 1, 1)
		upper_layout.addWidget(self.up_button, 4, 0, 1, 1)
		upper_layout.addWidget(self.down_button, 5, 0, 1, 1)
		upper_layout.addWidget(pos_title, 6, 0, 1, 1)
		upper_layout.addWidget(self.pos_lbl, 6, 1, 1, 1)
		upper_layout.addWidget(speed_title, 7, 0, 1, 1)
		upper_layout.addWidget(self.speed_lbl, 7, 1, 1, 1)
		upper_layout.addWidget(self.new_pos_line, 2, 1, 1, 1)
		upper_layout.addWidget(self.draw_space, 8, 0, 8, 4)

		self.one_axle_layout.addLayout(upper_layout)
		self.get_data()
		# timer to run updating function get_data
		self.draw_space.timer.timeout.connect(self.get_data)


	def get_data(self):
		# updating data
		pos_struct = get_position_t()
		lib.get_position(self.id, byref(pos_struct))
		self.draw_space.pos = pos_struct.Position
		self.pos_lbl.setText(repr(self.draw_space.pos))
		stat_struct = status_t()
		lib.get_status(self.id, byref(stat_struct))
		self.draw_space.speed = stat_struct.CurSpeed
		self.speed_lbl.setText(repr(self.draw_space.speed))
		if abs(self.draw_space.speed) > 3: 
			self.draw_space.timer.setInterval(1)
		else:
			self.draw_space.timer.setInterval(100)

	def start_motion(self):
		""" called by pressing the motion button """
		lib.command_wait_for_stop(self.id, 10)
		sender = self.sender()
		if sender == self.up_button:
			lib.command_right(self.id)
		elif sender == self.down_button:
			lib.command_left(self.id)

	def stop_motion(self):
		""" called by releasing the motion button
			or by pressing stop button """
		lib.command_sstp(self.id)
		lib.command_wait_for_stop(self.id, 10)
		time.sleep(0.14)
		self.get_data()

	def move_to(self):
		""" movement to a specific point """
		new_pos = int(self.new_pos_line.text())
		lib.command_move(self.id, new_pos, 0)
		self.get_data()


	def zero(self):
		""" sets current position to zero """
		lib.command_zero(self.id)
		self.get_data()




class drawSpace(QtWidgets.QWidget):
	""" Initialy it was a subwidget to draw image of moving point,
	now it has its own timer, which is also used in oneWidget class 
	to update motion data """
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.pos = 0
		self.speed = 0
		self.point_speed = 1

		self.timer = QtCore.QTimer()
		self.timer.setSingleShot(False)
		self.timer.setInterval(1000)
		self.timer.timeout.connect(self.move_point)

		self.setFixedSize(100, 240)

		self.max_lbl = QtWidgets.QLabel(self)
		self.max_lbl.setFixedWidth(100)
		self.min_lbl = QtWidgets.QLabel(self)
		self.min_lbl.setFixedWidth(100)
		self.midle_lbl = QtWidgets.QLabel(self)
		self.midle_lbl.setText(str(0))
		self.point = QtWidgets.QLabel(self)
		self.point.setPixmap(QtGui.QPixmap("point.png"))

		self.timer.start()

	def paintEvent(self, event):
		qp = QtGui.QPainter()
		qp.begin(self)
		self.draw1axle(event, qp)
		qp.end()

	def draw1axle(self, event, qp):
		borders_pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
		grids_pen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.DashLine)

		place = [50, 10]
		qp.setPen(borders_pen)
		qp.drawLine(place[0], place[1], place[0], place[1]+200)
		qp.drawLine(place[0], place[1]+200, place[0]+30, place[1]+200)
		qp.drawLine(place[0]+30, place[1]+200, place[0]+30, place[1])
		qp.drawLine(place[0]+30, place[1], place[0], place[1])	

		qp.setPen(grids_pen)
		for i in range(20):
			if i == 10:
				qp.setPen(borders_pen)
			qp.drawLine(place[0], place[1]+10*i, place[0]+30, place[1]+10*i)
			if i == 10:
				qp.setPen(grids_pen)

		self.max_lbl.setText(str(10000*self.point_speed))
		self.min_lbl.setText(str(-10000*self.point_speed))
		self.max_lbl.move(place[0]-40, place[1]-5)
		self.min_lbl.move(place[0]-40, place[1]+195)
		self.midle_lbl.move(place[0]-20, place[1]+95)

	def move_point(self):
		if abs(self.speed) > 3: 
			self.timer.setInterval(1)
		else:
			self.timer.setInterval(100)
		self.point.move(59, 105-self.pos//(100*self.point_speed))
		if self.point_speed != abs(self.pos)//10000 + 1:
			cur_pos = abs(self.pos)
			self.point_speed = cur_pos//10000 + 1
			self.max_lbl.setText(str(10000*self.point_speed))
			self.min_lbl.setText(str(-10000*self.point_speed))

	 