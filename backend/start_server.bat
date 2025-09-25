@echo off
echo Starting FlashThreat Backend Server...
echo.
echo Make sure you have:
echo 1. PostgreSQL running
echo 2. Redis running  
echo 3. .env file configured with API keys
echo.
echo Server will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python run_server.py

pause
