call %UserProfile%\Miniconda3\Scripts\activate.bat
call activate .\uv
python app.py rem if fail: reinstall
pause
