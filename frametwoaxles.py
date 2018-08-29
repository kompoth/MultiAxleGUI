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


class twoWidgets(QtWidgets.QFrame):
    def __init__(self, x_device, x_dev_id, y_device, y_dev_id):
        super().__init__()
        self.initUI(x_device, x_dev_id, y_device, y_dev_id)

    def initUI(self, x_device, x_dev_id, y_device, y_dev_id):
        self.x_id = x_dev_id
        self.x_name = x_device
        self.x_b_name = bytes(self.x_name, 'utf8')
        self.y_id = y_dev_id
        self.y_name = y_device
        self.y_b_name = bytes(self.y_name, 'utf8')

        # UI setup
        self.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)
        zero_button = QtWidgets.QPushButton("Zero")
        zero_button.clicked.connect(self.zero)
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_motion)
        move_button = QtWidgets.QPushButton("Move to")
        move_button.clicked.connect(self.move_to)

        self.up_button = QtWidgets.QPushButton("Up")
        self.up_button.pressed.connect(self.start_motion)
        self.up_button.released.connect(self.stop_motion)
        self.down_button = QtWidgets.QPushButton("Down")
        self.down_button.pressed.connect(self.start_motion)
        self.down_button.released.connect(self.stop_motion)
        self.right_button = QtWidgets.QPushButton("Right")
        self.right_button.setFixedSize(QtCore.QSize(60, 16777215))
        self.right_button.pressed.connect(self.start_motion)
        self.right_button.released.connect(self.stop_motion)
        self.left_button = QtWidgets.QPushButton("Left")
        self.left_button.setFixedSize(QtCore.QSize(60, 16777215))
        self.left_button.pressed.connect(self.start_motion)
        self.left_button.released.connect(self.stop_motion)
        self.draw_space = drawSpace()


        Xname_lbl = QtWidgets.QLabel(self)
        Xname_lbl.setFixedWidth(100)
        Xname_lbl.setText("X: "+str(self.x_name))
        Yname_lbl = QtWidgets.QLabel(self)
        Yname_lbl.setFixedWidth(100)
        Yname_lbl.setText("Y: "+str(self.y_name))
        # current position display
        xpos_title = QtWidgets.QLabel()
        xpos_title.setText("X position: ")
        self.xpos_lbl = QtWidgets.QLabel(self)
        self.xpos_lbl.setFixedWidth(100)
        ypos_title = QtWidgets.QLabel()
        ypos_title.setText("Y position: ")
        self.ypos_lbl = QtWidgets.QLabel(self)
        self.ypos_lbl.setFixedWidth(100)
        # current speed display
        xsp_title = QtWidgets.QLabel()
        xsp_title.setText("X speed: ")
        self.xsp_lbl = QtWidgets.QLabel(self)
        self.xsp_lbl.setFixedWidth(100)
        ysp_title = QtWidgets.QLabel()
        ysp_title.setText("Y speed: ")
        self.ysp_lbl = QtWidgets.QLabel(self)
        self.ysp_lbl.setFixedWidth(100)

        self.new_x_line = QtWidgets.QLineEdit()
        self.new_x_line.setText("0")
        self.new_x_line.setFixedSize(QtCore.QSize(100, 16777215))
        self.new_y_line = QtWidgets.QLineEdit()
        self.new_y_line.setText("0")
        self.new_y_line.setFixedSize(QtCore.QSize(100, 16777215))

        self.one_axle_layout =  QtWidgets.QVBoxLayout(self)
        upper_layout = QtWidgets.QGridLayout()

        upper_layout.addWidget(Xname_lbl, 0, 0, 1, 2)
        upper_layout.addWidget(Yname_lbl, 0, 2, 1, 2)
        upper_layout.addWidget(zero_button, 1, 1, 1, 1)
        upper_layout.addWidget(move_button, 2, 1, 1, 1)
        upper_layout.addWidget(self.stop_button, 3, 1, 1, 1)
        upper_layout.addWidget(self.up_button, 4, 1, 1, 1)
        upper_layout.addWidget(self.down_button, 5, 1, 1, 1)
        upper_layout.addWidget(self.right_button, 4, 2, 2, 1)
        upper_layout.addWidget(self.left_button, 4, 0, 2, 1)
        upper_layout.addWidget(xpos_title, 6, 0, 1, 1)
        upper_layout.addWidget(self.xpos_lbl, 6, 1, 1, 1)
        upper_layout.addWidget(xsp_title, 7, 0, 1, 1)
        upper_layout.addWidget(self.xsp_lbl, 7, 1, 1, 1)
        upper_layout.addWidget(ypos_title, 6, 2, 1, 1)
        upper_layout.addWidget(self.ypos_lbl, 6, 3, 1, 1)
        upper_layout.addWidget(ysp_title, 7, 2, 1, 1)
        upper_layout.addWidget(self.ysp_lbl, 7, 3, 1, 1)
        upper_layout.addWidget(self.new_x_line, 2, 2, 1, 1)
        upper_layout.addWidget(self.new_y_line, 2, 3, 1, 1)
        upper_layout.addWidget(self.draw_space, 8, 1, 8, 6)

        self.one_axle_layout.addLayout(upper_layout)
        self.get_data()
        # timer to run updating function get_data
        self.draw_space.timer.timeout.connect(self.get_data)

    def get_data(self):
        # updating data
        pos_struct = get_position_t()
        lib.get_position(self.x_id, byref(pos_struct))
        self.draw_space.X = pos_struct.Position
        self.xpos_lbl.setText(repr(self.draw_space.X))
        lib.get_position(self.y_id, byref(pos_struct))
        self.draw_space.Y = pos_struct.Position
        self.ypos_lbl.setText(repr(self.draw_space.Y))

        stat_struct = status_t()
        lib.get_status(self.x_id, byref(stat_struct))
        self.draw_space.Xspeed = stat_struct.CurSpeed
        self.xsp_lbl.setText(repr(self.draw_space.Xspeed))
        lib.get_status(self.y_id, byref(stat_struct))
        self.draw_space.Yspeed = stat_struct.CurSpeed
        self.ysp_lbl.setText(repr(self.draw_space.Yspeed))

        if abs(self.draw_space.Xspeed) > 3 or abs(self.draw_space.Yspeed) > 3: 
            self.draw_space.timer.setInterval(1)
        else:
            self.draw_space.timer.setInterval(100)

    def zero(self):
        """ sets current position to zero """
        lib.command_zero(self.x_id)
        lib.command_zero(self.y_id)
        self.get_data()

    def start_motion(self):
        """ called by pressing the motion button """
        sender = self.sender()
        if sender == self.up_button:
            lib.command_right(self.y_id)
        elif sender == self.down_button:
            lib.command_left(self.y_id)
        elif sender == self.right_button:
            lib.command_right(self.x_id)
        elif sender == self.left_button:
            lib.command_left(self.x_id)

    def stop_motion(self):
        """ called by releasing the motion button
            or by pressing stop button """
        sender = self.sender()
        if sender == self.up_button or sender == self.down_button or sender == self.stop_button:
            lib.command_sstp(self.y_id)
            lib.command_wait_for_stop(self.y_id, 10)
        if sender == self.right_button or sender == self.left_button or sender == self.stop_button:
            lib.command_sstp(self.x_id)
            lib.command_wait_for_stop(self.x_id, 10)
        time.sleep(0.14)
        self.get_data()

    def move_to(self):
        """ movement to a specific point """
        new_x = int(self.new_x_line.text())
        new_y = int(self.new_y_line.text())
        lib.command_move(self.x_id, new_x, 0)
        lib.command_move(self.y_id, new_y, 0)
        self.get_data()


