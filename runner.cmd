@rem -*- mode: bat; coding: utf-8 -*-
@REM ~ (c) Valik mailto:vasnake@gmail.com
@REM ~ Python tools executor

REM ~ 1. Install Python 2.7.
REM ~ 2. set envvars PROJECT_DIR, path and others
REM ~ 3. Execute once each step in turn: installVirtualenvLib, createVirtualenv, installDevelop.
REM ~ 4. Now you can run step fb2toolsProcedures as many times as you wish.

@echo on
chcp 1251 > nul
set wd=%~dp0
pushd "%wd%"

set PROJECT_DIR=%wd%
set PATH=%PATH%;C:\Python27;C:\Python27\Scripts
@REM SET http_proxy=http://user:password@someproxy.com:3128

@REM ~ GOTO installVirtualenvLib
@REM ~ GOTO createVirtualenv
@REM ~ GOTO installDevelop

@REM ~ GOTO fb2toolsProcedures

GOTO endOfScript

@REM ~ ################################################################################

:fb2toolsProcedures
pushd %PROJECT_DIR%
call env\scripts\activate.bat
@REM https://docs.python.org/2/using/cmdline.html#envvar-PYTHONIOENCODING
set PYTHONIOENCODING=cp1251:backslashreplace
python -u -m fb2tools namezip --workdir %wd%zip --scandir %wd%fb2
python -u -m fb2tools stripauthor --workdir %wd%zip
pause
exit

:installVirtualenvLib
pushd %PROJECT_DIR%
python -c "from urllib import urlretrieve; urlretrieve('https://bootstrap.pypa.io/get-pip.py', 'get-pip.py')"
python -u get-pip.py
pip install virtualenv
pause
exit

:createVirtualenv
pushd %PROJECT_DIR%
virtualenv  --no-site-packages env
pause
exit

:installDevelop
pushd %PROJECT_DIR%
call env\scripts\activate.bat
python setup.py develop
pause
exit

:endOfScript
popd
pause
exit
