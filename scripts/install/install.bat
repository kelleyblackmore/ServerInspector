@echo off
:: serverinspector Windows Installer
:: This script detects your environment and installs serverinspector

echo serverinspector Windows Installer
echo ===============================
echo.

:: Check for admin privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges: Yes
) else (
    echo Running with administrator privileges: No
    echo Note: Some installation methods may require admin rights
)

echo.
echo Detecting system configuration...

:: Check for Docker
where docker >nul 2>&1
if %errorLevel% == 0 (
    echo * Docker detected: Yes
    set HAS_DOCKER=1
) else (
    echo * Docker detected: No
    set HAS_DOCKER=0
)

:: Check for Python
where python >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo * %PYTHON_VERSION% detected
    set HAS_PYTHON=1
) else (
    echo * Python not detected
    set HAS_PYTHON=0
)

:: Check for pipx
where pipx >nul 2>&1
if %errorLevel% == 0 (
    echo * pipx detected: Yes
    set HAS_PIPX=1
) else (
    echo * pipx detected: No
    set HAS_PIPX=0
)

:: Check for Git
where git >nul 2>&1
if %errorLevel% == 0 (
    echo * Git detected: Yes
    set HAS_GIT=1
) else (
    echo * Git detected: No
    set HAS_GIT=0
)

echo.
echo Installation Options:

:: Set default installation method
if %HAS_DOCKER% == 1 (
    echo 1. Docker [Recommended]
    echo    - Runs in an isolated container
    echo    - Includes all dependencies
    set DEFAULT_METHOD=docker
) else if %HAS_PIPX% == 1 (
    echo 1. pipx [Recommended]
    echo    - Installs in an isolated environment
    echo    - No dependency conflicts
    echo    - Requires Python %PYTHON_VERSION%
    set DEFAULT_METHOD=pipx
) else if %HAS_PYTHON% == 1 (
    echo 1. Python pip [Recommended]
    echo    - Installs as a Python package
    echo    - Requires Python %PYTHON_VERSION%
    set DEFAULT_METHOD=pip
) else (
    echo 1. Download executable [Recommended]
    echo    - Standalone executable
    echo    - No dependencies required
    set DEFAULT_METHOD=exe
)

:: Show alternative options
if not "%DEFAULT_METHOD%"=="docker" if %HAS_DOCKER% == 1 (
    echo 2. Docker
    echo    - Runs in an isolated container
    echo    - Includes all dependencies
)

if not "%DEFAULT_METHOD%"=="pipx" if %HAS_PIPX% == 1 (
    echo 2. pipx
    echo    - Installs in an isolated environment
    echo    - No dependency conflicts
    echo    - Requires Python %PYTHON_VERSION%
)

if not "%DEFAULT_METHOD%"=="pip" if %HAS_PYTHON% == 1 (
    echo 3. Python pip
    echo    - Installs as a Python package
    echo    - Requires Python %PYTHON_VERSION%
)

if not "%DEFAULT_METHOD%"=="exe" (
    echo 4. Download executable
    echo    - Standalone executable
    echo    - No dependencies required
)

echo.
set /p CHOICE="Select installation method [1]: "

if "%CHOICE%"=="" set CHOICE=1

if "%CHOICE%"=="1" (
    set METHOD=%DEFAULT_METHOD%
) else if "%CHOICE%"=="2" (
    if "%DEFAULT_METHOD%"=="docker" (
        if %HAS_PIPX% == 1 (
            set METHOD=pipx
        ) else if %HAS_PYTHON% == 1 (
            set METHOD=pip
        ) else (
            set METHOD=exe
        )
    ) else if "%DEFAULT_METHOD%"=="pipx" (
        if %HAS_DOCKER% == 1 (
            set METHOD=docker
        ) else (
            set METHOD=exe
        )
    ) else if "%DEFAULT_METHOD%"=="pip" (
        if %HAS_DOCKER% == 1 (
            set METHOD=docker
        ) else if %HAS_PIPX% == 1 (
            set METHOD=pipx
        ) else (
            set METHOD=exe
        )
    ) else (
        if %HAS_DOCKER% == 1 (
            set METHOD=docker
        ) else if %HAS_PIPX% == 1 (
            set METHOD=pipx
        ) else if %HAS_PYTHON% == 1 (
            set METHOD=pip
        ) else (
            echo Invalid selection.
            exit /b 1
        )
    )
) else if "%CHOICE%"=="3" (
    if %HAS_PIPX% == 1 (
        set METHOD=pipx
    ) else (
        set METHOD=pip
    )
) else if "%CHOICE%"=="4" (
    set METHOD=exe
) else (
    echo Invalid selection.
    exit /b 1
)

echo.
echo Installing via %METHOD%...
echo.

if "%METHOD%"=="docker" (
    call :install_docker
) else if "%METHOD%"=="pipx" (
    call :install_pipx
) else if "%METHOD%"=="pip" (
    call :install_pip
) else if "%METHOD%"=="exe" (
    call :install_exe
)

echo.
echo Installation completed!
echo.
exit /b 0

