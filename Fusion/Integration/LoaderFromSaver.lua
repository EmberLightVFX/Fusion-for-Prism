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
#
#   Original Script by:
#
#       Description: 
#           Create a Loader from selected Saver node. Works with multiple selected selectedSavers.
#       License: MIT
#       Author: Alex Bogomolov
#       email: mail@abogomolov.com
#       Donate: paypal.me/aabogomolov
#       Version: 1.1, 2020/9/1
#
#       Modified for use in Prism2
#
###########################################################################
]]

comp = fu:GetCurrentComp()
selectedSavers = comp:GetToolList(true, 'Saver')

function place_loader(name, tool)
    local flow = comp.CurrentFrame.FlowView
    x, y = flow:GetPos(tool)

    -- Unselect all tools
    flow:Select(nil, false)

    -- Load and paste the LoaderPrism macro
    local loaderLoc = comp:MapPath('Macros:/LoaderPrism.setting')
    local loaderText = bmd.readfile(loaderLoc)
    comp:Paste(loaderText)

    -- Get the added LoaderPrism tool
    local loader = comp.ActiveTool

    -- Set the Clip property
    loader.Clip = name
    flow:SetPos(loader, x, y + 1)

    inputs = tool.Output:GetConnectedInputs()
    for i, input in ipairs(inputs) do
        input:ConnectTo(loader.Output)
    end

    if not bmd.fileexists(name) then
        print("File not found:", name)
        local parseFile = bmd.parseFilename(name)
    end
end


function pathIsMovieFormat(path)
    local extension = bmd.parseFilename(path).Extension:lower()
    if extension ~= nil then
        if  ( extension == ".3gp" ) or
            ( extension == ".aac" ) or
            ( extension == ".aif" ) or
            ( extension == ".aiff" ) or
            ( extension == ".avi" ) or
            ( extension == ".dvs" ) or
            ( extension == ".fb" ) or
            ( extension == ".flv" ) or
            ( extension == ".m2ts" ) or
            ( extension == ".m4a" ) or
            ( extension == ".m4b" ) or
            ( extension == ".m4p" ) or
            ( extension == ".mkv" ) or
            ( extension == ".mov" ) or
            ( extension == ".mp3" ) or
            ( extension == ".mp4" ) or
            ( extension == ".mts" ) or
            ( extension == ".mxf" ) or
            ( extension == ".omf" ) or
            ( extension == ".omfi" ) or
            ( extension == ".qt" ) or
            ( extension == ".stm" ) or
            ( extension == ".tar" ) or
            ( extension == ".vdr" ) or
            ( extension == ".vpv" ) or
            ( extension == ".wav" ) or
            ( extension == ".webm" ) then
            return true
        end
    end
    return false
end

if (#selectedSavers) == 0 then
    print('select some savers')
else
    comp:Lock()
    comp:StartUndo('loader from saver')
    for _, tool in ipairs(selectedSavers) do
        selected_clipname = tool:GetAttrs()["TOOLST_Clip_Name"][1]
        if selected_clipname == "" then
            print(tool.Name .. " filename is empty!")
        else
            match_sequence_number = string.match(selected_clipname, '(%d+)%..$')
            --ext = string.match(selected_clipname, '(%.%w+)$')
            --match_sequence_number = string.match(selected_clipname, '(%d+)' .. ext .. '$')

            -- if pattern 0000.ext$ is found or file is a movie container, set the name as is
            if match_sequence_number or pathIsMovieFormat(comp:MapPath(selected_clipname)) then
                place_loader(selected_clipname, tool)
            else
                name, ext = string.match(selected_clipname,'([^/]-([^.]+))$')
                local new_name = selected_clipname:gsub('.'..ext, '0000.'..ext)
                place_loader(new_name, tool)
            end
        end
    end
    comp:EndUndo()
    comp:Unlock()
    if comp:GetAttrs("COMPS_FileName") == "" and comp:IsLocked() then
        print('save the comp!')
    end
end

