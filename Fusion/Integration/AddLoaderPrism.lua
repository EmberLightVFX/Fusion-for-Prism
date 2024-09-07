-- AddLoaderPrism.lua
--[[
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
]]


local comp = fusion:GetCurrentComp()
if not comp then
    print("[Prism Error] No active composition found.")
    return
end

local flow = comp.CurrentFrame.FlowView
local tool = comp.ActiveTool
local x, y = flow:GetPos(tool)

-- Unselect all tools
flow:Select(nil, false)

-- Load and paste the LoaderPrism macro
local loaderLoc = comp:MapPath('Macros:/LoaderPrism.setting')
local loaderText = bmd.readfile(loaderLoc)
if loaderText then
    comp:Paste(loaderText)

    -- Get the added LoaderPrism tool
    local loader = comp.ActiveTool

    -- Set the Clip property
    flow:SetPos(loader, x, y + 1)

    -- Connect inputs to the loader output
    local inputs = tool.Output:GetConnectedInputs()
    for _, input in ipairs(inputs) do
        input:ConnectTo(loader.Output)
    end

    if not bmd.fileexists(name) then
        print("File not found:", name)
    end
else
    print("[Prism Error] LoaderPrism setting file not found.")
end
