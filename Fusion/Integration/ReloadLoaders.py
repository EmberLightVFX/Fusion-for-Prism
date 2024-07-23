"""""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """'
ReloadLoaders
-------------
Version: v1.03
Last update: 24 Sep 2019

Description:The ReloadLoaders script will refresh all or selected Loader nodes in your comp
            by rereading the "clip" filename attribute so it also updates the footage
            for the full duration of the sequence.

Installation: copy AlbertoGZ/ReloadLoaders folder in your Fusion:/Scripts/Comp/

Author: AlbertoGZ
Email: albertogzgz@gmail.com
Website: albertogz.com

""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """"""

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
