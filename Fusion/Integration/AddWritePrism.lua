-- AddWritePrism.lua
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
local loaderLoc = comp:MapPath('Macros:/WritePrism.setting')
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
