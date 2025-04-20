@echo off
REM Start the backend server
start cmd /k "cd ./backend && uvicorn main:app --port 8000 --reload"

REM Start the frontend server
start cmd /k "cd ./frontend && npm run dev"

REM Open the frontend in the default web browser
start chrome http://localhost:5173

REM Exit the script
exit