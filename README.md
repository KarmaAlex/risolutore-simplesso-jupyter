# risolutore-simplesso-jupyter
Un risolutore per problemi di programmazione lineare in forma standard che usa il metodo del simplesso in forma di tableau
## Istruzioni per l'uso
La maggior parte delle informazioni è inclusa nel notebook stesso. Accetta solo problemi in forma standard in cui tutte le variabili hanno un nome del tipo x_n con n numero intero. Basta immettere la funzione obiettivo ed i vincoli (omessi quelli di non negatività che sono sottointesi), e poi eseguire tutti i blocchi di codice seguenti.
## Installazione
Testato solo con python 3.11+, si consideri un requisito per il funzionamento.

Si può avviare come qualsiasi altro notebook jupyter, basta assicurarsi di avere installato il package per poi eseguirlo.

Se non è installato fa parte di requirements.txt quindi basta eseguire `pip install -r requirements.txt` dalla cartella in cui si è clonato il progetto e poi avviare jupyter chiamando `jupyter notebook` sempre da linea di comando.

Su windows potrebbe essere necessario eseguire `python -m notebook` al posto del comando sopra.

Si noti che su VSCode l'output latex non funziona per delle differenze nel modo di rendering, ho dato priorità a jupyter perché è il metodo consigliato di usare i notebook.
## Contribuzione
Si accettano cambiamenti tramite pull request
