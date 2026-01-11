@echo off
echo Installing requirements if needed...
pip install pyinstaller

echo.
echo Building executable...
pyinstaller --noconsole --onefile --name "YunpanSearchTool" --add-data "tj_yunpan_tree.json;." gui_search.py

echo.
if exist "dist\YunpanSearchTool.exe" (
    echo Build successful! The executable is located in the 'dist' folder.
    explorer dist
) else (
    echo Build failed. Please check the output above.
)
pause
