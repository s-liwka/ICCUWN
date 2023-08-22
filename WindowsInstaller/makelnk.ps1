$source = "$env:LOCALAPPDATA\ICCUWN\run.bat"
$destination = "$env:USERPROFILE\Desktop\ICCUWN"
New-Item -ItemType SymbolicLink -Path $destination -Target $source