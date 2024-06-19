Set WshShell = WScript.CreateObject("WScript.Shell")
WScript.Sleep 5000
WshShell.AppActivate "File"
WshShell.SendKeys "{F11}"