class drawSpace(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.red)
        self.setPalette(p)

        self.X = 0
        self.Y = 0
        self.Xspeed = 0
        self.Yspeed = 0
        self.point_Xspeed = 1
        self.point_Yspeed = 1

        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(False)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.move_point)

        self.setFixedSize(300, 250)

        self.Xmax_lbl = QtWidgets.QLabel(self)
        self.Xmax_lbl.setFixedWidth(100)
        self.Xmin_lbl = QtWidgets.QLabel(self)
        self.Xmin_lbl.setFixedWidth(100)
        self.Ymax_lbl = QtWidgets.QLabel(self)
        self.Ymax_lbl.setFixedWidth(100)
        self.Ymin_lbl = QtWidgets.QLabel(self)
        self.Ymin_lbl.setFixedWidth(100)
        self.point = QtWidgets.QLabel(self)
        self.point.setPixmap(QtGui.QPixmap("point.png"))

        self.timer.start()
        self.move_point()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.draw2axles(event, qp)
        qp.end()

    def draw2axles(self, event, qp):
        borders_pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
        grids_pen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.DashLine)

        place = [40, 20]
        qp.setPen(borders_pen)
        qp.drawLine(place[0], place[1], place[0], place[1]+200)
        qp.drawLine(place[0], place[1]+200, place[0]+200, place[1]+200)
        qp.drawLine(place[0]+200, place[1]+200, place[0]+200, place[1])
        qp.drawLine(place[0]+200, place[1], place[0], place[1])
        
        qp.setPen(grids_pen)
        for i in range(20):
            if i == 10:
                qp.setPen(borders_pen)
            qp.drawLine(place[0], place[1]+10*i, place[0]+200, place[1]+10*i)
            qp.drawLine(place[0]+10*i, place[1], place[0]+10*i, place[1]+200)
            if i == 10:
                qp.setPen(grids_pen)

        self.Xmax_lbl.setText(str(10000*self.point_Xspeed))
        self.Xmin_lbl.setText(str(-10000*self.point_Xspeed))
        self.Xmax_lbl.move(place[0]+205, place[1]+95)
        self.Xmin_lbl.move(place[0]-40, place[1]+95)

        self.Ymax_lbl.setText(str(10000*self.point_Yspeed))
        self.Ymin_lbl.setText(str(-10000*self.point_Yspeed))
        self.Ymax_lbl.move(place[0]+85, place[1]-15)
        self.Ymin_lbl.move(place[0]+80, place[1]+200)

    def move_point(self):
        if abs(self.Xspeed) > 3 or abs(self.Yspeed) > 3: 
            self.timer.setInterval(1)
        else:
            self.timer.setInterval(100)
        self.point.move(135+self.X//(100*self.point_Xspeed), 
                        115-self.Y//(100*self.point_Yspeed))
        if self.point_Xspeed != abs(self.X)//10000 + 1:
            cur_x = abs(self.X)
            self.point_Xspeed = cur_x//10000 + 1
            self.Xmax_lbl.setText(str(10000*self.point_Xspeed))
            self.Xmin_lbl.setText(str(-10000*self.point_Xspeed))
        if self.point_Yspeed != abs(self.Y)//10000 + 1:
            cur_y = abs(self.Y)
            self.point_Yspeed = cur_y//10000 + 1
            self.Ymax_lbl.setText(str(10000*self.point_Yspeed))
            self.Ymin_lbl.setText(str(-10000*self.point_Yspeed))
