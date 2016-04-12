WScript.Sleep(1500)
On Error Resume Next
KODIPath="""" & wscript.arguments(0) & """"
KODIParams=wscript.arguments(1)

Dim objShell
Set objShell = WScript.CreateObject ("WScript.shell")
objShell.run KODIPath & " " & KODIParams