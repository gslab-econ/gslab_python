REM ****************************************************
REM * make.bat: double-click to run all scripts
REM *
REM *
REM ****************************************************

cd ./test
SET LOG=make.log

REM LOG START
ECHO make.bat started	>%LOG%
ECHO %DATE%				>>%LOG%
ECHO %TIME%				>>%LOG%

REM RUN TEST SCRIPT
python test_extract_data.py 
COPY %LOG%+test_extract_data.log %LOG%
DEL test_extract_data.log
RMDIR /S /Q ..\external

REM LOG END
ECHO make.bat completed	>>%LOG%
ECHO %DATE%				>>%LOG%
ECHO %TIME%				>>%LOG%

MOVE make.log ../make.log

PAUSE