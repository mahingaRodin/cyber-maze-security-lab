@echo off
echo Building Cyber Maze EXE...
echo.
echo Make sure you have updated the IP in client_agent.py!
echo Your current IP is:
ipconfig | findstr IPv4
echo.
pause

pyinstaller --onefile --windowed --name CyberMaze.exe --add-data "client_agent.py;." --add-data "config.json;." maze_game.py

echo.
echo Done! Check the dist folder
pause