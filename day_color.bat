@echo off
:Begin
echo %time%
echo "start"
z:/Enviroments/dc/Scripts/python.exe z:/GG/Source/day_color/day_color.py
echo "done"
echo %time%
echo sleep 600 sec
timeout 600 > NUL
goto begin