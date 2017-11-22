start /wait "" .\Miniconda3-latest-Windows-x86_64.exe /InstallationType=JustMe /RegisterPython=1 /AddToPath=0 /S /D=%UserProfile%\Miniconda3
call %UserProfile%\Miniconda3\Scripts\activate.bat
echo "wait for a while. You can check progress by look at uv folder size, it should be about 1.01GB in the end"
conda create --prefix .\uv --file uv.txt
pause
