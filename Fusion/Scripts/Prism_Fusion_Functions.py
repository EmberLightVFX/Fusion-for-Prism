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
import re
import glob
import shutil

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from PrismUtils.Decorators import err_catcher as err_catcher


class Prism_Fusion_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin
        self.prismRoot = os.path.normpath(self.core.prismRoot)

        self.core.registerCallback("getIconPathForFileType",
                                   self.getIconPathForFileType,
                                   plugin=self)


    @err_catcher(name=__name__)
    def instantStartup(self, origin):
        qapp = QApplication.instance()

        ssFile = os.path.join(self.pluginDirectory,
                                "UserInterfaces",
                                "FusionStyleSheet",
                                "Fusion.qss")

        with (open(ssFile, "r",)) as ssFile:
            ssheet = ssFile.read()

        ssheet = ssheet.replace("qss:", os.path.join(self.pluginDirectory,
                                                     "UserInterfaces",
                                                     "FusionStyleSheet",
                                                     ).replace("\\", "/") + "/")

        self.core.setActiveStyleSheet("Fusion")
        
        if "parentWindows" in origin.prismArgs:
            # origin.messageParent.setStyleSheet(ssheet)
            #   origin.messageParent.resize(10,10)
            #   origin.messageParent.show()
            origin.parentWindows = True
        else:
            qapp = QApplication.instance()
            qapp.setStyleSheet(ssheet)
            appIcon = QIcon(
                os.path.join(
                    self.prismRoot, "Scripts", "UserInterfacesPrism", "p_tray.png"
                    )
                )
            qapp.setWindowIcon(appIcon)

        self.isRendering = [False, ""]

        return False
    
    #   Adds custom icon for Fusion auto-backup files
    @err_catcher(name=__name__)
    def getIconPathForFileType(self, extension):
        if extension == ".autocomp":
            icon = os.path.join(self.pluginDirectory, "UserInterfaces", "Fusion-Autosave.ico")
            return icon

        return None


    @err_catcher(name=__name__)
    def startup(self, origin):
        if not hasattr(self, "fusion"):
            return False

        origin.timer.stop()
        return True


    @err_catcher(name=__name__)
    def onProjectChanged(self, origin):
        pass


    @err_catcher(name=__name__)
    def sceneOpen(self, origin):
        if hasattr(origin, "asThread") and origin.asThread.isRunning():
            origin.startasThread()


    @err_catcher(name=__name__)
    def executeScript(self, origin, code, preventError=False):
        if preventError:
            try:
                return eval(code)
            except Exception as e:
                msg = "\npython code:\n%s" % code
                exec(
                    "raise type(e), type(e)(e.message + msg), sys.exc_info()[2]")
        else:
            return eval(code)
        

    @err_catcher(name=__name__)
    def getCurrentFileName(self, origin, path=True):
        curComp = self.fusion.GetCurrentComp()
        if curComp is None:
            currentFileName = ""
        else:
            currentFileName = self.fusion.GetCurrentComp().GetAttrs()[
                "COMPS_FileName"]

        return currentFileName
    

    @err_catcher(name=__name__)
    def getSceneExtension(self, origin):
        return self.sceneFormats[0]


    @err_catcher(name=__name__)
    def saveScene(self, origin, filepath, details={}):
        try:
            return self.fusion.GetCurrentComp().Save(filepath)
        except:
            return ""


    @err_catcher(name=__name__)
    def captureViewportThumbnail(self):
        #   Make temp dir and file
        tempDir = os.path.join(self.pluginDirectory, "Temp")
        if not os.path.exists(tempDir):
            os.mkdir(tempDir)
        thumbPath = os.path.join(tempDir, "FusionThumb.jpg")
        thumbName = os.path.basename(thumbPath).split('.')[0]

        #   Get Fusion API stuff
        comp = self.fusion.GetCurrentComp()
        flow = comp.CurrentFrame.FlowView

        comp.Lock()
        comp.StartUndo()

        thumbSaver = None
        origSaverList = {}

        #   Get tool through logic (Selected or Saver or last)
        thumbTool = self.findThumbnailTool(comp)

        if thumbTool:
            #   Save pass-through state of all savers
            origSaverList = self.origSaverStates("save", comp, origSaverList)

            # Add a Saver tool to the composition
            thumbSaver = comp.AddTool("Saver", -32768, -32768, 1)

            # Connect the Saver tool to the currently selected tool
            thumbSaver.Input = thumbTool

            # Set the path for the Saver tool
            thumbSaver.Clip = os.path.join(tempDir, thumbName + ".jpg")

            #   Get current frame number
            currFrame = comp.CurrentTime

            origStartFrame = comp.GetAttrs("COMPN_RenderStart")
            origEndFrame = comp.GetAttrs("COMPN_RenderEnd")

            # Temporarily set the render range to the current frame
            comp.SetAttrs({'COMPN_RenderStart' : currFrame})
            comp.SetAttrs({'COMPN_RenderEnd' : currFrame})

            # Render the current frame
            comp.Render()  # Trigger the render

            # Restore the original render range
            comp.SetAttrs({'COMPN_RenderStart' : origStartFrame})
            comp.SetAttrs({'COMPN_RenderEnd' : origEndFrame})

        #   Deals with the frame number suffix added by Fusion rener
        pattern = os.path.join(tempDir, thumbName + "*.jpg")
        renderedThumbs = glob.glob(pattern)

        if renderedThumbs:
            renderedThumb = renderedThumbs[0]  # Assuming only one matching file
            os.rename(renderedThumb, thumbPath)

        comp.EndUndo()
        comp.Undo()

        if thumbSaver:
            try:
                thumbSaver.Delete()
            except:
                pass

        #   Restore pass-through state of orig savers
        self.origSaverStates("load", comp, origSaverList)

        comp.Unlock()

        #   Get pixmap from Prism
        pm = self.core.media.getPixmapFromPath(thumbPath)

        #   Delete temp dir
        if os.path.exists(tempDir):
            shutil.rmtree(tempDir)

        return pm


    # Handle Savers pass-through state for thumb capture
    @err_catcher(name=__name__)
    def origSaverStates(self, mode, comp, origSaverList):
        for tool in comp.GetToolList(False).values():
            if self.isSaver(tool):
                tool_name = tool.GetAttrs()["TOOLS_Name"]
                if mode == "save":
                    # Save the current pass-through state
                    origSaverList[tool_name] = tool.GetAttrs()["TOOLB_PassThrough"]
                    # Set the tool to pass-through
                    tool.SetAttrs({"TOOLB_PassThrough": True})
                elif mode == "load":
                    # Restore the original pass-through state
                    if tool_name in origSaverList:
                        tool.SetAttrs({"TOOLB_PassThrough": origSaverList[tool_name]})

        return origSaverList
    

    #   Finds the tool to use for the thumbnail in priority
    @err_catcher(name=__name__)
    def findThumbnailTool(self, comp):
        # 1. Check the selected tool
        currTool = comp.ActiveTool
        if currTool:
            return currTool

        # 2. Check for any saver that is not pass-through
        for tool in comp.GetToolList(False).values():
            if self.isSaver(tool) and not self.isPassThrough(tool):
                return tool

        # 3. Check for any saver, even if pass-through
        for tool in comp.GetToolList(False).values():
            if self.isSaver(tool):
                return tool

        # 4. Fallback to the final tool in the flow
        return self.getLastTool(comp) or None


    #   Checks if tool is a Saver, or custom Saver type
    @err_catcher(name=__name__)
    def isSaver(self, tool):
        # Check if tool is valid
        if not tool:
            return False
        # Check if tool name is 'Saver' (should work if node is renamed)
        if tool.GetAttrs({"TOOLS_Name"})["TOOLS_RegID"] == "Saver":
            return True

        return False


    # Checks if tool is set to pass-through mode
    @err_catcher(name=__name__)
    def isPassThrough(self, tool):
        return tool and tool.GetAttrs({"TOOLS_Name"})["TOOLB_PassThrough"]


    #   Tries to find last tool in the flow
    @err_catcher(name=__name__)
    def getLastTool(self, comp):
        try:
            for tool in comp.GetToolList(False).values():
                if not self.hasConnectedOutputs(tool):
                    return tool
        except:
            return None


    #   Finds if tool has any outputs connected
    @err_catcher(name=__name__)
    def hasConnectedOutputs(self, tool):
        if not tool:
            return False

        outputList = tool.GetOutputList()
        for output in outputList.values():
            if output is not None and hasattr(output, 'GetConnectedInput'):
                # Check if the output has any connected inputs in other tools
                try:
                    connection = output.GetConnectedInputs()
                    if connection != {}:
                        return True
                except:
                    return False

        return False


    @err_catcher(name=__name__)
    def getImportPaths(self, origin):
        return False


    @err_catcher(name=__name__)
    def getFrameRange(self, origin):
        startframe = self.fusion.GetCurrentComp().GetAttrs()[
            "COMPN_GlobalStart"]
        endframe = self.fusion.GetCurrentComp().GetAttrs()["COMPN_GlobalEnd"]

        return [startframe, endframe]
    

    @err_catcher(name=__name__)
    def setFrameRange(self, origin, startFrame, endFrame):
        comp = self.fusion.GetCurrentComp()
        comp.Lock()
        comp.SetAttrs(
            {
                "COMPN_GlobalStart": startFrame,
                "COMPN_RenderStart": startFrame,
                "COMPN_GlobalEnd": endFrame,
                "COMPN_RenderEnd": endFrame
            }
        )
        comp.SetPrefs(
            {
                "Comp.Unsorted.GlobalStart": startFrame,
                "Comp.Unsorted.GlobalEnd": endFrame,
            }
        )
        comp.Unlock()


    @err_catcher(name=__name__)
    def getFPS(self, origin):
        fps = self.fusion.GetCurrentComp().GetPrefs()["Comp"]["FrameFormat"]["Rate"]
        return fps
    

    @err_catcher(name=__name__)
    def setFPS(self, origin, fps):
        return self.fusion.GetCurrentComp().SetPrefs({"Comp.FrameFormat.Rate": fps})
    

    @err_catcher(name=__name__)
    def getResolution(self):
        width = self.fusion.GetCurrentComp().GetPrefs()[
            "Comp"]["FrameFormat"]["Width"]
        height = self.fusion.GetCurrentComp().GetPrefs()[
            "Comp"]["FrameFormat"]["Height"]
        return [width, height]


    @err_catcher(name=__name__)
    def setResolution(self, width=None, height=None):
        self.fusion.GetCurrentComp().SetPrefs(
            {
                "Comp.FrameFormat.Width": width,
                "Comp.FrameFormat.Height": height,
            }
        )


