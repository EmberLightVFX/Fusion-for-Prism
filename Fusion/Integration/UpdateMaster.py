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
if qapp is None:
    qapp = QApplication(sys.argv)

# Make PrismObject
pcore = PrismCore.PrismCore(app="Fusion")

# Pass Fusion Scripting objects to Fusion plugin
pcore.appPlugin.bmd = bmd
pcore.appPlugin.fusion = fusion

curPrj = pcore.getConfig('globals', 'current project')
if curPrj is not None and curPrj != "":
    pcore.changeProject(curPrj)
    tool = comp.ActiveTool

    #   Gets the Media Identifier from the WritePrism tool
    MediaID = tool.GetInput("PrismMediaIDControl")
    if MediaID is None or MediaID == "":
        pcore.popup("Please choose a Media Identifier.", title="Media Identifier")
    
    try:
        #   Get directory from image path of Saver
        versionPath = os.path.dirname(tool.GetAttrs()["TOOLST_Clip_Name"][1])
        if not os.path.exists(versionPath):
            versionPath = os.path.dirname(versionPath)
    except:
        versionPath = ""
    
    #   Get version number from dir name
    versionNumber = os.path.basename(versionPath)
    
    if os.path.exists(versionPath):
        #   Get details and add more
        curfile = pcore.getCurrentFileName()
        context = pcore.getScenefileData(curfile, getEntityFromPath=True)
        context["identifier"] = tool.GetInput("PrismMediaIDControl")
        context["path"] = versionPath

        try:
            #   Trigger Update Master in Prism
            result = pcore.mediaProducts.updateMasterVersion(
                                                            path=versionPath,
                                                            context=context,
                                                            isFilepath=False,
                                                            add=False,
                                                            mediaType="2drenders"
                                                            )

            if result:
                pcore.popup(f"Master updated to {versionNumber}.")

            else:
                pcore.popup("Failed to update Master version.")
        
        except Exception as e:
            pcore.popup(f"Error updating master version: {str(e)}")
    else:
        pcore.popup("The output folder doesn't exist yet.")
else:
    pcore.popup("No project is active.\nPlease set a project in the Prism Settings or by opening the Project Browser.")
