import socket
import time
# L'utilizzo dei thread mi permette di creare un router dinamico
import threading

# Creo alcune costanti che mi torneranno utili durate la scrittura del codice
SERVER = ""
PORT = 5500
ADDR_SERVER = (SERVER, PORT)
ADDR = ("", 6000)

FORMAT = 'utf-8'
SIZE = 1024

# Messaggi per la connessione dei client
DISCONNECT_MESSAGE  = "!DISCONNECT"
CONNECT_MESSAGE     = "!CONNECT"
CLIENT_OFFLINE      = "!CLIENT_OFFLINE"
GO_OFFLINE_MESSAGE = "!GO_OFFLINE"

router_mac = "32:03:0A:CF:10:DB"
router_ip = "195.1.10.2"

server_mac = "52:AB:0A:DF:10:DC"
server_ip = "195.1.10.10"

arp_table_socket = { "ip" : "socket"}
arp_table_mac = {"ip" : "mac"}
client_ip = []

router = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
router.bind(ADDR)
print("ROUTER is starting..")

router_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
router_send.connect(ADDR_SERVER)

# Metto il router in attesa che il server gli comunichi l'avvio
# Questo perche il server non funziona se non sono collegati ambi due i router
router_send.recv(SIZE)
print("connected to the SERVER")

# Creo alcune funzioni che mi torneranno utili
def send(conn, msg):
    msg = msg.encode(FORMAT)
    conn.send(msg)

def send_packet(conn, msg, source_mac, destination_mac, ip, destination_ip):
    ethernet_header = source_mac + destination_mac
    IP_header = ip + destination_ip
    packet = ethernet_header + IP_header + msg
    send(conn, packet)

def recv_message(conn):
    msg = conn.recv(SIZE).decode(FORMAT)
    return msg

def disconnect_client(msg, ip):
    message = msg + ip
    send(router_send, message)
    ip = ip.replace(" ", "")
    client_ip.remove(ip)
    return False

def go_offline_client(ip):
    message = DISCONNECT_MESSAGE + ip
    send(router_send, message)

def pause(conn, ip):
    msg = recv_message(conn)
    send(router_send, (CONNECT_MESSAGE + ip))

# Gestisco i client
def handle_client(conn, addr):
    mac_ip= recv_message(conn)
    ip = mac_ip[17:].replace(" ", "")
    connected = True
    # Controllo che non esistano client con lo stesso ip
    for c in client_ip:
        if c == ip:
            connected = False
    if connected == True:
        client_ip.append(ip)
        arp_table_socket[ip] = conn
        arp_table_mac[ip] = mac_ip[0:17]
        while len(ip) < 11:
            ip = ip + " "
        send(router_send, (CONNECT_MESSAGE + ip))
    try:
        while connected:
            msg = recv_message(conn)
            if msg == DISCONNECT_MESSAGE:
                connected = disconnect_client(msg, ip)
            elif msg == GO_OFFLINE_MESSAGE:
                go_offline_client(ip)
                pause(conn, ip)
            else:
                destination_ip = msg[45:56]
                send(router_send, "!IS_ONLINE" + destination_ip + ip)
                time.sleep(2)
                msg = msg[56:]
                send_packet(router_send, msg, router_mac, server_mac, ip, destination_ip)
        conn.close()
    except BrokenPipeError:
        print("BrokenPipeError")

def handle_server(server, client_side):
    while True:
        msg = recv_message(server)
        if msg[0:1] == "!":
            if msg[0:10] == "!IS_ONLINE":
                ip = msg[21:].replace(" ", "")
                send(arp_table_socket[ip], "MESSAGE SENT")
            elif msg[0:11] == "!IS_OFFLINE":
                ip = msg[22:].replace(" ", "")
                send(arp_table_socket[ip], "CLIENT OFFLINE")
        else:
            client_reference = msg[45:56]
            client_reference = client_reference.replace(" ", "")
            conn = arp_table_socket[client_reference]
            source_mac = router_mac
            destination_mac = arp_table_mac[client_reference]
            ip = msg[34:45]
            destination_ip = msg[45:56]
            message = msg[56:]
            send_packet(conn, message, source_mac, destination_mac, ip, destination_ip)

# Gestisco gli accessi
def start():
    router.listen()
    print("ROUTER is running...")
    flag = False
    while True:
        conn, addr = router.accept()
        thread = threading.Thread(target = handle_client, args = (conn, addr))
        thread.start()

thread = threading.Thread(target = handle_server, args = (router_send, router))
thread.start()

start()
