from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

#Pra rodar essa bagaça, executa: python server.py e torçe pra funcionar, pq na minha maquina funcionou kkkk...

#Eu n sei se era pra juntar os dados do arquivo de origem com os dados do cliente e salvar tudo no arquivo de destino.... mas é isso, eu acho...

# Página inicial. Ele é enviado como resposta de uma requisição .get...
html_form = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Formulário - Atividade 2</title>
</head>
<body>
    <main>
        <article>
            <section>
                <div>
                    <h2>Formulário Atividade 2</h2>
                    <form action="/" method="post">
                        <label for="nome">Nome:</label><br>
                        <input type="text" id="nome" name="nome"><br>
                        <label for="idade">Idade:</label><br>
                        <input type="text" id="idade" name="idade"><br><br>
                        <input type="submit" value="Enviar">
                    </form>
                </div>
            </section>
        </article>
    </main>

</body>
</html>
"""

# Manipulando requisições. RequestHandler() processa as requisições HTTP q ocorrerem...
class RequestHandler(BaseHTTPRequestHandler):
    
    # Tratando requisições GET...
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_form.encode('utf-8'))

    # Fazendo o mesmo com requisições POST...
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        parsed_data = urllib.parse.parse_qs(post_data)
        
        nome = parsed_data['nome'][0]
        idade = parsed_data['idade'][0]
        
        # Salva os dados em um arquivo txtzin...
        with open('dados_cliente.txt', 'w') as file:
            file.write(f'Nome: {nome}\nIdade: {idade}')
        
        # Responde ao cliente com os dados do formulário...
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        response = f"""
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Resposta do Servidor - Atividade 2</title>
        </head>
        <body>
            <main>
                <article>
                    <section>
                        <div>
                            <h2>Dados Recebidos</h2>
                            <p>Nome: {nome}</p>
                            <p>Idade: {idade}</p>
                        </div>
                    </section>
                </article>
            </main>
        </body>
        </html>
        """
        self.wfile.write(response.encode('utf-8'))

# Aqui tu pdoe configurar o servidor, ajustando a porta e talz....
def run_server(port=8000): # Aqui tu pode alterar a porta pra rodar o server em outra se quiser, eu coloco sempre 8000...
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f'Servidor HTTP iniciado em http://localhost:{port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()