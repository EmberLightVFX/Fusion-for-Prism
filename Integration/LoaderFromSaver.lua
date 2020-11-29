-- Description: 
-- Create a Loader from selected Saver node. Works with multiple Savers.
-- Features:
-- If the Saver has image sequence with no number padding, scan existing files and suggest correct sequence numbering 
-- If the file is a container (mov, avi, mp4, mxf) — original name is used. 
-- Launch this scripts with Saver Manager UI tool (available in Reactor) 
-- connect the created Loader to Saver's downstream nodes 
-- convert regular saver to Saver Plus 
-- add versioning buttons to Saver Plus 
--
-- License: MIT
-- Author: Alexey Bogomolov
-- email: mail@abogomolov.com
-- Donate: paypal.me/aabogomolov/2usd
-- Version: 1.2, 2020/27/11

comp = fu:GetCurrentComp()

selectedSavers = comp:GetToolList(true, 'Saver')

local platform = (FuPLATFORM_WINDOWS and 'Windows') or (FuPLATFORM_MAC and 'Mac') or (FuPLATFORM_LINUX and 'Linux')

local listDirCmd = "ls "
local suffixCmd = ""

if platform == "Windows" then
    listDirCmd = "dir "
    suffixCmd = " /b"
end

if comp:GetAttrs("COMPS_FileName") == "" then
    print('save the comp!')
end



function isMovieFormat(extension)
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

function findFiles(parsedPath)
    files = assert(io.popen(listDirCmd .. comp:MapPath(parsedPath.Path) .. suffixCmd))

    for file in files:lines() do
        base, snum, ext = string.match(file,"^(.+[._-])(%d+)(%..+)$")
        if base == parsedPath.CleanName then
            return snum or "0000"
        end
    end
    files:close()
    return nil

end

function placeAndReconnect(name, tool)
    local flow = comp.CurrentFrame.FlowView
    x, y = flow:GetPos(tool)
    local loader = comp:AddTool("Loader")
    loader.Clip = name
    flow:SetPos(loader, x+1, y)
    inputs = tool.Output:GetConnectedInputs()
    for i, input in ipairs(inputs) do
        input:ConnectTo(loader.Output)
    end
    if not bmd.fileexists(comp:MapPath(name)) then
        print("file is not found ", name)
    end
end

if (#selectedSavers) == 0 then
    print('select some savers')
else
    comp:Lock()
    comp:StartUndo('loader from saver')
    for _, tool in ipairs(selectedSavers) do
        selectedClipName = tool.Clip[1]
        if selectedClipName == "" then
            print("Saver " .. tool.Name .. ": filename is empty!")
        else
            parsedFile = bmd.parseFilename(selectedClipName)
            ext = parsedFile.Extension:lower()
            path = parsedFile.Path
            cleanName = parsedFile.CleanName
            sequenceNumber = parsedFile.SNum 

            -- if it is a sequence, find actual seq number
            if not isMovieFormat(ext) then
                if not sequenceNumber or not bmd.fileexists(comp:MapPath(selectedClipName)) then
                    suggestedSnum = findFiles(parsedFile)
                    if not suggestedSnum then
                        newClipName = selectedClipName
                    else
                        print("starting sequence number for the new loader is set to: ".. suggestedSnum)
                        newClipName = path .. cleanName .. suggestedSnum .. ext
                    end
                else
                    newClipName = path .. cleanName .. sequenceNumber .. ext
                end
            else
                newClipName = selectedClipName
            end

            placeAndReconnect(newClipName, tool)
        end
    end
    comp:EndUndo()
    comp:Unlock()
end
