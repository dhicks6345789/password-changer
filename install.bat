@echo off
echo Installing...

set srcPath=%cd%

rem Make sure the application folder exists, copy the code over to it.
if not exist "C:\Program Files\PasswordChanger\" (
  mkdir "C:\Program Files\PasswordChanger"
  mkdir "C:\Program Files\PasswordChanger\templates"
)
copy app.py "C:\Program Files\PasswordChanger"
copy runWaitress.bat "C:\Program Files\PasswordChanger"
xcopy /s /y templates "C:\Program Files\PasswordChanger\templates"

rem Change to the application folder.
cd "C:\Program Files\PasswordChanger"

rem Make sure the Python Virtual Environment (venv) exists.
if not exist "venv\" (
  pip install virtualenv
  virtualenv venv
)

rem Make sure the Python module requirements are installed in the venv.
if not exist "C:\Program Files\PasswordChanger\venv\Lib\site-packages\flask" (
  venv\Scripts\pip.exe install flask
)
if not exist "C:\Program Files\PasswordChanger\venv\Lib\site-packages\waitress" (
  venv\Scripts\pip.exe install waitress
)

echo Setting up PasswordChanger (running via the Waitress WSGI server) as a Windows service...
net stop PasswordChanger > nul 2>&1
"%srcPath%\nssm\2.24\win64\nssm.exe" install PasswordChanger "C:\Program Files\PasswordChanger\runWaitress.bat" > nul 2>&1
"%srcPath%\nssm\2.24\win64\nssm.exe" set PasswordChanger DisplayName "Password Changer" > nul 2>&1
"%srcPath%\nssm\2.24\win64\nssm.exe" set PasswordChanger AppNoConsole 1 > nul 2>&1
"%srcPath%\nssm\2.24\win64\nssm.exe" set PasswordChanger Start SERVICE_AUTO_START > nul 2>&1
net start PasswordChanger

rem Note: to test locally, go to a command line and do:
rem net stop PasswordChanger
rem cd "C:\Program Files\Password Changer"
rem cls & venv\Scripts\flask.exe --app app run
