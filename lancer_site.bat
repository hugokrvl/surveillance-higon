@echo off
chcp 65001 >nul
echo ============================================================
echo   SITE LOCAL - Portefeuille Higon (simulation en points)
echo ============================================================
echo.
echo   Installation/maj des dependances...
python -m pip install -q -r requirements.txt
echo.
echo   Demarrage du site... ouvre ton navigateur sur :
echo.
echo       http://127.0.0.1:5000
echo.
echo   (Ferme cette fenetre ou Ctrl+C pour arreter)
echo ============================================================
python -X utf8 app.py
pause
