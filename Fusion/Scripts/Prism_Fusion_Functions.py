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
import re
import tempfile

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

        with (open(os.path.join(self.pluginDirectory,
                                "UserInterfaces",
                                "FusionStyleSheet",
                                "Fusion.qss"),
                                "r",)) as ssFile:
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
        




    # @err_catcher(name=__name__)
    # def captureViewportThumbnail(self):

    #     # path = tempfile.NamedTemporaryFile(suffix=".jpg").name

    #     path = r"C:\\Users\\Alta Arts\\Desktop\\THUMBS\\TESTTHUMB.png"

    #     self.core.popup(f"self.fusion from thumb:  {self.fusion}")                                      #    TESTING


    #     comp = self.fusion.GetCurrentComp()
    #     flow = comp.CurrentFrame.FlowView
    #     # viewer = self.fusion.CurrentViewer()
    #     # image = viewer.GetCurrentImage()

    #     # Get the right viewer
    #     right_viewer = fusion.GetViewers().get("RightView", None)
    #     if right_viewer is None:
    #         print("Right viewer not found.")
    #         return
        

    #     selectedTool = comp.GetToolList(False).get("Selected", None)
    #     self.core.popup(f"selectedTool:  {selectedTool}")                                      #    TESTING

    #     lastTool = self.getLastTool(comp)
    #     self.core.popup(f"lastTool: {lastTool}")                                      #    TESTING

    #     tempSaver = comp.AddTool("WritePrism")

    #     if lastTool:
    #         tempSaver.ConnectInput(1, lastTool)

    #     tempSaver.SetData("File", path)
    #     tempSaver.SetData("Format", "PNG")

    #     comp.QueueAction("Render")

        # # Wait for render completion
        # import time
        # time.sleep(5)  # Adjust time as needed for rendering

        # # Remove the temporary Saver tool
        # current_comp.DeleteTool(tempSaver)


        # if image:
        #     image.Save(path)

        # pm = self.core.media.getPixmapFromPath(path)

        # return pm

    @err_catcher(name=__name__)
    def getLastTool(self, comp):

        toolList = comp.GetToolList()
        lastTool = None
        for tool in toolList.values():
            if not tool.GetInputList():
                lastTool = tool

        return lastTool



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
        return self.fusion.GetCurrentComp().GetPrefs()["Comp"]["FrameFormat"]["Rate"]
    

    @err_catcher(name=__name__)
    def setFPS(self, origin, fps):
        return self.fusion.GetCurrentComp().SetPrefs({"Comp.FrameFormat.Rate": fps})
    

    @err_catcher(name=__name__)
    def getResolution(self):
        width = self.fusion.GetCurrentComp().GetPrefs()[
            "Comp"]["FrameFormat"]["Height"]
        height = self.fusion.GetCurrentComp().GetPrefs()[
            "Comp"]["FrameFormat"]["Width"]
        return [width, height]
    

    @err_catcher(name=__name__)
    def setResolution(self, width=None, height=None):
        self.fusion.GetCurrentComp().SetPrefs(
            {
                "Comp.FrameFormat.Width": width,
                "Comp.FrameFormat.Height": height,
            }
        )


    @err_catcher(name=__name__)
    def updateReadNodes(self):
        updatedNodes = []

        selNodes = self.fusion.GetCurrentComp().GetToolList(True, "Loader")
        if len(selNodes) == 0:
            selNodes = self.fusion.GetCurrentComp().GetToolList(False, "Loader")

        if len(selNodes):
            comp = self.fusion.GetCurrentComp()
            comp.StartUndo("Updating loaders")
            for k in selNodes:
                i = selNodes[k]
                curPath = comp.MapPath(i.GetAttrs()["TOOLST_Clip_Name"][1])

                self.core.popup(f"curPath:  {curPath}")                                      #    TESTING

                # newPath = self.core.getLatestCompositingVersion(curPath)
                newPath = self.core.getHighestVersion(curPath)

                self.core.popup(f"newPath: {newPath}")                                      #    TESTING

                if os.path.exists(os.path.dirname(newPath)) and not curPath.startswith(
                    os.path.dirname(newPath)
                ):
                    firstFrame = i.GetInput("GlobalIn")
                    lastFrame = i.GetInput("GlobalOut")

                    i.Clip = newPath

                    i.GlobalOut = lastFrame
                    i.GlobalIn = firstFrame
                    i.ClipTimeStart = 0
                    i.ClipTimeEnd = lastFrame - firstFrame
                    i.HoldLastFrame = 0

                    updatedNodes.append(i)
            comp.EndUndo(True)

        if len(updatedNodes) == 0:
            QMessageBox.information(
                self.core.messageParent, "Information", "No nodes were updated"
            )
        else:
            mStr = "%s nodes were updated:\n\n" % len(updatedNodes)
            for i in updatedNodes:
                mStr += i.GetAttrs()["TOOLS_Name"] + "\n"

            QMessageBox.information(
                self.core.messageParent, "Information", mStr)
            

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


    @err_catcher(name=__name__)
    def importImages(self, filepath=None, mediaBrowser=None, parent=None):
        if mediaBrowser:
            sourceData = mediaBrowser.compGetImportSource()
            if not sourceData:
                return


        fString = "Please select an import option:"
        buttons = ["Current pass", "All passes", "Cancel"]
        result = self.core.popupQuestion(fString, buttons=buttons, icon=QMessageBox.NoIcon, parent=parent)

        if result == "Current pass":
            self.fusionImportSource(filepath, sourceData)
        elif result == "All passes":
            self.fusionImportPasses(filepath, sourceData)
        else:
            return
        

    @err_catcher(name=__name__)
    def fusionImportSource(self, filePath, sourceData):

        comp = self.fusion.GetCurrentComp()
        comp.Lock()

        filePathTemplate = sourceData[0][0]
        firstFrame = sourceData[0][1]
        lastFrame = sourceData[0][2]

        framePadding = self.core.framePadding

        # Extract filename from the file path template
        fileNameWithPlaceholder = os.path.basename(filePathTemplate)
        fileName = fileNameWithPlaceholder.replace('#' * framePadding, '').replace('.', '')     #   TODO - to be used with rename if poss

        # Replace the placeholder '####' with the padded first frame number
        paddedFirstFrame = str(firstFrame).zfill(framePadding)
        filePath = filePathTemplate.replace('#' * framePadding, paddedFirstFrame)

        comp.CurrentFrame.FlowView.Select(None, False)

        try:
            loaderLoc = comp.MapPath('Macros:/LoaderPrism.setting')
            loaderText = self.bmd.readfile(loaderLoc)
            comp.Paste(loaderText)

            tool = comp.ActiveTool()

        except:
            print("LoaderPrism is not found.  Using normal Loader.")
            tool = comp.AddTool("Loader", -32768, -32768)

        tool.Clip[1] = filePath
        tool.GlobalIn[1] = firstFrame
        tool.GlobalOut[1] = lastFrame
        tool.ClipTimeStart[1] = firstFrame
        tool.ClipTimeEnd[1] = lastFrame
        tool.HoldFirstFrame[1] = 0
        tool.HoldLastFrame[1] = 0
        tool.SetAttrs({"TOOLS_Name": "LoaderPrism"})        #   TODO - look at F2 rename

        comp.Unlock()


    @err_catcher(name=__name__)
    def fusionImportPasses(self, filepath, sourceData):

        self.core.popup("Currently unused.  Please use 'Current Pass for now.")


        # self.fusion.GetCurrentComp().Lock()

        # sourceData = origin.compGetImportPasses()

        # for i in sourceData:
        #     filePath = i[0]
        #     firstFrame = i[1]
        #     lastFrame = i[2]

        #     filePath = filePath.replace(
        #         "#"*self.core.framePadding, "%04d".replace("4", str(self.core.framePadding)) % firstFrame)

        #     self.fusion.GetCurrentComp().CurrentFrame.FlowView.Select()
        #     tool = self.fusion.GetCurrentComp().AddTool("Loader", -32768, -32768)
        #     tool.Clip = filePath
        #     tool.GlobalOut = lastFrame
        #     tool.GlobalIn = firstFrame
        #     tool.ClipTimeStart = 0
        #     tool.ClipTimeEnd = lastFrame - firstFrame
        #     tool.HoldLastFrame = 0

        # self.fusion.GetCurrentComp().Unlock()


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
        

    @err_catcher(name=__name__)
    def updateNodeUI(self, nodeType, node):
        if nodeType == "writePrism":
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
