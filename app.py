import sys
import threading
import socket

#O envio usando os paranauê dos TCP UDP eu n sei direito se ta certo, mas funcionou na minha maquina kkkk...
#Pra testar o envio pra servidores TCP e UDP criei dois servers pra isso. Não sei se é assim q a atividade pedia, mas já estão recebendo os dados...
#Tu deve ter imaginado isso já, mas por desencargo de consciencia, é preciso que os dois servidores estejam sendo executados juntos.



#Pra tu testar, depois do python ta instalado no pc né, executa: python app.py arquivo_origem.txt arquivo_destino.txt
#Do jeito q ta no main()...

#O servidor tem q ta rodando já pra receber a requisição e o programa conseguir enviar o arquivo, se não, ele só copia pro arquivo de destino e acusa o erro do except...

#Acho que de resto ta tudo certo...


def copy_file(source_file, dest_file): #aqui, copy_file() ta lendo o arquivo de origem de 1024 em 1024 bytes e escrevendo ao msm tempo...    
    try:
        with open(source_file, 'rb') as sf, open(dest_file, 'wb') as df:
            while True:
                data = sf.read(1024)
                if not data:
                    break
                df.write(data)
        print(f"Cópia do arquivo '{source_file}' para '{dest_file}' concluída. Felicidade!")#lembrar de alterar antes de entregar a atividade....
    except Exception as e:
        print(f"Erro ao copiar arquivo: {e}. Alguma merda deu..")#lembrar de alterar antes de entregar a atividade....

def send_file_tcp(file_path, host, port): #aqui, send_file_tcp() tenta se conectar com um servidor TCP e enviar o arquivo...
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    s.sendall(data)
        print(f"Envio do arquivo '{file_path}' via TCP para {host}:{port} concluído. Mais felicidade!!")#lembrar de alterar antes de entregar a atividade....
    except Exception as e:
        print(f"Erro ao enviar arquivo via TCP: {e}. Frustração é uma merda....")#lembrar de alterar antes de entregar a atividade....

def send_file_udp(file_path, host, port): #aqui, send_file_udp() tenta enviar o arquivo pra um servidor UDP...
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    s.sendto(data, (host, port))
        print(f"Envio do arquivo '{file_path}' via UDP para {host}:{port} concluído. É Natal na Leader...")#lembrar de alterar antes de entregar a atividade....
    except Exception as e:
        print(f"Erro ao enviar arquivo via UDP: {e}.  Frustração é uma merda tão grande nesse ramo...")#lembrar de alterar antes de entregar a atividade....

def main(): #aqui, main() é onde chama as funções pra ler os argumentos com o sys.argv. N sei se era assim q devia fazer, mas...
    if len(sys.argv) != 3:
        print("Uso: python app.py <arquivo_origem> <arquivo_destino>")
        sys.exit(1)

    source_file = sys.argv[1]
    dest_file = sys.argv[2]

    copy_file(source_file, dest_file)

    #combinando com as portas q eu defini nos servidores, pode alterar se quiser mas precisa ta tudo certo, se n da merda...
    host = 'localhost'
    tcp_port = 5000 
    udp_port = 5001

    tcp_thread = threading.Thread(target=send_file_tcp, args=(dest_file, host, tcp_port))
    udp_thread = threading.Thread(target=send_file_udp, args=(dest_file, host, udp_port))

    tcp_thread.start()
    udp_thread.start()

    tcp_thread.join()
    udp_thread.join()

if __name__ == "__main__":
    main()
