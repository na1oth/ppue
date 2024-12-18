For windows, install the latest version of python from https://www.python.org/downloads/ 

This was originally written for 3.11, but should work with any python 3.x. After install, you will need a few utility libraries (mostly wxPython).

The two neceesary utilities are the current version of pip and wxPython, but we'll also install support for later printing pdfs when that gets implemented.

To install start by opening a terminal window.  You can right click on the windows icon and select "Terminal" it does not need to be "Terminal (Admin)" but that works too.

In that terminal window after the > prompt, you will type each of the following lines, hitting enter after each line, and answering yes to any questions asked. 

py.exe -m pip install --upgrade pip
py.exe -m pip install wxPython
py.exe -m pip install fpdf

To install the PPUE program, click the green button labled "<> Code" then select "Download Zip".  You will save this to your Downloads directory.
Go to the downloads directory, right click on the ppue-main.zip and select "Extract All" from the menu.  
You can specify another path to extract to, but the default will put it in the Downloads folder with the name "ppue-main" 
Go into the ppue-main directory (and again since it tends to make a directory in a directory).  
Execute ppue by double clicking "mkchar" or "mkchar.py"  (depending if your file extensions are visible).
A debug window will pop up, but you can ignore/minimize that.  
The other window will be the utility.  Plz report back any issues or suggestions. 

Enjoy!
