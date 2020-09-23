import socket
import time
import threading # Mi permnettera di gestire i due router contemporaneamente


# Creo delle costanti
SERVER = ""
PORT = 5500
INDIRIZZO = (SERVER, PORT)

FORMAT = 'utf-8'
SIZE = 1024

# Messaggi per la connessione dei client
DISCONNECT_MESSAGE  = "!DISCONNECT"
CONNECT_MESSAGE     = "!CONNECT"
CLIENT_OFFLINE      = "!CLIENT_OFFLINE"

server_ip   = "195.1.10.10"
server_mac  = "52:AB:0A:DF:10:DC"

router1_ip	= "195.1.10.1"
router1_mac	= "55:04:0A:EF:10:AB"
router2_ip  = "195.1.10.2"
router2_mac = "32:03:0A:CF:10:DB"

# Quando il server riceve un messaggio destinato a un cliente, prima verifica che esso è online
client_online = ["CLIENT ONLINE"]

# Creo il server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(INDIRIZZO)
print("SERVER is starting..")

# creo i riferimenti per i router
server.listen()
router1 = None
router2 = None

# Prima di avviare il server controllo che i router sono collegati
while router1 == None or router2 == None:
    router, indir = server.accept()
    if(router1 == None):
        router1 = router
        indir1 = indir
    elif router2 == None:
        router2 = router
        indir2 = indir

# Definisco alcune funzioni per operazioni frequenti
def send(conn, sms):
    sms = sms.encode(FORMAT)
    conn.send(sms)

def send_packet(router, source_ip, destination_ip, sms):
    if router == 1:
        router_mac = router1_mac
        conn = router1
    else:
        router_mac = router2_mac
        conn = router2
    ethernet_header = server_mac + router_mac
    IP_header = source_ip + destination_ip
    packet = ethernet_header + IP_header + sms
    send(conn, packet)

def recv_message(conn):
    sms = conn.recv(SIZE)
    sms = sms.encode(FORMAT)
    return sms

def check_connection(ip):
    flag = False
    for c in client_online:
        if c == ip:
            flag = True
            break
    return flag

def disconnect_ip(ip):
    if len(ip) < 11:
        while len(ip) < 11:
            ip = ip + " "
    flag = check_connection(ip)
    if flag == False:
        sms = "\nClient doesn't exist...\n"
    else:
        client_online.remove(ip)
        print(f"\nCLIENT {ip} is now offline...\n")
        sms = "\nSUCCESS\n"
    return sms

def handle_connection(conn, sms):
    if sms[0:8] == CONNECT_MESSAGE:
        ip = sms[8:]
        if len(ip) < 11:
            while len(ip) < 11:
                ip = ip + " "
        else:
            client_online.append(ip)
        print(f"\nCLIENT {ip} is now online\n")
        for s in client_online:
            print(s)
        return True
    elif sms[0:11] == DISCONNECT_MESSAGE:
        print(disconnect_ip(sms[11:]))
        return True
    elif sms[0:10] == "!IS_ONLINE":
        find = check_connection(sms[10:21])
        if find == True:
            returned = "!IS_ONLINE" + sms[10:]
        else:
            returned = "!IS_OFFLINE" + sms[10:]
        send(conn, returned)
        return find

def handle_message(conn, sms, flag):
    if flag == True:
        if sms[45:47] == "92":
            r = 1
        else:
            r = 2
        source_ip = sms[34:45]
        destination_ip = sms[45:56]
        message = sms[56:]
        send_packet(r, source_ip, destination_ip, message)

def start_router(router, indir):
    flag = True
    while True:
        sms = router.recv(1024).decode(FORMAT)
        if sms[0:1] == '!':
            flag = handle_connection(router, sms)
        else:
            handle_message(router, sms, flag)
            flag = True

# Una volta connesso a i due router, invia ad essi un messaggio per confermare l'avvio
send(router1, "OK")
send(router2, "OK")

c = 0
while c < 3:
    if c == 0:
        router = router1
        indir = indir1
    elif c == 1:
        router = router2
        indir = indir2
    thread = threading.Thread(target = start_router, args = (router, indir))
    thread.start()
    c += 1
