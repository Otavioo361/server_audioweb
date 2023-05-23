import Pyro4
from gtts import gTTS
import os
import threading
import time


@Pyro4.expose
class Server(object):
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.messagem)
        self.thread.start()

    def authenticate(self, username, password):
        if username == "otavio" and password == "otavio123":
            return "senha_certa"
        else:
            return None

    def messagem(self):
        while True:
            if len(self.queue) > 0:
                messages = []
                with self.lock:
                    while len(self.queue) > 0:
                        messages.append(self.queue.pop(0))
                for message in messages:
                    print("Mensagem recebida: ", message)
                    tts = gTTS(text=message, lang='pt-br')
                    tts.save("audio.mp3")
                    os.system("mpg321 audio.mp3")
                    time.sleep(1)
                    os.remove('audio.mp3')

    def receive_message(self, message, token):
        if token == "senha_certa":
            with self.lock:
                self.queue.append(message)
        else:
            print("Erro de autenticação")


server = Server()

# Crie um objeto Pyro4 daemon com o endereço IP da máquina e porta 5050
daemon = Pyro4.Daemon(host="127.0.0.1", port=5050)

# Registre o objeto Pyro4 com o endereço IP e porta do servidor
uri = daemon.register(server, "server")
ns = Pyro4.locateNS()
ns.register("server", uri)
print("Servidor registrado com sucesso em", uri)

# Inicie o loop de eventos do Pyro4 daemon
print("Aguardando conexões de clientes...")
daemon.requestLoop()