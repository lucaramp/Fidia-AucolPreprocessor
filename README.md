# Istruzioni per creare l'eseguibile: 

* Aprire una console di windows e posizionarsi nella cartella work dove si vuole scaricare il progetto.
(ES.: f:\Git )  

* Clonare il progetto:    
***git clone https://github.com/lucaramp/Fidia-AucolPreprocessor.git***  
verrà creata la cartella g:\Git\AucolPreprocessor che contiene i sorgenti ed il file dei requirements.txt

* Creazione del Virtuale Environment:  
***python -m venv venv***  
verrà creato un ambiente virtuale (bisogna avere installato Python 3.8.10) sotto la cartella "venv"  

* Attivazione dell'ambiente e installazione dei requirements:  
***.\venv\Scripts\activate***  
***python.exe -m pip install --upgrade pip***  
per aggiornare PIP  
***pip install -r .\requirements.txt***  
per installare i Requirements
* Test di esecuzione come script Python:  
***python main.py***  
L'applicazione parte in modalità script.
* Creazione eseguibile sotto .\dist  :  
***.\MakeExe.cmd***  
ora sotto .\dist\AucolPreprocessor ci dovrebbe essere AucolPreprocessor.exe
* Apertura e gestione progetto con PyCharm:  
File->Open  e selezionare la cartella AucolPreprocessor e dare OK  
Bisogna aggiungere una RunConfiguration che lancia main.py dalla cartella f:\git\AucolPreprocessor che utilizza un ambiente virtuale già creato e che sta sotto .\venv

