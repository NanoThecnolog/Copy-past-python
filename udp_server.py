import socket

#Pra startar o server: python udp_server.py

def start_udp_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((host, port))
        print(f"Servidor UDP ouvindo em {host}:{port}")
        while True:
            data, addr = s.recvfrom(1024)
            print(f"Recebido de {addr}: {data}")

if __name__ == "__main__":
    start_udp_server('localhost', 5001)
