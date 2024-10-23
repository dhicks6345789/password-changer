@echo off
echo Installing...

rem Make sure the application folder exists, copy the code over to it.
if not exist "C:\Program Files\PasswordChanger\" (
  mkdir "C:\Program Files\PasswordChanger"
  mkdir "C:\Program Files\PasswordChanger\templates"
)
copy app.py "C:\Program Files\PasswordChanger"
xcopy /s /y templates "C:\Program Files\PasswordChanger\templates"

rem Change to the application folder.
cd "C:\Program Files\PasswordChanger"

rem Make sure the Python Virtual Environment (venv) exists.
if not exist "venv\" (
  pip install virtualenv
  virtualenv venv
)

rem Make sure the Python module requirements are installed in the venv.
venv\Scripts\pip.exe install flask
venv\Scripts\pip.exe install waitress

rem venv\Scripts\python.exe app.py
