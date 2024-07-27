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
import platform
import shutil

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class Prism_Fusion_Integration(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

        if platform.system() == "Windows":
            self.examplePath = os.path.join(
                os.environ["appdata"], "Blackmagic Design", "Fusion"
                )
        elif platform.system() == "Linux":
            userName = (
                os.environ["SUDO_USER"]
                if "SUDO_USER" in os.environ
                else os.environ["USER"]
                )
            self.examplePath = "/home/%s/.fusion/BlackmagicDesign/Fusion" % userName
        elif platform.system() == "Darwin":
            userName = (
                os.environ["SUDO_USER"]
                if "SUDO_USER" in os.environ
                else os.environ["USER"]
                )
            self.examplePath = (
                "/Users/%s/Library/Application Support/Blackmagic Design/Fusion"
                % userName
                )

        #   Files to be used in Integration
        self.prismFuPrismDirFiles = ["SaveVersion.py",
                                    "SaveComment.py",
                                    "UpdateLoadNodes.py",
                                    "OpenProjectBrowser.py",
                                    "OpenSettings.py",
                                    "OpenInExplorer.py",
                                    "RefreshLocation.py",
                                    "RefreshWriter.py",
                                    # "SceneOpen.py",       #   commented out - needed for scene open checks - but has memory leak
                                    "LoaderFromSaver.lua",
                                    "LoaderFromSaverMstr.lua",
                                    "Pre-RenderCheck.py",
                                    "RefreshMediaID.py",
                                    "ReloadLoaders.py",
                                    "UpdateMaster.py",
                                    "AddLoaderPrism.lua",
                                    "AddWritePrism.lua",
                                    "CreateVersionInfo.py"]
        
        self.prismFuConfigDirFiles = ["PrismEvents.fu",
                                    "PrismMenu.fu"]
        
        self.prismFuScriptsDirFiles = ["PrismInit.scriptlib"]

        self.prismFuMacroDirFiles = ["WritePrism.setting", "LoaderPrism.setting"]
    

    @err_catcher(name=__name__)
    def getExecutable(self):
        execPath = ""
        if platform.system() == "Windows":
            execPath = "C:\\Program Files\\Blackmagic Design\\Fusion 9\\Fusion.exe"

        return execPath
    

    def addIntegration(self, installPath):
        try:
            if not os.path.exists(installPath):
                QMessageBox.warning(
                    self.core.messageParent,
                    "Prism Integration",
                    "Invalid Fusion path: %s.\nThe path doesn't exist." % installPath,
                    QMessageBox.Ok,
                )
                return False

            integrationBase = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "Integration"
            )
            addedFiles = []

            # "PrismMenu.fu" add a Prism menu, but leads to freezes
            for i in self.prismFuConfigDirFiles:
                origFile = os.path.join(integrationBase, i)
                targetFile = os.path.join(installPath, "Config", i)

                if not os.path.exists(os.path.dirname(targetFile)):
                    os.makedirs(os.path.dirname(targetFile))
                    addedFiles.append(os.path.dirname(targetFile))

                if os.path.exists(targetFile):
                    os.remove(targetFile)

                shutil.copy2(origFile, targetFile)
                addedFiles.append(targetFile)

                with open(targetFile, "r") as init:
                    initStr = init.read()
                    initStr = initStr.replace(
                        "PRISMROOT", '"%s"' % self.core.prismRoot.replace(
                            "\\", "/")
                    )

                with open(targetFile, "w") as init:
                    init.write(initStr)

            for i in self.prismFuScriptsDirFiles:
                origFile = os.path.join(integrationBase, i)
                targetFile = os.path.join(installPath, "Scripts", i)

                if not os.path.exists(os.path.dirname(targetFile)):
                    os.makedirs(os.path.dirname(targetFile))
                    addedFiles.append(os.path.dirname(targetFile))

                if os.path.exists(targetFile):
                    os.remove(targetFile)

                shutil.copy2(origFile, targetFile)
                addedFiles.append(targetFile)

                with open(targetFile, "r") as init:
                    initStr = init.read()

                with open(targetFile, "w") as init:
                    initStr = initStr.replace(
                        "PRISMROOT", '"%s"' % self.core.prismRoot.replace(
                            "\\", "/")
                    )
                    init.write(initStr)

            for i in self.prismFuPrismDirFiles:

                origFile = os.path.join(integrationBase, i)
                targetFile = os.path.join(installPath, "Scripts", "Prism", i)

                if not os.path.exists(os.path.dirname(targetFile)):
                    os.makedirs(os.path.dirname(targetFile))
                    addedFiles.append(os.path.dirname(targetFile))

                if os.path.exists(targetFile):
                    os.remove(targetFile)

                shutil.copy2(origFile, targetFile)
                addedFiles.append(targetFile)

                with open(targetFile, "r") as init:
                    initStr = init.read()

                with open(targetFile, "w") as init:
                    initStr = initStr.replace(
                        "PRISMROOT", '"%s"' % self.core.prismRoot.replace(
                            "\\", "/")
                    )
                    init.write(initStr)

            for i in self.prismFuMacroDirFiles:
                origFile = os.path.join(integrationBase, i)
                targetFile = os.path.join(installPath, "Macros", i)

                if not os.path.exists(os.path.dirname(targetFile)):
                    os.makedirs(os.path.dirname(targetFile))
                    addedFiles.append(os.path.dirname(targetFile))

                if os.path.exists(targetFile):
                    os.remove(targetFile)

                shutil.copy2(origFile, targetFile)
                addedFiles.append(targetFile)

                with open(targetFile, "r") as init:
                    initStr = init.read()

                with open(targetFile, "w") as init:
                    initStr = initStr.replace(
                        "PRISMROOT", '"%s"' % self.core.prismRoot.replace(
                            "\\", "/")
                    )
                    init.write(initStr)

            if platform.system() in ["Linux", "Darwin"]:
                for i in addedFiles:
                    os.chmod(i, 0o777)

            return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()

            msgStr = (
                "Errors occurred during the installation of the Fusion integration.\nThe installation is possibly incomplete.\n\n%s\n%s\n%s"
                % (str(e), exc_type, exc_tb.tb_lineno)
            )
            msgStr += "\n\nRunning this application as administrator could solve this problem eventually."

            QMessageBox.warning(self.core.messageParent,
                                "Prism Integration", msgStr)
            return False


    def removeIntegration(self, installPath):
        try:
            prismFusionScriptDir = os.path.join(installPath, "Scripts", "Prism")
            if os.path.exists(prismFusionScriptDir):
                shutil.rmtree(prismFusionScriptDir)

            prismFusionConfigDir = os.path.join(installPath, "Config")
            for file in self.prismFuConfigDirFiles:
                delFile = os.path.join(prismFusionConfigDir, file)
                if os.path.exists(delFile):
                    os.remove(delFile)

            scriptLibDir = os.path.join(installPath, "Scripts")
            for file in self.prismFuScriptsDirFiles:
                delFile = os.path.join(scriptLibDir, file)
                if os.path.exists(delFile):
                    os.remove(delFile)

            macrosDir = os.path.join(installPath, "Macros")
            for file in self.prismFuMacroDirFiles:
                delFile = os.path.join(macrosDir, file)
                if os.path.exists(delFile):
                    os.remove(delFile)

            return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()

            msgStr = (
                "Errors occurred during the removal of the Fusion integration.\n\n%s\n%s\n%s"
                % (str(e), exc_type, exc_tb.tb_lineno)
            )
            msgStr += "\n\nRunning this application as administrator could solve this problem eventually."

            QMessageBox.warning(self.core.messageParent,
                                "Prism Integration", msgStr)
            return False
        

    def updateInstallerUI(self, userFolders, pItem):
        try:
            pluginItem = QTreeWidgetItem([self.plugin.pluginName])
            pItem.addChild(pluginItem)

            pluginPath = self.examplePath

            if pluginPath != None and os.path.exists(pluginPath):
                pluginItem.setCheckState(0, Qt.Checked)
                pluginItem.setText(1, pluginPath)
                pluginItem.setToolTip(0, pluginPath)
            else:
                pluginItem.setCheckState(0, Qt.Unchecked)
                pluginItem.setText(1, "< doubleclick to browse path >")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            msg = QMessageBox.warning(
                self.core.messageParent,
                "Prism Installation",
                "Errors occurred during the installation.\n The installation is possibly incomplete.\n\n%s\n%s\n%s\n%s"
                % (__file__, str(e), exc_type, exc_tb.tb_lineno),
            )
            return False

    def installerExecute(self, fusionItem, result):
        try:
            installLocs = []

            if fusionItem.checkState(0) == Qt.Checked and os.path.exists(
                fusionItem.text(1)
            ):
                result["Fusion integration"] = self.core.integration.addIntegration(
                    self.plugin.pluginName, path=fusionItem.text(1), quiet=True)
                if result["Fusion integration"]:
                    installLocs.append(fusionItem.text(1))

            return installLocs
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            msg = QMessageBox.warning(
                self.core.messageParent,
                "Prism Installation",
                "Errors occurred during the installation.\n The installation is possibly incomplete.\n\n%s\n%s\n%s\n%s"
                % (__file__, str(e), exc_type, exc_tb.tb_lineno),
            )
            return False
