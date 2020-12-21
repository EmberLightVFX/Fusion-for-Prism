import os
import sys

prismRoot = os.getenv("PRISM_ROOT")
if not prismRoot:
    prismRoot = "C:/Prism"
	
sys.path.insert(0, os.path.join(prismRoot, "Scripts"))
sys.path.insert(0, os.path.join(prismRoot, "PythonLibs", "Python37", "PySide"))

try:
	from PySide2.QtCore import *
	from PySide2.QtGui import *
	from PySide2.QtWidgets import *
except:
	from PySide.QtCore import *
	from PySide.QtGui import *

qapp = QApplication.instance()

if qapp == None:
	qapp = QApplication(sys.argv)

	import PrismCore
	pcore = PrismCore.PrismCore(app="Fusion")
	pcore.appPlugin.fusion = fusion

	curPrj = pcore.getConfig("globals", "current project")
	if curPrj is not None and curPrj != "":
		pcore.changeProject(curPrj, openUi="") # projectBrowser
	else:
		pcore.projects.setProject(openUi="projectBrowser")

	pcore.sceneOpen()

	qapp.exec_()