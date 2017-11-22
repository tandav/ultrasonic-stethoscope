call D:\Anaconda3\Scripts\activate.bat
call activate .\uv
python app.py rem if fail: reinstall
pause


call D:\Anaconda3\Scripts\activate.bat
echo "wait for a while. You can check progress by look at uv folder size, it should be about 1.01GB in the end"
conda create --prefix .\uv --file uv.txt
rem conda env create --prefix .\testenv --file testenv.txt 
rem call activate .\uv 
rem conda list > abc.txt
rem pause

rem @echo off
rem conda create --yes --prefix .\testenv
rem call activate .\testenv
rem call .\testenv\Scripts\activate.bat
rem conda install --yes zlib
rem conda list --explicit > testenv.txt
rem python app.py > fail.txt
pause


