@ECHO OFF

rem ***************** Edit these default parameters ********************
rem one week is 168 hours, month is 720 hours, cannot sample beyond 6 weeks (1008 hours)
set HOURS=1000 

rem are there any duplicate instance names across any of the projects? (Y/N)
set APPEND=N
rem **************** edit nothing beyond this point *********************

echo Copyright (c) 2017 Cirba Inc. D/B/A Densify. All Rights Reserved.

set AUTO="f"
set FILE="f"
set HELP="f"
set MANUAL="f"
set fpath=%~sdp0

IF "%1"=="--auto" set AUTO="t"
IF "%1"=="-a" set AUTO="t"
IF "%1"=="--file" set FILE="t"
IF "%1"=="-f" set FILE="t"
IF "%1"=="--help" set HELP="t"
IF "%1"=="-h" set HELP="t"
IF %FILE%=="t" (
	set PROJECT_ID=%2
	set MANUAL="t"
)

IF "%1"=="" (
	set MANUAL="t"
	set /p PROJECT_ID=Please enter full credential file name: [ex. my-project-123.json] 
	echo one week is 168 hours, month is 720 hours, cannot sample beyond 6 weeks [1008 hours]
	set /p HOURS=Please enter your desired sample size in hours: 
	echo Are there any duplicate instance names across any of the projects?
	set /p APPEND=Please enter [Y/N] : 
)

IF %MANUAL%=="t" (
	echo __________________ Manually Loading %PROJECT_ID% _____________________________
	call:discoveryFunc %PROJECT_ID% %HOURS% %APPEND%
)


IF %AUTO%=="t" (
	for /f %%i in ('dir /b "%fpath%credentials\*.json"') do (
		echo __________________ Automatically Loading %%i _____________________________
		call:discoveryFunc %%i %HOURS% %APPEND% 
	)
)

if %HELP%=="t" (
	echo -a / --auto  : load all projects in the credentials folder using the default parameters
	echo -f / --file  : pass in credential file [my-project.json] load specified project using the default parameters.
	echo no arguments : specifiy all of the parameters manually 
)

GOTO:EOF

:discoveryFunc

echo Clearing previous config...
for /f %%i in ('dir /b %fpath%conf') do if not %%i == .gitignore 2>NUL del /q %fpath%conf\%%i
2>NUL del /q %fpath%workload.csv
2>NUL del /q %fpath%attributes.csv
2>NUL del /q %fpath%gcp_config.csv

ECHO  - Step 1 - GCP Discovery
py -2 %fpath%src\main.py -i %~1 -t %~2 -a %~3 

if errorlevel 1 GOTO:EOF

ECHO  - Step 2 - GCP Config
move %fpath%gcp_config.csv %fpath%conf\gcp_config.csv
move %fpath%attributes.csv %fpath%conf\attributes.csv
move %fpath%workload.csv %fpath%conf\workload.csv
if errorlevel 1 GOTO:EOF

ECHO  - Step 3 - Creating Manifest
call "%CIRBA_HOME%\bin\audit-converter.bat" -m %fpath%conf\ "GCP"
if errorlevel 1 GOTO:EOF

ECHO  - Step 4 - Creating Repository
call "%CIRBA_HOME%\bin\audit-converter.bat" %fpath%conf\ %fpath%repo\
if errorlevel 1 GOTO:EOF

ECHO  - Step 5 - Loading Repository
call "%CIRBA_HOME%\bin\load-repository.bat" %fpath%repo\ -o
if errorlevel 1 GOTO:EOF

ECHO  - Step 6 - Import Attributes
call "%CIRBA_HOME%\bin\data-tools.bat" ImportAttributes -f %fpath%conf\
if errorlevel 1 GOTO:EOF
GOTO:EOF

:EOF
if errorlevel 1 echo Exiting program...
pause
