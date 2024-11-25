import wx
#import wx.lib.inspection
from lib.cframe import CharFrame
#import sel_diag
#from unit_tab import UnitTab

if __name__ == '__main__':
    app = wx.App()
    frame = CharFrame(None, "Prowlers and Paragons Character Builder")
    frame.Centre()
    frame.Show()
    #wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()


'''
Enhancements

Bugs

Quirks

Todo
'''

