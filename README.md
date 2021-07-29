MULTIAXLE INTERFACE
===================
_Project was a study exercise and was not updated for a long time. Currently it can be used as an example for new developers._

An example of a program with GUI, designed to work with multiple servo controllers (up to six inclusive, it is easy to increase this number if necessary) by means of XIMC protocol. GUI was created through PyQt5 package.
All necessary XIMC files are included, you can download the full package [here](https://doc.xisupport.com/en/8smc5-usb/8SMCn-USB/Files/Software.html)

### How to use:
1. Use XiLab to configurate servos and to upload 
2. Start main.py script by `python main.py` command.
3. In case of any modules absense exceptions (e.g. PyQt5) install them using pip.
4. Select devices and use GUI to manage with them.

### Files:
**main.py** -- starting point of program
**widgetselect.py** -- searches for controllers, creates device selection window, opens servo managment GUI after selection. This is a very simple example of GUI design with fixed elements.
**widgetcontrol.py** -- creates a basic panel, where device controll widgets will be situated.
**frametwoaxles.py** -- creates a widget to control two servos, bound to a two-dimensional plane.
**frameoneaxle.py** -- creates a widget to control stand-alone servo (only if an odd number of servos was chosen)
**point.png** -- an element of graphics
**ximc** -- directory with XIMC files
