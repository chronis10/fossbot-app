@echo off
set cur_path=%cd%
echo %cur_path%

start "" "C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\coppeliaSim.exe" -a "%cur_path%\coppelia\stream.lua" -h -f "%cur_path%\coppelia\default.ttt"

start "" fossbot-app.exe

exit