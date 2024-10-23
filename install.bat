@echo off
echo Installing...

if not exist "C:\Program Files\PasswordChanger\" (
  mkdir "C:\Program Files\PasswordChanger"
)

copy app.py "C:\Program Files\PasswordChanger"
xcopy /s /y templates "C:\Program Files\PasswordChanger"
