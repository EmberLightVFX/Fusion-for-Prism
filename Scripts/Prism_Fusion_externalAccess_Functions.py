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
# Copyright (C) 2016-2020 Richard Frangenberg
#
# Licensed under GNU GPL-3.0-or-later
#
# This file is part of Prism.
#
# Prism is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Prism is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Prism.  If not, see <https://www.gnu.org/licenses/>.

import os

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class Prism_Fusion_externalAccess_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

        self.core.registerCallback(
            "userSettings_saveSettings",
            self.userSettings_saveSettings,
            plugin=self.plugin,
            )
        self.core.registerCallback(
            "userSettings_loadSettings",
            self.userSettings_loadSettings,
            plugin=self.plugin,
            )
        self.core.registerCallback("getPresetScenes", self.getPresetScenes, plugin=self.plugin)

        ssheetPath = os.path.join(
            self.pluginDirectory,
            "UserInterfaces",
            "FusionStyleSheet"
            )
        
        self.core.registerStyleSheet(ssheetPath)


    @err_catcher(name=__name__)
    def userSettings_loadUI(self, origin, tab):
        origin.chb_fusionOpenPrism = QCheckBox("Open Project Browser on startup")
        tab.layout().addWidget(origin.chb_fusionOpenPrism)


    @err_catcher(name=__name__)
    def userSettings_saveSettings(self, origin, settings):
        if "fusion" not in settings:
            settings["fusion"] = {}

        settings["fusion"]["openprism"] = origin.chb_fusionOpenPrism.isChecked()


    @err_catcher(name=__name__)
    def userSettings_loadSettings(self, origin, settings):
        if "fusion" in settings:
            if "openprism" in settings["fusion"]:
                origin.chb_fusionOpenPrism.setChecked(settings["fusion"]["openprism"])
        else:
            origin.chb_fusionOpenPrism.setChecked(True)
            settings["fusion"] = {}
            settings["fusion"]["openprism"] = origin.chb_fusionOpenPrism.isChecked()


    @err_catcher(name=__name__)
    def getAutobackPath(self, origin, tab):
        autobackpath = ""

        fileStr = "Fusion Composition ("
        for i in self.sceneFormats:
            fileStr += "*%s " % i

        fileStr += ")"

        return autobackpath, fileStr
    

    @err_catcher(name=__name__)
    def getPresetScenes(self, presetScenes):
        presetDir = os.path.join(self.pluginDirectory, "Presets")
        scenes = self.core.entities.getPresetScenesFromFolder(presetDir)
        presetScenes += scenes

