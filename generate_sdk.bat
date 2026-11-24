@echo off
REM Regenerates the Python SDK (deepwork_sdk) from the API's OpenAPI spec and installs it.
REM Requires: Node.js (npm) and Java 11+.
REM
REM Equivalent to the challenge's command, against a running backend:
REM   openapi-generator-cli generate -i http://localhost:8000/openapi.json -g python -o deepwork_sdk --package-name deepwork_sdk
REM This script exports the spec straight from the code instead, so the backend need not be running.
cd /d "%~dp0"

where openapi-generator-cli >nul 2>nul || (
    echo Installing OpenAPI Generator CLI...
    call npm install -g @openapitools/openapi-generator-cli || goto :error
)
where java >nul 2>nul || (echo [ERROR] Java 11+ is required by OpenAPI Generator. & goto :error)

call env\Scripts\activate || (echo [ERROR] Run setupdev.bat first. & goto :error)

echo Exporting OpenAPI spec...
python export_openapi.py openapi.json || goto :error

echo Generating SDK...
call openapi-generator-cli generate -i openapi.json -g python -o deepwork_sdk --package-name deepwork_sdk || goto :error

echo Installing SDK into the virtual environment...
pip install ./deepwork_sdk || goto :error

echo.
echo SDK ready. Try it:  python sdk_example.py   (with the backend running)
exit /b 0

:error
echo.
echo [ERROR] SDK generation failed. See the messages above.
exit /b 1
