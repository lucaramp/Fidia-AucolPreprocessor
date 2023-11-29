set ExeName=AucolPreprocessor
rmdir /s /q .\dist\%ExeName%
pyinstaller  -w --icon=.\IMG\Fidialogo.ico --name %ExeName% main.py
xcopy /Y /S .\IMG\*.* .\dist\%ExeName%\IMG\
xcopy /Y /S .\QSS\*.* .\dist\%ExeName%\QSS\
xcopy /Y /S .\PLC\*.* .\dist\%ExeName%\PLC\
