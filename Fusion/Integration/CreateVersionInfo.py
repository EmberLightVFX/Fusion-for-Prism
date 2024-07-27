# -*- coding: utf-8 -*-
#
####################################################
#
# PRISM - Pipeline for animation and VFX projects
#
# www.prism-pipeline.com
#
# contact: contact@prism-pipeline.com
#
####################################################
#
#
# Copyright (C) 2016-2023 Richard Frangenberg
# Copyright (C) 2023 Prism Software GmbH
#
# Licensed under GNU LGPL-3.0-or-later
#
# This file is part of Prism.
#
# Prism is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Prism is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Prism.  If not, see <https://www.gnu.org/licenses/>.
###########################################################################
#
#                BMD Fusion Studio Plugin for Prism2
#
#                        Original code by:
#                          EmberLightVFX
#           https://github.com/EmberLightVFX/Fusion-for-Prism
#
#
#                       Updated for Prism2 by:
#                           Joshua Breckeen
#                              Alta Arts
#                          josh@alta-arts.com
#
###########################################################################


import os
import sys

prismRoot = os.getenv("PRISM_ROOT")
if not prismRoot:
    prismRoot = PRISMROOT

sys.path.insert(0, os.path.join(prismRoot, "PythonLibs", "Python3"))
sys.path.insert(0, os.path.join(prismRoot, "PythonLibs", "Python311"))
sys.path.insert(0, os.path.join(prismRoot, "Scripts"))

import PrismCore

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

qapp = QApplication.instance()
if qapp == None:
    qapp = QApplication(sys.argv)

#	Make PrismObject
pcore = PrismCore.PrismCore(app="Fusion")

#	Pass Fusion Scripting objects to Fusion plugin
pcore.appPlugin.bmd = bmd
pcore.appPlugin.fusion = fusion

curPrj = pcore.getConfig('globals', 'current project')

if curPrj is not None and curPrj != "":
	pcore.changeProject(curPrj)
	tool = comp.ActiveTool

	try:
		versionPath = tool.GetAttrs()["TOOLST_Clip_Name"][1]
		
		infoPath = pcore.mediaProducts.getMediaVersionInfoPathFromFilepath(versionPath, mediaType="2drenders")
		curfile = pcore.getCurrentFileName()
		details = pcore.getScenefileData(curfile, getEntityFromPath=True)

		details["identifier"] = tool.GetInput("PrismMediaIDControl")
		details["comment"] = tool.GetInput("PrismCommentControl")
		details["mediaType"] = "2drenders"
		details["versionpaths"] = os.path.dirname(versionPath)
		del details["version"]

		pcore.saveVersionInfo(filepath=os.path.dirname(infoPath), details=details)

	except:
		print("Unable to create versionInfo file.")

else:
	pcore.popup("No project is active.\nPlease set a project in the Prism Settings or by opening the Project Browser.")
