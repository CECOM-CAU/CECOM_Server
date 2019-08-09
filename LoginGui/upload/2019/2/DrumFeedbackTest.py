import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
#from PyQt5 import uic
from PyQt5 import QtCore
#from PyQt5.QtCore import pyqtSlot
from functools import partial

#Made by Younsoo 'coolkys' Kim ,2019 MAY 17
#Special thanks to 'eyllanesc' of stackoverflow for posting the 
#answer to "인정병원" over at
#https://stackoverflow.com/questions/52270391/i-want-to-create-a-color-animation-for-a-button-with-pyqt5
#after which I used to model this demo.

class Drumpad(QtWidgets.QPushButton):
	def __init__(self, *args, **kwargs):
		super(Drumpad, self).__init__(*args, **kwargs)
		effect = QtWidgets.QGraphicsColorizeEffect(self)
		self.setGraphicsEffect(effect)

		self.animation = QtCore.QPropertyAnimation(effect, b"color")
		self.animation.setStartValue(QtGui.QColor(QtCore.Qt.cyan))
		self.animation.setEndValue(QtGui.QColor(255,255,255))

		self.animation.setLoopCount(1)
		self.animation.setDuration(200)

class ReactionWidget(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super(ReactionWidget,self).__init__(parent)
		mainlayout = QtWidgets.QVBoxLayout(self)
		self.Drums = QtWidgets.QGroupBox()
		mainlayout.addWidget(self.Drums)
		mainlayout.setContentsMargins(150,150,150,150)

		lay = QtWidgets.QGridLayout(self.Drums)

		keypad = [
			'1','2','3',
			'drum1','drum2','drum3'
			]

		positions = [(i,j) for i in range (2) for j in range(3)]

		self.buttons = {}

		for position, name in zip(positions, keypad):
			if name == "1":
				btn = Drumpad(name)
				btn.setStyleSheet('background-color: white; font: 50pt;')
				btn.setDisabled(True)
			elif name == "2":
				btn = Drumpad(name)
				btn.setStyleSheet('background-color: white; font: 50pt;')
				btn.setDisabled(True)
			elif name == "3":
				btn = Drumpad(name)
				btn.setStyleSheet('background-color: white; font: 50pt;')
				btn.setDisabled(True)
			else:
				btn = QtWidgets.QPushButton(name)
				btn.setStyleSheet('background-color: white; font: 10pt;')

			self.buttons[name] = btn
			btn.clicked.connect(partial(self.on_clicked, name)) #Originally, syntax should be: self.<button>.clicked.connect(self.<function>)
			btn.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
			lay.addWidget(btn, *position)

	def on_clicked(self, text):
		if text == "drum1":
			btn = self.buttons["1"]
			#btn.setEnabled(True)
			btn.animation.stop()
			btn.animation.start()
		
		elif text == "drum2":
			btn = self.buttons["2"]
			#btn.setEnabled(True)
			btn.animation.stop()
			btn.animation.start()
		
		elif text == "drum3":
			btn = self.buttons["3"]
			#btn.setEnabled(True)
			btn.animation.stop()
			btn.animation.start()


class Form(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.center_widget = QtWidgets.QStackedWidget()
		self.setCentralWidget(self.center_widget)
		self.SearchUI()

	def SearchUI(self):
		reactionWidget = ReactionWidget()
		self.center_widget.addWidget(reactionWidget)

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	w = Form()
	w.show()
	sys.exit(app.exec_())