###     NOT IMPLEMENTED - FUNCTIONS ADDED TO LoaderPrism TOOL   ###
###     VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV   ###
    # @err_catcher(name=__name__)
    # def updateReadNodes(self):
    #     updatedNodes = []

    #     selNodes = self.fusion.GetCurrentComp().GetToolList(True, "Loader")
    #     if len(selNodes) == 0:
    #         selNodes = self.fusion.GetCurrentComp().GetToolList(False, "Loader")

    #     if len(selNodes):
    #         comp = self.fusion.GetCurrentComp()
    #         comp.StartUndo("Updating loaders")
    #         for k in selNodes:
    #             i = selNodes[k]
    #             curPath = comp.MapPath(i.GetAttrs()["TOOLST_Clip_Name"][1])

    #             # newPath = self.core.getLatestCompositingVersion(curPath)
    #             newPath = self.core.getHighestVersion(curPath)

    #             if os.path.exists(os.path.dirname(newPath)) and not curPath.startswith(
    #                 os.path.dirname(newPath)
    #             ):
    #                 firstFrame = i.GetInput("GlobalIn")
    #                 lastFrame = i.GetInput("GlobalOut")

    #                 i.Clip = newPath

    #                 i.GlobalOut = lastFrame
    #                 i.GlobalIn = firstFrame
    #                 i.ClipTimeStart = 0
    #                 i.ClipTimeEnd = lastFrame - firstFrame
    #                 i.HoldLastFrame = 0

    #                 updatedNodes.append(i)
    #         comp.EndUndo(True)

    #     if len(updatedNodes) == 0:
    #         QMessageBox.information(
    #             self.core.messageParent, "Information", "No nodes were updated"
    #         )
    #     else:
    #         mStr = "%s nodes were updated:\n\n" % len(updatedNodes)
    #         for i in updatedNodes:
    #             mStr += i.GetAttrs()["TOOLS_Name"] + "\n"

    #         QMessageBox.information(
    #             self.core.messageParent, "Information", mStr)

### ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^    ###         


    @err_catcher(name=__name__)
    def getAppVersion(self, origin):
        return self.fusion.Version
    

    @err_catcher(name=__name__)
    def onProjectBrowserStartup(self, origin):
        origin.actionStateManager.setEnabled(False)


    @err_catcher(name=__name__)
    def openScene(self, origin, filepath, force=False):
        if os.path.splitext(filepath)[1] not in self.sceneFormats:
            return False

        try:
            self.fusion.LoadComp(filepath)
        except:
            pass

        return True
    

    @err_catcher(name=__name__)
    def correctExt(self, origin, lfilepath):
        return lfilepath
    

    @err_catcher(name=__name__)
    def setSaveColor(self, origin, btn):
        btn.setPalette(origin.savedPalette)


    @err_catcher(name=__name__)
    def clearSaveColor(self, origin, btn):
        btn.setPalette(origin.oldPalette)


    #   Imports imags from Prism ProjectBrowser Media tab
    @err_catcher(name=__name__)
    def importImages(self, filepath=None, mediaBrowser=None, parent=None):
        #   Gets selected image from RCL
        if mediaBrowser:
            sourceData = mediaBrowser.compGetImportSource()
            if not sourceData:
                return

        #   Adds simple UI popup
        fString = "Please select an import option:"
        buttons = ["Normal", "Separate Passes", "Cancel"]
        result = self.core.popupQuestion(fString, buttons=buttons, icon=QMessageBox.NoIcon, parent=parent)

        if result == "Normal":
            self.fusionImportSource(filepath, sourceData)
        elif result == "Separate Passes":
            self.fusionImportPasses(filepath, sourceData)
        else:
            return
        
    #   Import image from ProjectBrowser
    @err_catcher(name=__name__)
    def fusionImportSource(self, filePath, sourceData):
        comp = self.fusion.GetCurrentComp()
        comp.Lock()

        #   Get image data
        filePathTemplate = sourceData[0][0]
        firstFrame = sourceData[0][1]
        lastFrame = sourceData[0][2]

        #   Frame padding integer
        framePadding = self.core.framePadding

        # Extract filename from the file path template
        fileNameWithPlaceholder = os.path.basename(filePathTemplate)
        fileName = fileNameWithPlaceholder.replace('#' * framePadding, '').replace('.', '')

        # Replace the placeholder '####' with the padded first frame number
        paddedFirstFrame = str(firstFrame).zfill(framePadding)
        filePath = filePathTemplate.replace('#' * framePadding, paddedFirstFrame)

        comp.CurrentFrame.FlowView.Select(None, False)

        #   Add custon Loader tool
        try:
            loaderLoc = comp.MapPath('Macros:/LoaderPrism.setting')
            loaderText = self.bmd.readfile(loaderLoc)
            comp.Paste(loaderText)
            tool = comp.ActiveTool()

        #   Fallback to standard Loader tool
        except:
            print("LoaderPrism is not found.  Using normal Loader.")
            tool = comp.AddTool("Loader", -32768, -32768)

        #   Config Loader with values
        tool.Clip[1] = filePath
        tool.GlobalIn[1] = firstFrame
        tool.GlobalOut[1] = lastFrame
        tool.ClipTimeStart[1] = firstFrame
        tool.ClipTimeEnd[1] = lastFrame
        tool.HoldFirstFrame[1] = 0
        tool.HoldLastFrame[1] = 0
        tool.SetAttrs({"TOOLS_Name": "LoaderPrism"})        #   TODO - look at F2 rename

        comp.Unlock()


    #   Import image and launch EXR splitter if avail
    @err_catcher(name=__name__)
    def fusionImportPasses(self, filePath, sourceData):
        #   Import images
        self.fusionImportSource(filePath, sourceData)

        # Call the splitter script after importing the source
        comp = self.fusion.GetCurrentComp()

        #   Default script name
        script_name = "hos_SplitEXR_Ultra.lua"
        base_dir = comp.MapPath("Scripts:")  # Base directory to start searching

        script_found = False

        # Traverse the base directory and its subdirectories
        # Script usually located in ...\Script\Comp
        for root, dirs, files in os.walk(base_dir):
            if script_name in files:
                script_path = os.path.join(root, script_name)
                script_found = True
                try:
                    #   If found, execute the splitter script
                    comp.RunScript(script_path)
                except Exception as e:
                    self.core.popup(f"There was an error running hos_SplitEXR_Ultra:\n\n: {e}")
                break

        if not script_found:
            self.core.popup(f"'{script_name}' is not found in:\n{base_dir}.....\n\n"
                            f"If the pass functions are desired, please place '{script_name}'\n"
                            "in a Fusion scripts directory.")



