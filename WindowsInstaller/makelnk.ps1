$source = "$env:LOCALAPPDATA\ICCUWN\run.bat"
$destination = "$env:USERPROFILE\Desktop\ICCUWN.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($destination)
$shortcut.TargetPath = $source
$shortcut.Save()