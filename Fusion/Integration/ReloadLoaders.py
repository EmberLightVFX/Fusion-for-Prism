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
#
#
#       ReloadLoaders
#       -------------
#       Version: v1.03
#       Last update: 24 Sep 2019
#
#       Description:The ReloadLoaders script will refresh all or selected Loader nodes in your comp
#                   by rereading the "clip" filename attribute so it also updates the footage
#                   for the full duration of the sequence.
#
#       Installation: copy AlbertoGZ/ReloadLoaders folder in your Fusion:/Scripts/Comp/
#
#       Author: AlbertoGZ
#       Email: albertogzgz@gmail.com
#       Website: albertogz.com
#
#
#       Modified for use with Prism
#
###########################################################################


allLoaders = comp.GetToolList(False, "Loader").values()
selLoaders = comp.GetToolList(True, "Loader").values()

# Check if selection and builds list with Loaders in,
# otherwise list inlcude all Loaders
if selLoaders:
    toollist = selLoaders
else:
    toollist = allLoaders

# add comp lock to remove prompt window
comp.Lock()
# Evaluate Loaders in list
for tool in toollist:
    loaderPath = tool.GetAttrs("TOOLST_Clip_Name")
    loaderName = tool.GetAttrs("TOOLS_Name")
    loaderPathClean = loaderPath[1]
    durationOld = tool.GetAttrs("TOOLIT_Clip_Length")
    durationOldClean = durationOld[1]

    # Rename the clipname to force reload duration
    tool.Clip = loaderPathClean + ""
    tool.Clip = loaderPathClean
    durationNew = tool.GetAttrs("TOOLIT_Clip_Length")
    durationNewClean = durationNew[1]

    # Disable/enable to reload clip cache
    tool.SetAttrs({"TOOLB_PassThrough": True})
    tool.SetAttrs({"TOOLB_PassThrough": False})

    # Outputs
    print(loaderName + " has been reloaded.")
    print(" + current filename: " + tool.Clip[0])
    print(" + old duration: " + str(durationOldClean) + " frames")
    print(" + new duration: " + str(durationNewClean) + " frames")
    print("")
comp.Unlock()
