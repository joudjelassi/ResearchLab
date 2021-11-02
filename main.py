import sys
import time
import os
import threading

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

app = QApplication(sys.argv)

class pump:
	def __init__(self, addr, sn, direction):
		super(pump, self).__init__()
		self.hat = MotorKit(address=addr)
		if sn == 1:
			self.stepper = self.hat.stepper1
		else:
			self.stepper = self.hat.stepper2
		self.stepper.release()
		self.currentPosition = 0
		if direction == 'N':
			self.forward = stepper.FORWARD
			self.backward = stepper.BACKWARD
		else:
			self.forward = stepper.BACKWARD
			self.backward = stepper.FORWARD

	def oneStep(self, stepperDirection):
		self.stepper.onestep(direction=stepperDirection, style=stepper.DOUBLE)

	def runMotor(self, numSteps, direction):
		for i in range(numSteps):
			self.oneStep(direction)
		self.release()

	def release(self):
		self.stepper.release()

class mainWindow(QWidget):
	class button(QPushButton):
		def __init__(self):
			super(mainWindow.button, self).__init__()
			self.setText("Button Name")

		def setButtonColor(self, color):
			self.setStyleSheet('background-color: {}'.format(color))

		def setButtonText(self, text):
			self.setText(text)

	def __init__(self, *args, **kwargs):
		super(mainWindow, self).__init__()
		self.stepperCount = 0
		self.forwardTimer = QTimer()
		self.backwardTimer = QTimer()

		self.loadComponents()
		self.currentMotor = self.peristaltic1
		self.loadButtons()
		self.UI()


	def loadComponents(self):
		self.peristaltic1 = pump(0x60, 1, "N")  # CHAMBER TO COLORIMETRIC
		self.peristaltic2 = pump(0x60, 2, "N")  # CHAMBER WASTE
# 		self.peristaltic3 = pump(0x62, 1, "W")  # MAGLEV EXTRACTION
# 		self.peristaltic4 = pump(0x62, 2, "W")  # RNASE INHIBITOR
# 		self.peristaltic5 = pump(0x63, 1, "W")  # REAGENT MIX 2
# 		self.peristaltic6 = pump(0x63, 2, "N")  # REAGENT MIX 3
# 		self.peristaltic7 = pump(0x64, 1, "N")  # REAGENT MIX 4
# 		self.peristaltic8 = pump(0x64, 2, "N")  # REAGE
		# self.stepperMotor = motorControl(0x64, 1)

	def loadButtons(self):
		self.b1 = self.button()
		self.b1.setButtonText("100 Forward")
		self.b1.clicked.connect(lambda: self.stepperControl(100, self.currentMotor.forward))

		self.b2 = self.button()
		self.b2.setButtonText("1000 Forward")
		self.b2.clicked.connect(lambda: self.stepperControl(1000, self.currentMotor.forward))

		self.b3 = self.button()
		self.b3.setButtonText("100 Backward")
		self.b3.clicked.connect(lambda: self.stepperControl(100, self.currentMotor.backward))

		self.b4 = self.button()
		self.b4.setButtonText("1000 Backward")
		self.b4.clicked.connect(lambda: self.stepperControl(1000, self.currentMotor.backward))

		self.b5 = self.button()
		self.b5.setButtonText("Reset Count")
		self.b5.clicked.connect(lambda: self.resetCount())

		self.b6 = self.button()
		self.b6.setButtonText("FORWARD")
		self.b6.pressed.connect(lambda: self.stepperForwardStart())
		self.b6.released.connect(lambda: self.stepperForwardReleased())

		self.b7 = self.button()
		self.b7.setButtonText("BACKWARD")
		self.b7.pressed.connect(lambda: self.stepperBackwardStart())
		self.b7.released.connect(lambda: self.stepperBackwardReleased())

		self.stepperCountLabel = QLabel()
		self.stepperCountLabel.setText("Steps = {}".format(self.stepperCount))

		self.s1 = self.button()
		self.s1.setButtonText("1")
		self.s1.clicked.connect(lambda: self.setCurrentMotor(1))

		self.s2 = self.button()
		self.s2.setButtonText("2")
		self.s2.clicked.connect(lambda: self.setCurrentMotor(2))
