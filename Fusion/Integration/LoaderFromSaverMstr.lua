-- Description: 
-- Create a Loader from selected Saver node. Works with multiple selected selectedSavers.
-- License: MIT
-- Author: Alex Bogomolov
-- email: mail@abogomolov.com
-- Donate: paypal.me/aabogomolov
-- Version: 1.1, 2020/9/1

--Edited for use with PrismPipeline plugin

comp = fu:GetCurrentComp()
selectedSavers = comp:GetToolList(true, 'Saver')

-- Load the LoaderPrism macro and set it up
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

-- Deal with extensions
function pathIsMovieFormat(path)
    local extension = bmd.parseFilename(path).Extension:lower()
    local movieExtensions = {
        ".3gp", ".aac", ".aif", ".aiff", ".avi", ".dvs", ".fb", ".flv",
        ".m2ts", ".m4a", ".m4b", ".m4p", ".mkv", ".mov", ".mp3", ".mp4",
        ".mts", ".mxf", ".omf", ".omfi", ".qt", ".stm", ".tar", ".vdr",
        ".vpv", ".wav", ".webm"
    }
    for _, ext in ipairs(movieExtensions) do
        if ext == extension then
            return true
        end
    end
    return false
end

if (#selectedSavers) == 0 then
    print('Select some savers.')
else
    comp:Lock()
    comp:StartUndo('Loader from Saver')
    for _, tool in ipairs(selectedSavers) do
        local selected_clipname = tool:GetAttrs()["TOOLST_Clip_Name"][1]
        if selected_clipname == "" then
            print(tool.Name .. " filename is empty!")
        else
            -- Parse the filename to get the path and the file
            local parsedFilename = bmd.parseFilename(selected_clipname)
            local directoryPath = parsedFilename.Path
            local fileName = parsedFilename.FullName

            -- Match and replace the version directory with "master"
            local newDirectoryPath = directoryPath:gsub("[/\\][vV]%d+", "/master")

            -- Replace the version number in the file name with "master"
            local newFileName = fileName:gsub("[vV]%d+", "master")

            -- Combine the new directory path with the new file name
            local newFilePath = newDirectoryPath .. "/" .. newFileName

            -- Check if it's a sequence or movie format
            local match_sequence_number = string.match(selected_clipname, '(%d+)%..$')

            -- If pattern 0000.ext$ is found or file is a movie container, set the name as is
            if match_sequence_number or pathIsMovieFormat(comp:MapPath(selected_clipname)) then
                place_loader(newFilePath, tool)
            else
                local name, ext = string.match(newFilePath, '([^/]-([^.]+))$')
                local new_name = newFilePath:gsub('.'..ext, '0000.'..ext)
                place_loader(new_name, tool)
            end
        end
    end
    comp:EndUndo()
    comp:Unlock()
    if comp:GetAttrs("COMPS_FileName") == "" and comp:IsLocked() then
        print('Save the comp!')
    end
end

