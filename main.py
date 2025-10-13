

import speech_recognition as sr
import pyttsx3
import os
import sys
import subprocess
import platform
import webbrowser
from datetime import datetime
import psutil
import random

class AssistenteVoz:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        self.engine = pyttsx3.init()
        self.configurar_voz()

        self.sistema = platform.system()
        self.apps = self.configurar_apps()
        self.processos = self.configurar_processos()
        self.nome_usuario = "Mestre Eduardo"

    def configurar_voz(self):
        voices = self.engine.getProperty('voices')

        for voice in voices:
            if 'portuguese' in voice.name.lower() or 'brasil' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

        self.engine.setProperty('rate', 180)  
        self.engine.setProperty('volume', 0.9) 

    def configurar_apps(self):
        if self.sistema == "Windows":
            return {
                'netflix': 'start shell:AppsFolder\\4DF9E0F8.Netflix_mcm4njqhnhss8!Netflix.App',
                'opera': 'C:\\Program Files\\Opera\\launcher.exe',
                'discord': os.path.join(os.getenv('LOCALAPPDATA'), 'Discord\\Update.exe --processStart Discord.exe'),
                'whatsapp': 'start shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!WhatsAppDesktop',
                'chrome': 'start chrome',
                'edge': 'start microsoft-edge:',
                'spotify': 'start spotify:',
                'steam': 'C:\\Program Files (x86)\\Steam\\steam.exe',
                'cursor': 'cursor .',
                'vscode': 'code .'
            }
        elif self.sistema == "Linux":
            return {
                'netflix': 'xdg-open https://www.netflix.com',
                'opera': 'opera',
                'discord': 'discord',
                'whatsapp': 'whatsapp-for-linux',
                'chrome': 'google-chrome',
                'firefox': 'firefox',
                'spotify': 'spotify',
                'steam': 'steam',
                'cursor': 'cursor .',
                "vscode": 'code .'
            }
        elif self.sistema == "Darwin":
            return {
                'netflix': 'open -a "Netflix"',
                'opera': 'open -a "Opera"',
                'discord': 'open -a "Discord"',
                'whatsapp': 'open -a "WhatsApp"',
                'chrome': 'open -a "Google Chrome"',
                'safari': 'open -a "Safari"',
                'spotify': 'open -a "Spotify"',
                'steam': 'open -a "Steam"',
                'cursor': 'cursor .',
                "vscode": "code ."
            }
        return {}

    def configurar_processos(self):
        if self.sistema == "Windows":
            return {
                'netflix': 'Netflix.exe',
                'opera': 'opera.exe',
                'discord': 'Discord.exe',
                'whatsapp': 'WhatsApp.exe',
                'chrome': 'chrome.exe',
                'edge': 'msedge.exe',
                'spotify': 'Spotify.exe',
                'steam': 'steam.exe',
            }
        elif self.sistema == "Linux":
            return {
                'netflix': 'firefox',
                'opera': 'opera',
                'discord': 'discord',
                'whatsapp': 'whatsapp-for-linux',
                'chrome': 'chrome',
                'firefox': 'firefox',
                'spotify': 'spotify',
                'steam': 'steam',
            }
        elif self.sistema == "Darwin":
            return {
                'netflix': 'Netflix',
                'opera': 'Opera',
                'discord': 'Discord',
                'whatsapp': 'WhatsApp',
                'chrome': 'Google Chrome',
                'safari': 'Safari',
                'spotify': 'Spotify',
                'steam': 'Steam',
            }
        return {}

    def falar(self, texto):
        print(f"🤖 Assistente: {texto}")
        self.engine.say(texto)
        self.engine.runAndWait()

    def ouvir(self):
        with self.microphone as source:
            print("\n🎤 Escutando... (fale agora)")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                print("🔄 Processando...")

                comando = self.recognizer.recognize_google(audio, language='pt-BR')
                print(f"✅ Você disse: {comando}")
                return comando.lower()

            except sr.WaitTimeoutError:
                print("⏱️  Tempo esgotado. Nenhum comando detectado.")
                return ""
            except sr.UnknownValueError:
                print("❌ Não consegui entender o que você disse.")
                return ""
            except sr.RequestError as e:
                print(f"❌ Erro no serviço de reconhecimento: {e}")
                return ""

    def desligar_pc(self):
        self.falar("Desligando o computador em 5 segundos. Até logo!")

        if self.sistema == "Windows":
            os.system("shutdown /s /t 5")
        elif self.sistema == "Linux":
            os.system("shutdown -h +1")
        elif self.sistema == "Darwin":
            os.system("sudo shutdown -h +1")

    def reiniciar_pc(self):
        self.falar("Reiniciando o computador em 5 segundos.")

        if self.sistema == "Windows":
            os.system("shutdown /r /t 5")
        elif self.sistema == "Linux":
            os.system("shutdown -r +1")
        elif self.sistema == "Darwin":
            os.system("sudo shutdown -r +1")

    def cancelar_desligamento(self):
        self.falar("Cancelando o desligamento.")

        if self.sistema == "Windows":
            os.system("shutdown /a")
        elif self.sistema in ["Linux", "Darwin"]:
            os.system("sudo shutdown -c")

    def abrir_app(self, app_nome):
        if app_nome in self.apps:
            self.falar(f"Abrindo {app_nome}")
            try:
                if self.sistema == "Windows":
                    os.system(self.apps[app_nome])
                else:
                    subprocess.Popen(self.apps[app_nome], shell=True)
                return True
            except Exception as e:
                self.falar(f"Erro ao abrir {app_nome}")
                print(f"Erro: {e}")
                return False
        else:
            self.falar(f"Desculpe, não sei como abrir {app_nome}")
            return False

    def fechar_app(self, app_nome):
        if app_nome in self.processos:
            self.falar(f"Fechando {app_nome}")
            try:
                if self.sistema == "Windows":
                    os.system(f"taskkill /F /IM {self.processos[app_nome]}")
                elif self.sistema == "Linux":
                    os.system(f"pkill -f {self.processos[app_nome]}")
                elif self.sistema == "Darwin":
                    os.system(f"killall '{self.processos[app_nome]}'")
                return True
            except Exception as e:
                self.falar(f"Erro ao fechar {app_nome}")
                print(f"Erro: {e}")
                return False
        else:
            self.falar(f"Desculpe, não sei como fechar {app_nome}")
            return False

    def abrir_site(self, site):
        sites = {
            'youtube': 'https://www.youtube.com',
            'google': 'https://www.google.com',
            'facebook': 'https://www.facebook.com',
            'instagram': 'https://www.instagram.com',
            'twitter': 'https://www.twitter.com',
            'github': 'https://www.github.com',
            'amazon': 'https://www.amazon.com.br',
            'mercado livre': 'https://www.mercadolivre.com.br',
        }

        if site in sites:
            self.falar(f"Abrindo {site}")
            webbrowser.open(sites[site])
            return True
        else:
            self.falar(f"Desculpe, não sei o endereço de {site}")
            return False

    def pesquisar_google(self, termo):
        self.falar(f"Pesquisando {termo} no Google")
        url = f"https://www.google.com/search?q={termo}"
        webbrowser.open(url)

    def pesquisar_youtube(self, termo):
        self.falar(f"Pesquisando {termo} no YouTube")
        url = f"https://www.youtube.com/results?search_query={termo}"
        webbrowser.open(url)

    def que_horas_sao(self):
        agora = datetime.now()
        horas = agora.strftime("%H:%M")
        self.falar(f"São {horas}")

    def que_dia_e_hoje(self):
        agora = datetime.now()
        dias_semana = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']
        dia_semana = dias_semana[agora.weekday()]
        data = agora.strftime("%d de %B de %Y")
        self.falar(f"Hoje é {dia_semana}, dia {data}")

    def aumentar_volume(self):
        self.falar("Aumentando o volume")
        if self.sistema == "Windows":
            os.system("nircmd.exe changesysvolume 5000")
        elif self.sistema == "Linux":
            os.system("amixer -D pulse sset Master 10%+")
        elif self.sistema == "Darwin":
            os.system("osascript -e 'set volume output volume (output volume of (get volume settings) + 10)'")

    def diminuir_volume(self):
        self.falar("Diminuindo o volume")
        if self.sistema == "Windows":
            os.system("nircmd.exe changesysvolume -5000")
        elif self.sistema == "Linux":
            os.system("amixer -D pulse sset Master 10%-")
        elif self.sistema == "Darwin":
            os.system("osascript -e 'set volume output volume (output volume of (get volume settings) - 10)'")

    def silenciar_volume(self):
        self.falar("Silenciando")
        if self.sistema == "Windows":
            os.system("nircmd.exe mutesysvolume 1")
        elif self.sistema == "Linux":
            os.system("amixer -D pulse set Master mute")
        elif self.sistema == "Darwin":
            os.system("osascript -e 'set volume output muted true'")

    def bloquear_pc(self):
        self.falar("Bloqueando o computador")
        if self.sistema == "Windows":
            os.system("rundll32.exe user32.dll,LockWorkStation")
        elif self.sistema == "Linux":
            os.system("gnome-screensaver-command -l")
        elif self.sistema == "Darwin":
            os.system("/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession -suspend")

    def info_sistema(self):
        try:
            cpu = psutil.cpu_percent(interval=1)
            memoria = psutil.virtual_memory().percent
            disco = psutil.disk_usage('/').percent

            self.falar(f"Uso da CPU: {cpu} por cento. Uso da memória: {memoria} por cento. Uso do disco: {disco} por cento")
            print(f"\n💻 INFORMAÇÕES DO SISTEMA:")
            print(f"  CPU: {cpu}%")
            print(f"  Memória: {memoria}%")
            print(f"  Disco: {disco}%")
        except Exception as e:
            self.falar("Erro ao obter informações do sistema")
            print(f"Erro: {e}")

    def contar_piada(self):
        piadas = [
            "Por que o Python foi ao médico? Porque estava com problemas de sintaxe!",
            "Por que os programadores preferem o modo escuro? Porque a luz atrai bugs!",
            "O que o Java disse para o C? Você não tem classe!",
            "Por que o notebook foi ao psicólogo? Porque tinha muitos problemas internos!",
            "Qual é o cantor favorito dos programadores? Loop Fiasco!",
        ]
        self.falar(random.choice(piadas))

    def tocar_musica_aleatoria(self):
        self.falar(f"Abrindo música para você, {self.nome_usuario}")
        webbrowser.open("https://www.youtube.com/results?search_query=música+relaxante")

    def modo_produtivo(self):
        self.falar(f"Ativando modo produtivo, {self.nome_usuario}")
        if self.sistema == "Windows":
            os.system("taskkill /F /IM chrome.exe /FI \"WINDOWTITLE eq *Facebook*\"")
            os.system("taskkill /F /IM chrome.exe /FI \"WINDOWTITLE eq *Instagram*\"")

    def tirar_screenshot(self):
        self.falar("Capturando a tela")
        if self.sistema == "Windows":
            os.system("snippingtool")
        elif self.sistema == "Linux":
            os.system("gnome-screenshot -i")
        elif self.sistema == "Darwin":
            os.system("screencapture -i ~/Desktop/screenshot.png")

    def limpar_tela(self):
        os.system('cls' if self.sistema == "Windows" else 'clear')
        self.falar("Tela limpa")

    def abrir_calculadora(self):
        self.falar("Abrindo calculadora")
        if self.sistema == "Windows":
            os.system("calc")
        elif self.sistema == "Linux":
            os.system("gnome-calculator &")
        elif self.sistema == "Darwin":
            os.system("open -a Calculator")

    def abrir_bloco_notas(self):
        self.falar("Abrindo bloco de notas")
        if self.sistema == "Windows":
            os.system("notepad")
        elif self.sistema == "Linux":
            os.system("gedit &")
        elif self.sistema == "Darwin":
            os.system("open -a TextEdit")

    def abrir_gerenciador_tarefas(self):
        self.falar("Abrindo gerenciador de tarefas")
        if self.sistema == "Windows":
            os.system("taskmgr")
        elif self.sistema == "Linux":
            os.system("gnome-system-monitor &")
        elif self.sistema == "Darwin":
            os.system("open -a 'Activity Monitor'")

    def abrir_previsao_tempo(self):
        self.falar("Abrindo previsão do tempo")
        webbrowser.open("https://www.google.com/search?q=previsão+do+tempo")

    def abrir_noticias(self):
        self.falar("Abrindo notícias")
        webbrowser.open("https://news.google.com")

    def abrir_email(self):
        self.falar("Abrindo email")
        webbrowser.open("https://mail.google.com")

    def processar_comando(self, comando):
        if not comando:
            return True

        # Comandos de controle do sistema
        if "desligar" in comando or "desliga" in comando:
            self.desligar_pc()
            return False

        elif "reiniciar" in comando or "reinicia" in comando:
            self.reiniciar_pc()
            return False

        elif "cancelar" in comando and ("desligar" in comando or "desligamento" in comando):
            self.cancelar_desligamento()

        elif "abrir" in comando or "abre" in comando or "abra" in comando:
            for app in self.apps.keys():
                if app in comando:
                    self.abrir_app(app)
                    break
            else:
                self.falar("Não identifiquei qual aplicativo você quer abrir.")

        elif "fechar" in comando or "fecha" in comando or "feche" in comando:
            for app in self.processos.keys():
                if app in comando:
                    self.fechar_app(app)
                    break
            else:
                self.falar("Não identifiquei qual aplicativo você quer fechar.")

        elif "abrir site" in comando or "acessar" in comando:
            sites = ['youtube', 'google', 'facebook', 'instagram', 'twitter', 'github', 'amazon', 'mercado livre']
            for site in sites:
                if site in comando:
                    self.abrir_site(site)
                    break
            else:
                self.falar("Não identifiquei qual site você quer abrir.")

        elif "pesquisar no google" in comando or "buscar no google" in comando:
            termo = comando.replace("pesquisar no google", "").replace("buscar no google", "").strip()
            if termo:
                self.pesquisar_google(termo)
            else:
                self.falar("O que você quer pesquisar?")

        elif "pesquisar no youtube" in comando or "buscar no youtube" in comando:
            termo = comando.replace("pesquisar no youtube", "").replace("buscar no youtube", "").strip()
            if termo:
                self.pesquisar_youtube(termo)
            else:
                self.falar("O que você quer pesquisar?")

        elif "que horas são" in comando or "que horas" in comando or "horas" in comando:
            self.que_horas_sao()

        elif "que dia é hoje" in comando or "que dia" in comando or "data" in comando:
            self.que_dia_e_hoje()

        elif "aumentar volume" in comando or "aumenta volume" in comando:
            self.aumentar_volume()

        elif "diminuir volume" in comando or "diminui volume" in comando or "abaixar volume" in comando:
            self.diminuir_volume()

        elif "silenciar" in comando or "mudo" in comando or "silêncio" in comando:
            self.silenciar_volume()

        elif "bloquear" in comando or "travar" in comando:
            self.bloquear_pc()

        elif "informações do sistema" in comando or "status do sistema" in comando or "info sistema" in comando:
            self.info_sistema()

        elif "olá" in comando or "oi" in comando:
            saudacoes = [
                f"Olá {self.nome_usuario}! Como posso ajudá-lo?",
                f"Oi {self.nome_usuario}! Estou às suas ordens!",
                f"Olá {self.nome_usuario}! Pronto para atendê-lo!"
            ]
            self.falar(random.choice(saudacoes))

        elif "como você está" in comando or "tudo bem" in comando:
            self.falar(f"Estou funcionando perfeitamente, {self.nome_usuario}! Obrigado por perguntar!")

        elif "qual é o seu nome" in comando or "quem é você" in comando:
            self.falar(f"Sou seu assistente pessoal, criado para servir você, {self.nome_usuario}")

        elif "contar piada" in comando or "conte uma piada" in comando:
            self.contar_piada()

        elif "tocar música" in comando or "reproduzir música" in comando:
            self.tocar_musica_aleatoria()

        elif "modo produtivo" in comando or "foco total" in comando:
            self.modo_produtivo()

        elif "tirar screenshot" in comando or "capturar tela" in comando:
            self.tirar_screenshot()

        elif "limpar tela" in comando or "limpar terminal" in comando:
            self.limpar_tela()

        elif "abrir calculadora" in comando:
            self.abrir_calculadora()

        elif "abrir bloco de notas" in comando or "abrir notepad" in comando:
            self.abrir_bloco_notas()

        elif "lista de tarefas" in comando or "gerenciador de tarefas" in comando:
            self.abrir_gerenciador_tarefas()

        elif "clima" in comando or "tempo" in comando or "previsão" in comando:
            self.abrir_previsao_tempo()

        elif "notícias" in comando:
            self.abrir_noticias()

        elif "email" in comando or "e-mail" in comando:
            self.abrir_email()

        elif "ajuda" in comando or "comandos" in comando:
            self.mostrar_ajuda()

        elif "sair" in comando or "encerrar" in comando or "tchau" in comando:
            despedidas = [
                f"Até logo, {self.nome_usuario}! Foi um prazer servi-lo!",
                f"Encerrando, {self.nome_usuario}. Estarei aqui quando precisar!",
                f"Até breve, {self.nome_usuario}!"
            ]
            self.falar(random.choice(despedidas))
            return False

        else:
            self.falar("Desculpe, não entendi o comando.")

        return True

    def mostrar_ajuda(self):
        comandos = [
            "Desligar/Reiniciar/Cancelar desligamento/Bloquear o computador",
            "Abrir aplicativos: " + ", ".join(list(self.apps.keys())[:5]) + "...",
            "Fechar aplicativos: " + ", ".join(list(self.processos.keys())[:5]) + "...",
            "Abrir sites: YouTube, Google, Facebook, Instagram, etc.",
            "Pesquisar no Google/YouTube: [termo]",
            "Que horas são / Que dia é hoje",
            "Aumentar/Diminuir/Silenciar volume",
            "Informações do sistema",
            "Contar piada / Tocar música",
            "Modo produtivo / Tirar screenshot",
            "Abrir calculadora / Bloco de notas / Gerenciador de tarefas",
            "Clima / Notícias / Email",
            "Limpar tela",
            "Sair do assistente"
        ]

        print("\n📋 COMANDOS DISPONÍVEIS:")
        for cmd in comandos:
            print(f"  • {cmd}")

        self.falar("Mostrei os comandos disponíveis na tela.")

    def executar(self):
        self.falar(f"Olá {self.nome_usuario}! Assistente de voz iniciado e pronto para servi-lo. Diga 'ajuda' para ver os comandos disponíveis.")

        continuar = True
        while continuar:
            try:
                comando = self.ouvir()
                continuar = self.processar_comando(comando)
            except KeyboardInterrupt:
                self.falar("Encerrando o assistente.")
                break
            except Exception as e:
                print(f"❌ Erro inesperado: {e}")
                continuar = True


def main():
    print("="*60)
    print("🤖 ASSISTENTE DE VOZ PARA CONTROLE DO COMPUTADOR")
    print("="*60)
    print("\n⚠️  REQUISITOS:")
    print("  pip install SpeechRecognition pyttsx3 pyaudio")
    print("\n💡 DICA: Fale de forma clara e pausada")
    print("="*60)

    try:
        assistente = AssistenteVoz()
        assistente.executar()
    except Exception as e:
        print(f"\n❌ Erro ao iniciar o assistente: {e}")
        print("\nVerifique se você instalou todas as dependências:")
        print("  pip install SpeechRecognition pyttsx3 pyaudio")
        sys.exit(1)


if __name__ == "__main__":
    main()
