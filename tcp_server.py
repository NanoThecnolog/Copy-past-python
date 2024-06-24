import socket

#Pra startar o server: python tcp_server.py

def start_tcp_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Servidor TCP ouvindo em {host}:{port}")
        conn, addr = s.accept()
        with conn:
            print(f"Conectado por {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"Recebido: {data}")

if __name__ == "__main__":
    start_tcp_server('localhost', 5000)
