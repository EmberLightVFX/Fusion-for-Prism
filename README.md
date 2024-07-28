# BMD Fusion for Prism-Pipeline

This is an update of EmberLightVFX's work for version 2 of Prism Pipeline.

https://github.com/EmberLightVFX/Fusion-for-Prism

***********************************************
Prism automates and simplifies the workflow of animation and VFX projects.

You can find more information on the website:

https://prism-pipeline.com/

*********************************************
## **Notes**

- Fusion versions 18+ have been tested.  It should work with version 17 as well.
- It is recommended to use the WritePrism tool to render into Prism.
- Hint: when it doubt, hit the Refresh button in WritePrism.
- Hint: clicking some Prism actions will load an instance of Prism, and thus there is a slight delay for the actions such as opening the Project Browser or clicking the Refresh button.
- Several scripts from other developers are used in the integration.  Many thanks to them!
<br/><br/>

## **Installation**

This plugin is for Windows only, as Prism2 only supports Windows at this time.

You can either download the latest stable release version from: [Latest Release](https://github.com/AltaArts/FusionStudio--Prism2/releases/latest)

or download the current code zipfile from the green "Code" button above or on [Github](https://github.com/AltaArts/FusionStudio--Prism2)

Copy the directory named "Fusion" to a directory of your choice, or a Prism2 plugin directory.

It is suggested to have the Fusion plugin with the other DCC plugins in: *{drive}\ProgramData\Prism2\plugins*

Prism's default plugin directories are: *{installation path}\Plugins\Apps* and *{installation Path}\Plugins\Custom*.

You can add the additional plugin search paths in Prism2 settings.  Go to Settings->Plugins and click the gear icon.  This opens a dialogue and you may add additional search paths at the bottom.

Once added, select the "Add existing plugin" (plus icon) and navigate to where you saved the Fusion folder.

![Plugin Refresh](https://github.com/user-attachments/assets/334d3134-cc34-4059-8d4e-bcde4e1b4648)


Afterwards, you can select the Plugin autoload as desired:

![Plugin Refresh](https://github.com/user-attachments/assets/aa7ad6ef-84e5-4ef9-bdc6-73423f13b156)


To add the integration, go to the "DCC Apps" -> "Fusion" tab.  Then click the "add" button and navigate to the folder containing Fusion's scripts - normally "[USER]\AppData\Roaming\Blackmagic Design\Fusion".  If there is more than one version of Fusion installed, it is advisable to set the executable in the "Override" box in the DCC settings.

![FusionSettings](https://github.com/user-attachments/assets/6d76eaac-90c6-4680-8e42-86501973b6c4)


### **Fusion Paths**

This Prism integration install assumes that Fusion's Path Maps includes the default locations.  The required scripts are written to the default basepath "[USER]\AppData\Roaming\Blackmagic Design\Fusion" and subdirectories such as "\Scripts", and "\Macros\".  If Fusion path maps have not been edited, the plugin should work correctly.  But if the path mapping does not contain these locations, they will need to be added.

![PathMaps](https://github.com/user-attachments/assets/c2fa3b17-a5ba-4b46-a2fe-b62d19abd4be)

<br/>

## **Usage**

### **Menu**
Prism functions are accessed through the Prism menu in the top bar of Fusion's UI, and are the same as other Prism DCC integrations.

![Menu](https://github.com/user-attachments/assets/9beefc53-2a91-4d69-ab21-dc41d64ff499)


<br/>

### **Saving**

Fusion Comps are saved into Prism the same way as other DCC's.  A user can right-click in the Prism Project Browser to "Create new version from preset", or "Create new version from Current".

Using the Save Version button in the Prism menu will save the Comp into the new version, and attempt to save a thumbnail.  The thumbnail will be saved using a hierarchy of available nodes:  currently selected node, then un-muted Saver, then muted Saver, then last tool in flow, or none.

If Fusion has autosave enabled, by default Fusion places the ".autocomp" file next to scenefile.  A custom icon will be displayed for the autosave file:


![Autosave](https://github.com/user-attachments/assets/aecce157-4670-4ff6-860d-81a730e0d890)


### **Importing Images**

The Fusion integration adds a custom Loader tool called "LoaderPrism" that is located in the Fusion Macros directory.  This tool is a standard Fusion Loader tool, with an added button that will refresh the image(s) in the Loader using AlbertoGZ's "ReloadLoaders" script.  The reload will refresh the image cache and adjust the clip in/out to the full duration of the file sequence.  This tool can be accessed from the Prism menu, and from the normal Fusion tools menus.  

![LoaderPrism](https://github.com/user-attachments/assets/eb9aaf4c-80d1-441c-a4ee-986e2313459f)

To import images from the Prism project, open the Prism Project Browser from inside Fusion and change to the Media tab.  In the Media Browser there is an "Import Images" option in the right-click menu that will open a dialogue.  

![RCL](https://github.com/user-attachments/assets/44438228-63e4-4d45-aaed-cc390c7b9453)  ![ImportDialogue](https://github.com/user-attachments/assets/c796e7b9-f357-490a-8b01-788466dd565f)


This dialogue has options to import the image(s) as normal, or choose to import the image(s) and then launch a tool to separate the EXR layers/channels/passes into separate Loader nodes if the splitter script is installed.

![EXR_Split](https://github.com/user-attachments/assets/104160de-32e4-47d0-870e-5b890664f422)

** Note:  The 'hos_SplitEXR_Ultra" script is not included in this repo, but will need to be added manually by the user.  The script is a fantastic tool, and works with most all .exr formatting, and it is constantly developed.  It is usually installed using the Reactor plugin that works for both Fusion Studio and Resolve Fusion.

https://gitlab.com/WeSuckLess/Reactor

![Reactor](https://github.com/user-attachments/assets/ce0c8f7b-c66e-499b-b545-c7414bf4e49f)



<br/><br/>

### **Rendering**

A custom Saver tool called "WritePrism" is used to render images into the Prism Project and is added to the comp just like a normal Saver.  The tool adds integration with Prism's file-naming and replaces the need to use the Browse button.  The workflow is:
- Add a WritePrism to the flow
- Select Output Format as desired
- Enter MediaID to be used in Prism
- Add comment if desired
 - Select Location if needed
- Click the Refresh button
- Click Render this Node Now Button.
- Click Update Master button
- Add Loader if needed




![WritePrism-Empty](https://github.com/user-attachments/assets/3834cfbc-0505-4e56-83f9-bfebc385ea5e)

Most of the options of the WritePrism are the same as a Saver tool, with the added functions:
 - "Filename": will have a placeholder "< Please press the refresh button >" until a valid Prism Media Identifier is entered and the "Refresh" button has been pressed.
 - "MediaID": Required.  The name to be used for the Prism Media Identifier to be rendered into.
 - "Comment":  comment passed to the Prism media version.
 - "Location": additional render locations from the project settings.  Defaults to Global, and the "Update" button must be pressed to populate the list.
 - "Render as Previous Version":  will render to the previous version of the MediaID.  If there is no version present, it will render to v001.  This is useful if a user has pressed refresh and a new version has been created but still wants to render to previous. 
 - "Refresh": this will use the name in the "MediaID" text box, see if a media version already exists, and create the next version if one exists.  It will only create a new version of one already exists, so pressing the refresh again will not have any adverse effects.
 - "Solo":  will mute (pass-through) all other Savers to allow for rendering this WritePrism only.
 - "Open in Explorer": will open the clips directory if it exists.
 - "Render this Node Now!":  this is the best way to render into the Prism project.  This will mute all other Savers, render this Saver into the MediaID location, trigger Prism to create a versionInfo file with the scenefile details, and finally un-mute the other Savers.
 - "Make Loader":  this will make a LoaderPrism node using the newly rendered media version.  This uses Alex Bogomolov's "LoaderFromSaver" script.
 - "Update Master":  this will trigger Prism to update the Master media version to the new rendered version.
 - "Make Loader from Master":  the same as above, but using the Master media version.

<br/>

Clicking the Refresh button will create a new media version for the Media Indentifier, and display a popup detailing the WritePrism settings.

![SaverDetails](https://github.com/user-attachments/assets/68ea02fe-e9cd-4cf5-8a69-33b86c9064b3)



<br/><br/>


## **Issues / Suggestions**

For any bug reports or suggestions, please add an issue to the Projects or Issues tab above.
