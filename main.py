#!/usr/bin/env python3
"""
Assistente de Voz para Controle do Computador
Requer: pip install speechrecognition pyttsx3 pyaudio
"""

import speech_recognition as sr
import pyttsx3
import os
import sys
import subprocess
import platform

class AssistenteVoz:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        self.engine = pyttsx3.init()
        self.configurar_voz()

        self.sistema = platform.system()
        self.apps = self.configurar_apps()

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

        elif "olá" in comando or "oi" in comando:
            self.falar("Olá! Como posso ajudar você?")

        elif "como você está" in comando or "tudo bem" in comando:
            self.falar("Estou funcionando perfeitamente, obrigado por perguntar!")

        elif "ajuda" in comando or "comandos" in comando:
            self.mostrar_ajuda()

        elif "sair" in comando or "encerrar" in comando or "tchau" in comando:
            self.falar("Encerrando o assistente. Até logo!")
            return False

        else:
            self.falar("Desculpe, não entendi o comando.")

        return True

    def mostrar_ajuda(self):
        comandos = [
            "Desligar o computador",
            "Reiniciar o computador",
            "Cancelar desligamento",
            "Abrir aplicativos: " + ", ".join(self.apps.keys()),
            "Sair do assistente"
        ]

        print("\n📋 COMANDOS DISPONÍVEIS:")
        for cmd in comandos:
            print(f"  • {cmd}")

        self.falar("Mostrei os comandos disponíveis na tela.")

    def executar(self):
        self.falar("Assistente de voz iniciado. Diga 'ajuda' para ver os comandos disponíveis.")

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
