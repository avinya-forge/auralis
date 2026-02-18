"""
Custom Events for wxPython GUI
"""

import wx.lib.newevent # type: ignore

# Progress event: carries stage (str), current (int), total (int)
ProgressEvent, EVT_PROGRESS = wx.lib.newevent.NewEvent()

# Status event: carries message (str)
StatusEvent, EVT_STATUS = wx.lib.newevent.NewEvent()

# File event: carries file_path (str)
FileEvent, EVT_FILE = wx.lib.newevent.NewEvent()

# Completion event: carries results (dict)
CompletionEvent, EVT_COMPLETED = wx.lib.newevent.NewEvent()
