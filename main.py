#!/usr/bin/env python3
"""
Assistente de Voz para Controle do Computador
Requer: pip install SpeechRecognition pyaudio psutil edge-tts pygame
"""

import speech_recognition as sr
import os
import sys
import subprocess
import platform
import webbrowser
from datetime import datetime
import psutil
import random
import time
import asyncio
import tempfile
import edge_tts
import pygame
from pynput.keyboard import Key, Controller

async def _gerar_audio_edge_tts(texto: str, voz: str) -> str:
    communicate = edge_tts.Communicate(texto, voice=voz)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as handler:
        caminho = handler.name
    await communicate.save(caminho)
    return caminho

def _run_async(coro):
    try:
        return asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
        finally:
            try:
                loop.close()
            finally:
                asyncio.set_event_loop(None)

class AssistenteVoz:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        self.edge_tts_voice = os.getenv("EDGE_TTS_VOICE", "pt-BR-AntonioNeural")
        self._pygame_inicializado = False

        self.sistema = platform.system()
        self.apps = self.configurar_apps()
        self.processos = self.configurar_processos()
        self.nome_usuario = "Mestre Eduardo"

    def obter_saudacao_periodo(self):
        hora = datetime.now().hour
        if 5 <= hora < 12:
            return f"Bom dia, {self.nome_usuario}"
        elif 12 <= hora < 18:
            return f"Boa tarde, {self.nome_usuario}"
        else:
            return f"Boa noite, {self.nome_usuario}"

    def configurar_voz(self):
        return

    def configurar_apps(self):
        if self.sistema == "Windows":
            return {
                'netflix': 'start shell:AppsFolder\\4DF9E0F8.Netflix_mcm4njqhnhss8!Netflix.App',
                'opera': 'start opera',
                'opera gx': 'start opera',
                'discord': os.path.join(os.getenv('LOCALAPPDATA'), 'Discord\\Update.exe --processStart Discord.exe'),
                'whatsapp': 'start whatsapp:',
                'chrome': 'start chrome',
                'edge': 'start microsoft-edge:',
                'spotify': 'start spotify:',
                'steam': 'C:\\Program Files (x86)\\Steam\\steam.exe',
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
            }
        return {}

    def configurar_processos(self):
        if self.sistema == "Windows":
            return {
                'netflix': ['Netflix.exe', 'msedge.exe', 'chrome.exe'],
                'opera': 'opera.exe',
                'opera gx': 'opera.exe',
                'discord': 'Discord.exe',
                'whatsapp': ['WhatsApp.exe', 'msedge.exe', 'chrome.exe'],
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

        caminho = None
        try:
            caminho = _run_async(_gerar_audio_edge_tts(texto, voz=self.edge_tts_voice))

            if not self._pygame_inicializado:
                pygame.mixer.init()
                self._pygame_inicializado = True

            pygame.mixer.music.load(caminho)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        finally:
            if caminho and os.path.isfile(caminho):
                try:
                    os.unlink(caminho)
                except OSError:
                    pass

    def ouvir(self):
        with self.microphone as source:
            print("\n🎤 Ouvindo...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                print("🔄 Processando...")

                comando = self.recognizer.recognize_google(audio, language='pt-BR')
                print(f"👤 Você disse: {comando}")
                return comando.lower()

            except sr.WaitTimeoutError:
                print("⏱️  Tempo esgotado. Nenhum som detectado.")
                return None
            except sr.UnknownValueError:
                print("❌ Não consegui entender o que você disse.")
                return None
            except sr.RequestError:
                print("❌ Erro ao conectar ao serviço de reconhecimento de voz.")
                return None

    def abrir_app(self, app_nome):
        """Abre um aplicativo específico"""
        if app_nome in self.apps:
            self.falar(f"Abrindo {app_nome}")
            try:
                os.system(self.apps[app_nome])
                return True
            except Exception as e:
                self.falar(f"Erro ao abrir {app_nome}")
                print(f"Erro: {e}")
                return False
        else:
            self.falar(f"Desculpe, não sei como abrir {app_nome}")
            return False

    def fechar_app(self, app_nome):
        """Fecha um aplicativo específico"""
        if app_nome in self.processos:
            self.falar(f"Fechando {app_nome}")
            try:
                processos = self.processos[app_nome]
                if isinstance(processos, list):
                    fechou_algum = False
                    for processo in processos:
                        resultado = os.system(f"taskkill /F /IM {processo} 2>nul")
                        if resultado == 0:
                            fechou_algum = True
                    if not fechou_algum:
                        self.falar(f"{app_nome} não está aberto no momento")
                else:
                    if self.sistema == "Windows":
                        resultado = os.system(f"taskkill /F /IM {processos} 2>nul")
                        if resultado != 0:
                            self.falar(f"{app_nome} não está aberto no momento")
                    elif self.sistema == "Linux":
                        os.system(f"pkill -f {processos}")
                    elif self.sistema == "Darwin":
                        os.system(f"killall '{processos}'")
                return True
            except Exception as e:
                self.falar(f"Erro ao fechar {app_nome}")
                print(f"Erro: {e}")
                return False
        else:
            self.falar(f"Desculpe, não sei como fechar {app_nome}")
            return False

    def desligar_pc(self):
        """Desliga o computador"""
        self.falar("Desligando o computador em 1 minuto")
        if self.sistema == "Windows":
            os.system("shutdown /s /t 60")
        elif self.sistema == "Linux":
            os.system("shutdown -h +1")
        elif self.sistema == "Darwin":
            os.system("sudo shutdown -h +1")

    def reiniciar_pc(self):
        """Reinicia o computador"""
        self.falar("Reiniciando o computador em 1 minuto")
        if self.sistema == "Windows":
            os.system("shutdown /r /t 60")
        elif self.sistema == "Linux":
            os.system("shutdown -r +1")
        elif self.sistema == "Darwin":
            os.system("sudo shutdown -r +1")

    def cancelar_desligamento(self):
        """Cancela o desligamento do computador"""
        self.falar("Cancelando o desligamento")
        if self.sistema == "Windows":
            os.system("shutdown /a")
        elif self.sistema == "Linux":
            os.system("shutdown -c")
        elif self.sistema == "Darwin":
            os.system("sudo killall shutdown")

    def abrir_site(self, site):
        """Abre um site no navegador padrão"""
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
        """Faz uma pesquisa no Google"""
        self.falar(f"Pesquisando {termo} no Google")
        url = f"https://www.google.com/search?q={termo}"
        webbrowser.open(url)

    def pesquisar_youtube(self, termo):
        """Faz uma pesquisa no YouTube"""
        self.falar(f"Pesquisando {termo} no YouTube")
        url = f"https://www.youtube.com/results?search_query={termo}"
        webbrowser.open(url)

    def que_horas_sao(self):
        """Informa as horas atuais"""
        agora = datetime.now()
        horas = agora.strftime("%H:%M")
        self.falar(f"São {horas}")

    def que_dia_e_hoje(self):
        """Informa a data atual"""
        agora = datetime.now()
        dias_semana = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']
        dia_semana = dias_semana[agora.weekday()]
        data = agora.strftime("%d de %B de %Y")
        self.falar(f"Hoje é {dia_semana}, dia {data}")

    def aumentar_volume(self):
        """Aumenta o volume do sistema"""
        self.falar("Aumentando o volume")
        if self.sistema == "Windows":
            os.system("nircmd.exe changesysvolume 5000")
        elif self.sistema == "Linux":
            os.system("amixer -D pulse sset Master 10%+")
        elif self.sistema == "Darwin":
            os.system("osascript -e 'set volume output volume (output volume of (get volume settings) + 10)'")

    def diminuir_volume(self):
        """Diminui o volume do sistema"""
        self.falar("Diminuindo o volume")
        if self.sistema == "Windows":
            os.system("nircmd.exe changesysvolume -5000")
        elif self.sistema == "Linux":
            os.system("amixer -D pulse sset Master 10%-")
        elif self.sistema == "Darwin":
            os.system("osascript -e 'set volume output volume (output volume of (get volume settings) - 10)'")

    def silenciar_volume(self):
        """Silencia o volume do sistema"""
        self.falar("Silenciando")
        if self.sistema == "Windows":
            os.system("nircmd.exe mutesysvolume 1")
        elif self.sistema == "Linux":
            os.system("amixer -D pulse set Master mute")
        elif self.sistema == "Darwin":
            os.system("osascript -e 'set volume output muted true'")

    def bloquear_pc(self):
        """Bloqueia o computador"""
        self.falar("Bloqueando o computador")
        if self.sistema == "Windows":
            os.system("rundll32.exe user32.dll,LockWorkStation")
        elif self.sistema == "Linux":
            os.system("gnome-screensaver-command -l")
        elif self.sistema == "Darwin":
            os.system("/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession -suspend")

    def info_sistema(self):
        """Informa informações do sistema"""
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
        """Conta uma piada aleatória"""
        piadas = [
            "Por que o Python foi ao médico? Porque estava com problemas de sintaxe!",
            "Por que os programadores preferem o modo escuro? Porque a luz atrai bugs!",
            "O que o Java disse para o C? Você não tem classe!",
            "Por que o notebook foi ao psicólogo? Porque tinha muitos problemas internos!",
            "Qual é o cantor favorito dos programadores? Loop Fiasco!",
        ]
        self.falar(random.choice(piadas))

    def tocar_musica(self, termo: str | None = None):
        """Abre uma busca no Spotify pelo termo informado."""
        termo = (termo or "").strip()
        if not termo:
            self.falar("Qual música ou artista você quer ouvir?")
            resposta = self.ouvir()
            termo = (resposta or "").strip()

        if not termo:
            self.falar("Ok, não entendi o nome da música.")
            return

        self.falar(f"Colocando {termo} no Spotify")
        # Funciona mesmo sem o app instalado: abre no navegador.
        webbrowser.open(f"https://open.spotify.com/search/{termo}")

    def tocar_musica_aleatoria(self):
        """Compatibilidade: mantém o comando antigo abrindo uma busca genérica."""
        self.tocar_musica("música relaxante")

    def modo_produtivo(self):
        """Fecha redes sociais e abre ferramentas de produtividade"""
        self.falar(f"Ativando modo produtivo, {self.nome_usuario}")
        if self.sistema == "Windows":
            os.system("taskkill /F /IM chrome.exe /FI \"WINDOWTITLE eq *Facebook*\"")
            os.system("taskkill /F /IM chrome.exe /FI \"WINDOWTITLE eq *Instagram*\"")

    def tirar_screenshot(self):
        """Tira um screenshot da tela"""
        self.falar("Capturando a tela")
        if self.sistema == "Windows":
            os.system("snippingtool")
        elif self.sistema == "Linux":
            os.system("gnome-screenshot -i")
        elif self.sistema == "Darwin":
            os.system("screencapture -i ~/Desktop/screenshot.png")

    def limpar_tela(self):
        """Limpa o terminal"""
        os.system('cls' if self.sistema == "Windows" else 'clear')
        self.falar("Tela limpa")

    def abrir_calculadora(self):
        """Abre a calculadora"""
        self.falar("Abrindo calculadora")
        if self.sistema == "Windows":
            os.system("calc")
        elif self.sistema == "Linux":
            os.system("gnome-calculator &")
        elif self.sistema == "Darwin":
            os.system("open -a Calculator")

    def abrir_bloco_notas(self):
        """Abre o bloco de notas"""
        self.falar("Abrindo bloco de notas")
        if self.sistema == "Windows":
            os.system("notepad")
        elif self.sistema == "Linux":
            os.system("gedit &")
        elif self.sistema == "Darwin":
            os.system("open -a TextEdit")

    def abrir_gerenciador_tarefas(self):
        """Abre o gerenciador de tarefas"""
        self.falar("Abrindo gerenciador de tarefas")
        if self.sistema == "Windows":
            os.system("taskmgr")
        elif self.sistema == "Linux":
            os.system("gnome-system-monitor &")
        elif self.sistema == "Darwin":
            os.system("open -a 'Activity Monitor'")

    def abrir_previsao_tempo(self):
        """Abre previsão do tempo"""
        self.falar("Abrindo previsão do tempo")
        webbrowser.open("https://www.google.com/search?q=previsão+do+tempo")

    def abrir_noticias(self):
        """Abre portal de notícias"""
        self.falar("Abrindo notícias")
        webbrowser.open("https://news.google.com")

    def abrir_email(self):
        """Abre o email"""
        self.falar("Abrindo email")
        webbrowser.open("https://mail.google.com")

    def discord_silenciar(self):
        """Silencia/Desilencia o microfone no Discord (Ctrl+Shift+M)"""
        self.falar("Alternando microfone no Discord")
        keyboard = Controller()
        keyboard.press(Key.ctrl)
        keyboard.press(Key.shift)
        keyboard.press('m')
        keyboard.release('m')
        keyboard.release(Key.shift)
        keyboard.release(Key.ctrl)

    def discord_deafen(self):
        """Silencia/Desilencia o áudio no Discord (Ctrl+Shift+D)"""
        self.falar("Alternando áudio no Discord")
        keyboard = Controller()
        keyboard.press(Key.ctrl)
        keyboard.press(Key.shift)
        keyboard.press('d')
        keyboard.release('d')
        keyboard.release(Key.shift)
        keyboard.release(Key.ctrl)

    def discord_sair_chamada(self):
        """Desconecta da chamada no Discord (Ctrl+Shift+H)"""
        self.falar("Saindo da chamada no Discord")
        keyboard = Controller()
        keyboard.press(Key.ctrl)
        keyboard.press(Key.shift)
        keyboard.press('h')
        keyboard.release('h')
        keyboard.release(Key.shift)
        keyboard.release(Key.ctrl)

    def spotify_tocar_pausar(self):
        """Toca ou pausa a música no Spotify"""
        self.falar("Pausando musica")
        keyboard = Controller()
        keyboard.press(Key.media_play_pause)
        keyboard.release(Key.media_play_pause)

    def spotify_proxima(self):
        """Pula para a próxima música no Spotify"""
        self.falar("Próxima música")
        keyboard = Controller()
        keyboard.press(Key.media_next)
        keyboard.release(Key.media_next)

    def spotify_anterior(self):
        """Volta para a música anterior no Spotify"""
        self.falar("Música anterior")
        keyboard = Controller()
        keyboard.press(Key.media_previous)
        keyboard.release(Key.media_previous)

    def processar_comando(self, comando):
        """Processa o comando de voz recebido"""
        if not comando:
            return True

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
            periodo = self.obter_saudacao_periodo()
            saudacoes = [
                f"{periodo}! Como posso ajudá-lo?",
                f"{periodo}! Estou às suas ordens!",
                f"{periodo}! Pronto para atendê-lo!"
            ]
            self.falar(random.choice(saudacoes))

        elif "como você está" in comando or "tudo bem" in comando:
            self.falar(f"Estou funcionando perfeitamente, {self.nome_usuario}! Obrigado por perguntar!")

        elif "qual é o seu nome" in comando or "quem é você" in comando:
            self.falar(f"Sou seu assistente pessoal, criado para servir você, {self.nome_usuario}")

        elif "contar piada" in comando or "conte uma piada" in comando:
            self.contar_piada()

        elif "tocar música" in comando or "reproduzir música" in comando:
            termo = (
                comando.replace("tocar música", "")
                .replace("reproduzir música", "")
                .strip()
            )
            self.tocar_musica(termo)

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

        elif "discord silenciar" in comando or "discord mudo" in comando or "mutar discord" in comando:
            self.discord_silenciar()

        elif "discord deafen" in comando or "desligar áudio discord" in comando:
            self.discord_deafen()

        elif "sair da chamada" in comando or "desconectar discord" in comando or "sair chamada discord" in comando:
            self.discord_sair_chamada()

        elif "pausar música" in comando or "pausar spotify" in comando or "tocar música spotify" in comando:
            self.spotify_tocar_pausar()

        elif "próxima música" in comando or "próxima" in comando or "pular música" in comando:
            self.spotify_proxima()

        elif "música anterior" in comando or "anterior" in comando or "voltar música" in comando:
            self.spotify_anterior()

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
        """Mostra os comandos disponíveis"""
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
            "Discord: Silenciar / Deafen / Sair da chamada",
            "Spotify: Pausar / Próxima / Anterior",
            "Limpar tela",
            "Sair do assistente"
        ]

        print("\n📋 COMANDOS DISPONÍVEIS:")
        for cmd in comandos:
            print(f"  • {cmd}")

        self.falar("Mostrei os comandos disponíveis na tela.")

    def executar(self):
        """Loop principal do assistente"""
        saudacao = self.obter_saudacao_periodo()
        self.falar(f"{saudacao}! Assistente de voz iniciado e pronto para servi-lo. Diga 'ajuda' para ver os comandos disponíveis.")

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
    print("  pip install SpeechRecognition pyaudio psutil edge-tts pygame")
    print("\n💡 DICA: Fale de forma clara e pausada")
    print("="*60)

    try:
        assistente = AssistenteVoz()
        assistente.executar()
    except Exception as e:
        print(f"\n❌ Erro ao iniciar o assistente: {e}")
        print("\nVerifique se você instalou todas as dependências:")
        print("  pip install SpeechRecognition pyaudio psutil edge-tts pygame")
        sys.exit(1)


if __name__ == "__main__":
    main()
