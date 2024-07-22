import os
import sys

prismRoot = os.getenv("PRISM_ROOT")
if not prismRoot:
    prismRoot = PRISMROOT

sys.path.append(os.path.join(prismRoot, "Scripts"))


from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

qapp = QApplication.instance()
if qapp == None:
  qapp = QApplication(sys.argv)

import PrismCore
pcore = PrismCore.PrismCore(app='Fusion', prismArgs=["parentWindows"])
pcore.appPlugin.fusion = fusion

curPrj = pcore.getConfig('globals', 'current project')
if curPrj is not None and curPrj != "":
	pcore.changeProject(curPrj)
	tool = comp.ActiveTool
	pcore.appPlugin.getOutputPath(tool)
else:
	QMessageBox.warning(pcore.messageParent, "Prism warning", "No project is active.\nPlease set a project in the Prism Settings or by opening the Project Browser.")
