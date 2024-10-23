@echo off
echo Installing...

if exist "C:\Program Files\PasswordChanger\" (
  mkdir "C:\Program Files\PasswordChanger"
)

copy app.py "C:\Program Files\PasswordChanger"