### vvvvvvvvv STOPPED DEV TO JUST USE hos_SplitEXR_Ultra VVVVVVVV   ###
###             hos_SplitEXR_Ultra is just very good.               ###
             
        # comp = self.fusion.GetCurrentComp()
        # comp.Lock()

        # sourceImagePath = sourceData[0][0]
        # firstFrame = sourceData[0][1]
        # lastFrame = sourceData[0][2]

        # padding = self.core.framePadding
        # firstFramePadded = ("0" * (padding - 1)) + str(sourceData[0][1])

        # imagePath = sourceImagePath.replace('#' * padding, firstFramePadded)

        # layerNames = self.core.media.getLayersFromFile(imagePath)

        # self.core.popup(f"flayerNames: {layerNames}")                     #    TESTING
        # print(f"flayerNames: {layerNames}")                               #    TESTING


        # # Iterate through each layer to create a Loader node
        # for layer in layerNames:
        #     try:
        #         comp.CurrentFrame.FlowView.Select(None, False)
        #         loaderLoc = comp.MapPath('Macros:/LoaderPrism.setting')
        #         loaderText = self.bmd.readfile(loaderLoc)
        #         comp.Paste(loaderText)
        #         tool = comp.ActiveTool()
        #     except:
        #         print("LoaderPrism is not found. Using normal Loader.")
        #         tool = comp.AddTool("Loader", -32768, -32768)

        #     tool.Clip[1] = imagePath
        #     tool.GlobalIn[1] = firstFrame
        #     tool.GlobalOut[1] = lastFrame
        #     tool.ClipTimeStart[1] = firstFrame
        #     tool.ClipTimeEnd[1] = lastFrame
        #     tool.HoldFirstFrame[1] = 0
        #     tool.HoldLastFrame[1] = 0
        #     tool.SetAttrs({"TOOLS_Name": f"LoaderPrism_{layer}"})  # Set a unique name for each loader

        #     # Set the channels for the loader based on the layer
        #     # Assuming `layer` contains the name of the EXR channel (e.g., 'ALL.AO')

        #     # Set the channels for the loader based on the layer
        #     tool.Red = f"\"{layer}.Red\""
        #     tool.Green = f"\"{layer}.Green\""
        #     tool.Blue = f"\"{layer}.Blue\""
        #     tool.Alpha = f"\"{layer}.Alpha\""

        #     # Set the specific OpenEXR format channels
        #     tool["Clip1.OpenEXRFormat.Channels"] = 1  # Ensure this value is correct for your setup
        #     tool["Clip1.OpenEXRFormat.RedName"] = f"FuID('{layer}.R')"
        #     tool["Clip1.OpenEXRFormat.GreenName"] = f"FuID('{layer}.G')"
        #     tool["Clip1.OpenEXRFormat.BlueName"] = f"FuID('{layer}.B')"
        #     tool["Clip1.OpenEXRFormat.AlphaName"] = f"FuID('{layer}.A')"  # If there's an alpha channel


        # comp.Unlock()
### ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ###



    @err_catcher(name=__name__)
    def setProject_loading(self, origin):
        pass

    @err_catcher(name=__name__)
    def onPrismSettingsOpen(self, origin):
        pass

    @err_catcher(name=__name__)
    def createProject_startup(self, origin):
        pass

    @err_catcher(name=__name__)
    def editShot_startup(self, origin):
        pass

    @err_catcher(name=__name__)
    def shotgunPublish_startup(self, origin):
        pass


    @err_catcher(name=__name__)
    def getOutputPath(self, node, render=False):
        self.isRendering = [False, ""]

        #   Checks if no valid nodes passed
        if node is None:
            self.core.popup("Please select one or more write nodes you wish to refresh")
            return ""

        #   Gets the Media Identifier from the WritePrism tool
        MediaID = node.GetInput("PrismMediaIDControl")
        if MediaID is None or MediaID == "":
            self.core.popup("Please choose a Media Identifier.", title="Media Identifier")
            return ""

        #   Gets the comment from the WritePrism tool
        origComment = node.GetInput("PrismCommentControl")
        if origComment is None:
            comment = ""

        comment = self.core.validateStr(origComment)
        #   If the comment was changed in validation, adds the changed comment to the tool
        if origComment != comment:
            node.SetInput("PrismCommentControl", comment)


        #   Get the output format type
        FormatID = node.GetInput("OutputFormat")

        #   Dict to decode filetype from format
        fileType = {
            "PIXFormat": "pix",             # Alias PIX
            "IFFFormat": "iff",             # Amiga IFF
            "CineonFormat": "cin",          # Kodak Cineon
            "DPXFormat": "dpx",             # DPX
            "FusePicFormat": "fusepic",     # Fuse Pic
            "FlipbookFormat": "fb",         # Fusion Flipbooks
            "RawFormat": "raw",             # Fusion RAW Image
            "IFLFormat": "ifl",             # Image File List (Text File)
            "IPLFormat": "ipl",             # IPL
            "JpegFormat": "jpg",            # JPEG
            "Jpeg2000Format": "jp2",        # JPEG2000
            "MXFFormat": "mxf",             # MXF - Material Exchange Format
            "OpenEXRFormat": "exr",         # OpenEXR
            "PandoraFormat": "piyuv10",     # Pandora YUV
            "PNGFormat": "png",             # PNG
            "VPBFormat": "vpb",             # Quantel VPB
            "QuickTimeMovies": "mov",       # QuickTime Movie
            "HDRFormat": "hdr",             # Radiance
            "SixRNFormat": "6RN",           # Rendition
            "SGIFormat": "sgi",             # SGI
            "PICFormat": "si",              # Softimage PIC
            "SUNFormat": "RAS",             # SUN Raster
            "TargaFormat": "tga",           # Targa
            "TiffFormat": "tiff",           # TIFF
            "rlaFormat": "rla",             # Wavefront RLA
            "BMPFormat": "bmp",             # Windows BMP
            "YUVFormat": "yuv",             # YUV
            }.get(FormatID, "exr")          # EXR fallback format

        #   Gets from tool
        location = node.GetInput("Location")
        useLastVersion = node.GetInput("RenderLastVersionControl")

        #   Get info from Core
        curfile = self.core.getCurrentFileName()
        filepath = curfile.replace("\\", "/")
        if not filepath:
            self.core.showFileNotInProjectWarning()
            return False

        entity = self.core.getScenefileData(curfile)
        basePath = self.core.paths.getRenderProductBasePaths()[location]

        #   Get current filepath from tool
        try:
            versionPath = os.path.dirname(node.GetAttrs()["TOOLST_Clip_Name"][1])
            if not os.path.exists(versionPath):
                versionPath = os.path.dirname(versionPath)
        except:
            versionPath = ""

        #   Modify data
        if "version" in entity:
            del entity["version"]
        entity.update({
                    "project_path": basePath,
                    "identifier": MediaID,
                    "mediaType": "2drenders",
                    })

        #   Get the highest existing media version
        highestVersion = self.core.mediaProducts.getHighestMediaVersion(entity,
                                                                        ignoreFolder=False,
                                                                        getExisting=True,
                                                                        ignoreEmpty=False)
        if highestVersion is None:
            self.core.popup("Unable to get current version info")
            return False

        #   If render as last version
        version = None
        if useLastVersion:
            self.core.popup("Render as previous version is enabled.\nThis may overwrite existing files.")
            version = highestVersion
            versionDisplay = f"Version:                  {version}\n"

        #   Makes format specific details for the popup msg
        codecDetails = ""

        if fileType == "exr":
            bitdepthCode = node.GetInput("OpenEXRFormat.Depth")
            bitDepth = {
                0.0: "Auto",
                1.0: "16 bit",
                2.0: "32 bit"
                }.get(bitdepthCode)

            exrCompressCode = node.GetInput("OpenEXRFormat.Compression")
            exrCompress = {
                0.0: "None",
                1.0: "RLE",
                2.0: "ZipS (1 line)",
                3.0: "Zip (16 line)",
                4.0: "PIZ",
                5.0: "Pxr24",
                6.0: "B44",
                7.0: "B44a",
                8.0: "DWAA (32 line)",
                9.0: "DWAB (256 line)"
                }.get(exrCompressCode)
            
            codecDetails = (f"Bitdepth:           {bitDepth}\n"
                            f"Compression:   {exrCompress}\n")

        elif fileType == "mov":
            movCodec = node.GetInput("QuickTimeMovies.Compression")
            codecDetails = f"Codec:               {movCodec}\n"

        #   Gets the new filepath from Core
        outputNameRaw = self.core.getCompositingOut(MediaID,
                                                 fileType,
                                                 version,
                                                 render,
                                                 location,
                                                 comment,
                                                 ignoreEmpty=True,
                                                 )

        #   Replaces Prism seq formatting for Fusion
        framePlaceholder = "#" * self.core.framePadding
        outputName = outputNameRaw.replace(framePlaceholder, "")
        #   Gets filename for popup
        fileName = os.path.basename(outputNameRaw)

        #   Sets the new filepath details to the WritePrism
        node.Clip[self.fusion.TIME_UNDEFINED] = outputName
        node.FilePathControl = outputName

        #   Deal with version display if not Last Version
        if not useLastVersion:
            #   This is required since getHighestMediaVersion() will return v1 even if there are no versions
            #   Get a version one that is padded per project setting
            verOnePadded = "v" + ("0" * (self.core.versionPadding - 1)) + "1"
            #   Check if the returned highest version is v1
            if highestVersion == verOnePadded:
                #   Make a dummy v1 dir name to see if it exists
                tempBaseDir = os.path.dirname(os.path.dirname(outputNameRaw))
                tempVerOneDir = os.path.join(tempBaseDir, verOnePadded)

                if not os.path.exists(tempVerOneDir):
                    nextVer = highestVersion
                else:
                    match = re.search(r'\d+', highestVersion)
                    if match:
                        highVerInt = int(match.group())
                        nextVer = f"v{str(highVerInt + 1).zfill(self.core.versionPadding)}"
            else:
                match = re.search(r'\d+', highestVersion)
                if match:
                    highVerInt = int(match.group())
                    nextVer = f"v{str(highVerInt + 1).zfill(self.core.versionPadding)}"

            versionDisplay = f"Version:                  {nextVer}\n"

        #   Displays popup with WritePrism details
        self.core.popup(f"Media Identifier:   {MediaID}\n"
                        f"{versionDisplay}"
                        f"Location:               {location}\n\n"
                        f"File name:         {fileName}\n"
                        f"File type:            {fileType}\n"
                        f"{codecDetails}"
                        "\n\n"
                        f"Full path: \n\n{outputNameRaw}",
                        title="Saver Details")

        return outputName


    @err_catcher(name=__name__)
    def startRender(self, node):
        fileName = self.getOutputPath(node, render=True)

        if fileName == "FileNotInPipeline":
            QMessageBox.warning(
                self.core.messageParent,
                "Prism Warning",
                "The current file is not inside the Pipeline.\nUse the Project Browser to create a file in the Pipeline.",
            )
            return

        self.core.saveScene(versionUp=False)
        

    #   Used in the Refresh button on the LoaderPrism custom tool
    @err_catcher(name=__name__)
    def updateNodeUI(self, nodeType, node):
        if nodeType == "writePrism":
            #   Gets render locs from project settings
            locations = self.core.paths.getRenderProductBasePaths()
            locNames = list(locations.keys())

            self.core.popup("Locations have been updated")

            # As copySettings and loadSettings doesn't work with python we'll have to execute them as Lua code
            luacode = ' \
            local tool = comp.ActiveTool  \
            local ctrls = tool.UserControls  \
            local settings = comp:CopySettings(tool)  \
  \
            comp:Lock()  \
  \
            ctrls.Location = {'

            for location in locNames:
                luacode = luacode + \
                    '{CCS_AddString = "' + str(location) + '"},\n \
                     {CCID_AddID = "' + str(location) + '"},\n'

            luacode = luacode + ' \
            ICD_Width = 0.7,  \
            INP_Integer = false,  \
            INP_External = false,  \
            LINKID_DataType = "FuID",  \
            ICS_ControlPage = "File",  \
            CC_LabelPosition = "Horizontal",  \
            INPID_InputControl = "ComboIDControl",  \
            LINKS_Name = "Location",  \
        }  \
 \
            tool.UserControls = ctrls \
            tool:LoadSettings(settings) \
            refresh = tool:Refresh() \
            comp:Unlock() \
            '

            comp = self.fusion.GetCurrentComp()
            comp.Execute(luacode)
