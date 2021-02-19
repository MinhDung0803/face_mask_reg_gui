Installation
	pip3 install --user pyqt5  
	sudo apt-get install python3-pyqt5  
	sudo apt-get install pyqt5-dev-tools
	sudo apt-get install qttools5-dev-tools

Run from terminal
	qtchooser -run-tool=designer -qt=5

Conver to .py file from .ui file
	pyuic5 -x <.ui file name> -o <.py file name>


self.plot1.clicked.connect(self.display_plotting_figure_1)
self.button_camera_name_1.clicked.connect(self.get_camera_name_1)
self.plot2.clicked.connect(self.display_plotting_figure_2)
self.button_camera_name_2.clicked.connect(self.get_camera_name_2)
