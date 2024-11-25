For windows, install the latest version of python from https://www.python.org/downloads/ 

This was originally written for 3.11, but should work with any python 3.x. After install, you will need a few utility libraries (mostly wxPython):

py.exe -m pip install --upgrade pip
py.exe -m pip install wxPython

In the future you'll also need these for excel and pdf output, but I haven't gotten around to implementing that yet. 
py.exe -m pip install xlsxwriter
py.exe -m pip install fpdf
