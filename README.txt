Traccia 1

Marko Kumbara


Il progetto consiste nel creare 6 client, 2 router e 1 server in grado di comunicare tra loro.
Per far in modo che il server e i router comunichino correttamente è importante avviare prima il server e poi il router1 e dopo il secondo.
L'ordine dell'attivazione dei client non è importante.
Ho usato dei thread nei router e server per gestire i client e router in maniera singolare.
Nel router ho diviso le connessioni con i client e i server, in questa maniera quando il server invia un messaggio al router non ci sono problemi di richieste di comunicazioni precedenti.
