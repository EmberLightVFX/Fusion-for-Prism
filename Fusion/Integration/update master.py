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
        versionPath = os.path.dirname(tool.GetAttrs()["TOOLST_Clip_Name"][1])
        if not os.path.exists(versionPath):
            versionPath = os.path.dirname(versionPath)
    except:
        versionPath = ""
    
    versionNumber = os.path.basename(versionPath)
    
    if os.path.exists(versionPath):
        curfile = pcore.getCurrentFileName()
        context = pcore.getScenefileData(curfile, getEntityFromPath=True)
        context["identifier"] = tool.GetInput("PrismMediaIDControl")
        context["path"] = versionPath

        try:
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
