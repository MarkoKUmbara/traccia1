import socket
import sys
import time

PORT = 6500
ROUTER = ""
INDIRIZZO = (ROUTER, PORT)

FORMAT = 'utf-8'
SIZE = 1024

# Messaggi per la connessione dei client
DISCONNECT_MESSAGE  = "!DISCONNECT"
CONNECT_MESSAGE     = "!CONNECT"
CLIENT_OFFLINE      = "!CLIENT_OFFLINE"
GO_ONLINE_MESSAGE   = "!GO_ONLINE"
GO_OFFLINE_MESSAGE  = "!GO_OFFLINE"


client_ip   = "92.10.10.15"
client_mac  = "32:04:0A:EF:19:CF"

router_ip   = "92.10.10.1"
router_mac  = "55:04:0A:EF:11:CF"

client2_ip = "92.10.10.20"
client3_ip = "92.10.10.25"
client4_ip = "1.5.10.10"
client5_ip = "1.5.10.20"
client6_ip = "1.5.10.30"

# Creo una lista di client
client_list = [client2_ip, client3_ip, client4_ip, client5_ip, client6_ip]

# creo il client socket e lo connetto al router
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(INDIRIZZO)

# Creo delle funzioni che usero piu avanti
def send(sms):
    sms = sms.encode(FORMAT)
    client.send(sms)

def send_packet(sms, destination_ip):
    ethernet_header = client_mac + router_mac
    IP_header = client_ip + destination_ip
    packet = ethernet_header + IP_header + sms
    send(packet)

def wait_message():
    sms = client.recv(SIZE)
    sms = sms.decode(FORMAT)
    return sms

def wait_packet():
    sms = wait_message()
    source_ip = sms[34:45]
    message = sms[56:]
    print(f"[{source_ip}] : {message}")

def select_ip():
    while True:
        i = 0
        print()
        for c in client_list:
            i += 1
            print(f"{i}- {c}")
        ip_selected = input("Select the number relative to IP: ")
        if ip_selected != '1' and ip_selected != '2' and ip_selected != '3' and ip_selected != '4' and ip_selected != '5':
            print("\nIP doesn't exist - Retry...")
        else:
            break
    if ip_selected == '1':
        ip_selected = client2_ip
    elif ip_selected == '2':
        ip_selected = client3_ip
    elif ip_selected == '3':
        ip_selected = client4_ip + "  "
    elif ip_selected == '4':
        ip_selected = client5_ip + "  "
    elif ip_selected == '5':
        ip_selected = client6_ip + "  "
    print(f"\n{ip_selected}")
    return ip_selected


def handle_menu(j, client_ip):
    if j == '1':
        ip_selected = select_ip()
        sms = input("Insert the message: ")
        if len(client_ip) < 11:
            while len(client_ip) != 11:
                client_ip = client_ip + " "
        if len(ip_selected) < 11:
            while len(ip_selected) != 11:
                ip_selected = ip_selected + " "
        send_packet(sms, ip_selected)
        time.sleep(2)
        message = wait_message()
        print(message)
    elif j == '2':
        wait_packet()
    elif j == '3':
        send(GO_OFFLINE_MESSAGE)
        print("You are offline ")
        print("Press any key to reconnect to the server")
        m = input()
        send(GO_ONLINE_MESSAGE)
    elif j == '4':
        send(DISCONNECT_MESSAGE)
        client.close()
        sys.exit()
    else:
        print("Input error...  Try again...")

def menu():
    while True:
        j = input("\n1- Send a message to another client\n2- Waiting for a message\n3- Go offline\n4- Exit\nSelect an action:")
        handle_menu(j, client_ip)

# Invio al router l'ip/mac address
send(client_mac + client_ip)

menu()