#
# 		self.s3 = self.button()
# 		self.s3.setButtonText("3")
# 		self.s3.clicked.connect(lambda: self.setCurrentMotor(3))
#
# 		self.s4 = self.button()
# 		self.s4.setButtonText("4")
# 		self.s4.clicked.connect(lambda: self.setCurrentMotor(4))
#
# 		self.s5 = self.button()
# 		self.s5.setButtonText("5")
# 		self.s5.clicked.connect(lambda: self.setCurrentMotor(5))
#
# 		self.s6 = self.button()
# 		self.s6.setButtonText("6")
# 		self.s6.clicked.connect(lambda: self.setCurrentMotor(6))

# 		self.s7 = self.button()
# 		self.s7.setButtonText("7")
# 		self.s7.clicked.connect(lambda: self.setCurrentMotor(7))
#
# 		self.s8 = self.button()
# 		self.s8.setButtonText("8")
# 		self.s8.clicked.connect(lambda: self.setCurrentMotor(8))
#
	def setCurrentMotor(self, motorNum):
		if motorNum == 1:
			self.currentMotor = self.peristaltic1
		elif motorNum == 2:
			self.currentMotor = self.peristaltic2
# 		elif motorNum == 3:
# 			self.currentMotor = self.peristaltic3
# 		elif motorNum == 4:
# 			self.currentMotor = self.peristaltic4
# 		elif motorNum == 5:
# 			self.currentMotor = self.peristaltic5
# 		elif motorNum == 6:
# 			self.currentMotor = self.peristaltic6
# 		elif motorNum == 7:
# 			self.currentMotor = self.peristaltic7
# 		elif motorNum == 8:
# 			self.currentMotor = self.peristaltic8
		else:
			self.currentMotor = self.peristaltic1

	def stepperControl(self, steps, direction):
		self.currentMotor.runMotor(steps, direction)
		if direction == stepper.FORWARD:
			self.stepperCount += steps
		else:
			self.stepperCount -= steps
		self.stepperCountLabel.setText("Steps = {}".format(self.stepperCount))

	def stepperForwardStart(self):
		self.forwardStatus = True
		while self.forwardStatus:
			app.processEvents()
			self.stepperControl(50, self.currentMotor.forward)

	def stepperForwardReleased(self):
		self.forwardStatus = False
		self.currentMotor.release()

	def stepperBackwardStart(self):
		self.backwardStatus = True
		while self.backwardStatus:
			app.processEvents()

	def stepperBackwardReleased(self):
		self.backwardStatus = False
		self.currentMotor.release()

	def resetCount(self):
		self.stepperCount = 0
		self.stepperCountLabel.setText("Steps = {}".format(self.stepperCount))

	def UI(self):
		self.UILayout = QGridLayout()

		self.UILayout.addWidget(self.b1, 0, 0, 1, 2)
		self.UILayout.addWidget(self.b2, 1, 0, 1, 2)
		self.UILayout.addWidget(self.b3, 2, 0, 1, 2)
		self.UILayout.addWidget(self.b4, 3, 0, 1, 2)
		self.UILayout.addWidget(self.b5, 4, 0, 1, 2)
		self.UILayout.addWidget(self.b6, 5, 0, 1, 2)
		self.UILayout.addWidget(self.b7, 6, 0, 1, 2)

		self.UILayout.addWidget(self.s1, 0, 2, 1, 1)
		self.UILayout.addWidget(self.s2, 1, 2, 1, 1)
# 		self.UILayout.addWidget(self.s3, 2, 2, 1, 1)
# 		self.UILayout.addWidget(self.s4, 3, 2, 1, 1)
# 		self.UILayout.addWidget(self.s5, 4, 2, 1, 1)
# 		self.UILayout.addWidget(self.s6, 5, 2, 1, 1)
# 		self.UILayout.addWidget(self.s7, 6, 2, 1, 1)
# 		self.UILayout.addWidget(self.s8, 7, 2, 1, 1)

		self.UILayout.addWidget(self.stepperCountLabel)

		self.setLayout(self.UILayout)

def main():
	UI = mainWindow()
	UI.show()
	sys.exit(app.exec_())


if __name__ == "__main__":
	main()
