Set WshShell = CreateObject("WScript.Shell")
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(Wscript.ScriptFullName)
WshShell.CurrentDirectory = strPath
WshShell.Run "cmd /c run_backend.bat", 0, false
