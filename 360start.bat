@echo off

cd "C:\Users\Intel Nuc\Dropbox\360 dropbox"
:: Avvia il server PHP
start php -S localhost:8000

:: Attendi 5 secondi per assicurarti che il server PHP sia avviato
timeout /t 5 /nobreak

:: Esegui lo script Python
start python 360python.py

:: Attendi 10 secondi per assicurarti che lo script python sia avviato
timeout /t 10 /nobreak

:: Apri Microsoft Edge a schermo intero su localhost:8000
start msedge --start-fullscreen http://localhost:8000
wscript "fullscreen.vbs"

