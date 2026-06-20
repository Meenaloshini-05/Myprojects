@echo off
cd /d C:\expense_tracker

echo Starting Expense Tracker...
start "" http://127.0.0.1:5000

python app.py

pause
