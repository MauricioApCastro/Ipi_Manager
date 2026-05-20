@echo off
setlocal

set "DESTINO=C:\IPI_Manager"
set "ORIGEM=%~dp0"

echo Instalando IPI Manager em %DESTINO%...

if not exist "%DESTINO%" mkdir "%DESTINO%"
if not exist "%DESTINO%\data" mkdir "%DESTINO%\data"
if not exist "%DESTINO%\recibos" mkdir "%DESTINO%\recibos"
if not exist "%DESTINO%\backups" mkdir "%DESTINO%\backups"

copy /Y "%ORIGEM%IPI_Manager.exe" "%DESTINO%\IPI_Manager.exe" >nul
copy /Y "%ORIGEM%INSTALACAO_CLIENTE.md" "%DESTINO%\INSTALACAO_CLIENTE.md" >nul
copy /Y "%ORIGEM%MANUAL_PROFESSORA.md" "%DESTINO%\MANUAL_PROFESSORA.md" >nul

powershell -NoProfile -ExecutionPolicy Bypass -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop') + '\IPI Manager.lnk'); $s.TargetPath='%DESTINO%\IPI_Manager.exe'; $s.WorkingDirectory='%DESTINO%'; $s.Save()"

echo.
echo Instalacao concluida.
echo Atalho criado na Area de Trabalho: IPI Manager
echo.
pause