:install_docker
    echo Creating installation directory...
    if not exist "%USERPROFILE%\serverinspector" mkdir "%USERPROFILE%\serverinspector"
    cd /d "%USERPROFILE%\serverinspector"

    echo Downloading Docker configuration...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/kelleyblackmore/serverinspector/main/Dockerfile' -OutFile 'Dockerfile'}"
    if %errorLevel% neq 0 (
        echo Error downloading Dockerfile.
        exit /b 1
    )

    echo Building Docker image...
    docker build -t serverinspector .

    echo Creating wrapper batch file...
    (
        echo @echo off
        echo docker run -v "%%USERPROFILE%%\serverinspector\config:/config" ^
        echo            -v /etc:/host/etc:ro ^
        echo            -v /var/log:/host/var/log:ro ^
        echo            -v /proc:/host/proc:ro ^
        echo            serverinspector %%*
    ) > serverinspector.bat

    if not exist config mkdir config

    echo.
    echo Docker installation successful!
    echo.
    echo You can now use serverinspector with:
    echo   %USERPROFILE%\serverinspector\serverinspector.bat run /config/simple-test.yaml
    echo.
    echo To add it to your PATH, run the following in an administrator command prompt:
    echo   setx PATH "%%PATH%%;%USERPROFILE%\serverinspector"
    exit /b 0

:install_pipx
    echo Installing via pipx...

    if %HAS_PYTHON% == 0 (
        echo Error: Python not found.
        exit /b 1
    )

    if %HAS_PIPX% == 0 (
        echo pipx not found. Installing pipx first...
        pip install --user pipx
        echo Adding pipx to PATH...
        python -m pipx ensurepath
        echo Please restart your command prompt and run this installer again.
        exit /b 1
    )

    :: Check if we're already in the repository
    if exist "pyproject.toml" if exist "src\serverinspector" (
        echo Detected existing repository.

        echo Fixing package configuration...
        powershell -Command "& {(Get-Content pyproject.toml) -replace 'serverinspector.test_types', '' | Set-Content pyproject.toml}"

        echo Creating missing directory...
        if not exist "src\serverinspector\test_types" mkdir "src\serverinspector\test_types"

        echo Installing with pipx...
        pipx install .
    ) else (
        echo Creating temporary directory...
        set TEMP_DIR=%TEMP%\serverinspector_install_%RANDOM%
        mkdir "%TEMP_DIR%"
        cd /d "%TEMP_DIR%"

        echo Cloning repository...
        if %HAS_GIT% == 1 (
            git clone https://github.com/kelleyblackmore/serverinspector.git .
        ) else (
            echo Downloading source archive...
            powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/kelleyblackmore/serverinspector/archive/main.zip' -OutFile 'serverinspector.zip'}"
            echo Extracting archive...
            powershell -Command "& {Expand-Archive -Path 'serverinspector.zip' -DestinationPath .}"
            cd serverinspector-main
        )

        echo Fixing package configuration...
        powershell -Command "& {(Get-Content pyproject.toml) -replace 'serverinspector.test_types', '' | Set-Content pyproject.toml}"

        echo Creating missing directory...
        mkdir src\serverinspector\test_types

        echo Installing with pipx...
        pipx install .

        echo Cleaning up...
        cd /d "%USERPROFILE%"
        rd /s /q "%TEMP_DIR%"
    )

    echo.
    echo pipx installation successful!
    echo.
    echo You can now use serverinspector with:
    echo   serverinspector --help
    exit /b 0

:install_pip
    echo Installing via pip...

    if %HAS_PYTHON% == 0 (
        echo Error: Python not found.
        exit /b 1
    )

    :: Check if we're already in the repository
    if exist "pyproject.toml" if exist "src\serverinspector" (
        echo Detected existing repository.

        echo Fixing package configuration...
        powershell -Command "& {(Get-Content pyproject.toml) -replace 'serverinspector.test_types', '' | Set-Content pyproject.toml}"

        echo Creating missing directory...
        if not exist "src\serverinspector\test_types" mkdir "src\serverinspector\test_types"

        echo Installing with pip...
        pip install .
    ) else (
        echo Creating temporary directory...
        set TEMP_DIR=%TEMP%\serverinspector_install_%RANDOM%
        mkdir "%TEMP_DIR%"
        cd /d "%TEMP_DIR%"

        echo Cloning repository...
        if %HAS_GIT% == 1 (
            git clone https://github.com/kelleyblackmore/serverinspector.git .
        ) else (
            echo Downloading source archive...
            powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/kelleyblackmore/serverinspector/archive/main.zip' -OutFile 'serverinspector.zip'}"
            echo Extracting archive...
            powershell -Command "& {Expand-Archive -Path 'serverinspector.zip' -DestinationPath .}"
            cd serverinspector-main
        )

        echo Fixing package configuration...
        powershell -Command "& {(Get-Content pyproject.toml) -replace 'serverinspector.test_types', '' | Set-Content pyproject.toml}"

        echo Creating missing directory...
        mkdir src\serverinspector\test_types

        echo Installing with pip...
        pip install .

        echo Cleaning up...
        cd /d "%USERPROFILE%"
        rd /s /q "%TEMP_DIR%"
    )

    echo.
    echo Python installation successful!
    echo.
    echo You can now use serverinspector with:
    echo   serverinspector --help
    exit /b 0

:install_exe
    echo Downloading executable...
    if not exist "%USERPROFILE%\serverinspector" mkdir "%USERPROFILE%\serverinspector"
    cd /d "%USERPROFILE%\serverinspector"

    powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/kelleyblackmore/serverinspector/releases/latest/download/serverinspector-windows.exe' -OutFile 'serverinspector.exe'}"
    if %errorLevel% neq 0 (
        echo Error downloading executable.
        exit /b 1
    )

    echo.
    echo Downloaded executable to %USERPROFILE%\serverinspector\serverinspector.exe
    echo.
    echo You can now use serverinspector with:
    echo   %USERPROFILE%\serverinspector\serverinspector.exe --help
    echo.
    echo To add it to your PATH, run the following in an administrator command prompt:
    echo   setx PATH "%%PATH%%;%USERPROFILE%\serverinspector"
    exit /b 0
