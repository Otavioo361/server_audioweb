# Importa as classes Flask, render_template e request da biblioteca Flask
from flask import Flask, render_template, request
import os  # Importa o módulo os para lidar com funcionalidades relacionadas ao sistema operacional
import Pyro4  # Importa o módulo Pyro4 para suporte à comunicação entre processos distribuídos

# Cria uma instância da classe Flask e atribui ao objeto "app"
app = Flask(__name__)

# Substitua pelo endereço IP da máquina de destino na rede local
server_ip = "192.168.0.100"  # Exemplo de endereço IP
# Cria a URI para o servidor Pyro4
uri = "PYRO:server@{server_ip}:5050".format(server_ip=server_ip)
# Cria um objeto Proxy para se comunicar com o servidor Pyro4
server = Pyro4.Proxy(uri)
token = None  # Variável para armazenar o token de autenticação do usuário


# Define a rota "/" para manipular solicitações GET e POST
@app.route('/', methods=['GET', 'POST'])
def index():
    global token  # Indica que a variável token é global
    error_message = ''  # Variável para armazenar mensagens de erro inicializada como vazia

    if request.method == 'POST':  # Verifica se a solicitação é do tipo POST
        # Obtém o valor do campo "username" do formulário enviado
        username = request.form['username']
        # Obtém o valor do campo "password" do formulário enviado
        password = request.form['password']

        try:
            # Autentica o usuário chamando o método "authenticate" do servidor Pyro4
            token = server.authenticate(username, password)
            if token is not None:  # Verifica se o token de autenticação foi obtido com sucesso
                return render_template('index.html', token=token, logged_in=True, error_message=error_message, success_message='')
                # Renderiza o template "index.html" com o token, indicando que o usuário está logado
            else:
                # Define uma mensagem de erro caso a autenticação falhe
                error_message = 'Usuário ou senha incorretos'

        except Pyro4.errors.CommunicationError:
            # Define uma mensagem de erro caso ocorra um erro de comunicação com o servidor
            error_message = 'O servidor está fechado'

    return render_template('index.html', token=token, logged_in=False, error_message=error_message, success_message='')
    # Renderiza o template "index.html" sem um token, indicando que o usuário não está logado


# Define a rota "/send" para manipular solicitações POST
@app.route('/send', methods=['POST'])
def send_message():
    if token is None:  # Verifica se o usuário está logado (token não é None)
        # Retorna uma mensagem informando que o usuário precisa fazer login
        return 'Faça login para enviar mensagens'

    # Obtém o valor do campo "message" do formulário enviado, removendo espaços em branco desnecessários
    message = request.form['message'].strip()

    if not message:  # Verifica se a mensagem está vazia
        # Define uma mensagem de erro caso a mensagem esteja vazia
        error_message = 'A mensagem não pode estar vazia'
