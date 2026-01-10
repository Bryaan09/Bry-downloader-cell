import os
import threading
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFillRoundFlatIconButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.toast import toast
from kivy.utils import platform
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
import yt_dlp

# Ajuste visual apenas para PC
if platform != 'android':
    Window.size = (360, 680)

# Bloco de compatibilidade Android
if platform == 'android':
    from android.storage import primary_external_storage_path
    from android.permissions import request_permissions, Permission
else:
    def primary_external_storage_path(): return ""
    def request_permissions(x): pass
    Permission = None

# Logger silencioso para evitar erros de compatibilidade


class MyLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): print(f"LOG: {msg}")


class BryDownloadApp(MDApp):
    stop_download_flag = False
    save_path = ""

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Red"

        self.definir_caminho()

        screen = MDScreen()
        main_layout = MDBoxLayout(orientation='vertical')

        # Barra Superior
        toolbar = MDTopAppBar(title="Bry Download Pro", elevation=4)
        main_layout.add_widget(toolbar)

        # Layout Central
        content = MDBoxLayout(orientation='vertical', padding=20, spacing=15,
                              pos_hint={"center_x": 0.5, "center_y": 0.5}, adaptive_height=True)

        # Cartão Principal
        card = MDCard(orientation='vertical', padding=20, spacing=15,
                      size_hint=(1, None), adaptive_height=True, radius=[20, 20, 20, 20], elevation=3)

        # Conteúdo do Cartão
        lbl = MDLabel(text="Cole o link do Vídeo/Playlist:",
                      halign="center", theme_text_color="Secondary")

        # Input + Colar
        box_input = MDBoxLayout(orientation='horizontal',
                                spacing=5, adaptive_height=True)
        self.input_url = MDTextField(
            hint_text="https://...", mode="fill", size_hint_x=0.85)
        btn_paste = MDIconButton(
            icon="content-paste", on_release=self.colar, size_hint_x=0.15, pos_hint={"center_y": 0.6})
        box_input.add_widget(self.input_url)
        box_input.add_widget(btn_paste)

        # Botões
        self.btn_vid = MDFillRoundFlatIconButton(text="BAIXAR VÍDEO (MP4)", icon="video",
                                                 pos_hint={"center_x": 0.5}, size_hint_x=1, on_release=lambda x: self.start('video'))
        self.btn_aud = MDFillRoundFlatIconButton(text="BAIXAR ÁUDIO (M4A)", icon="music",
                                                 pos_hint={"center_x": 0.5}, size_hint_x=1, md_bg_color=(0.1, 0.7, 0.5, 1), on_release=lambda x: self.start('audio'))

        # Status e Cancelar
        self.lbl_status = MDLabel(
            text="Pronto para baixar", halign="center", font_style="Caption", theme_text_color="Hint")
        self.btn_cancel = MDFillRoundFlatIconButton(text="CANCELAR", icon="close-circle", pos_hint={"center_x": 0.5},
                                                    md_bg_color=(0.8, 0.1, 0.1, 1), disabled=True, opacity=0, on_release=self.cancelar)

        # Caminho (Rodapé)
        lbl_path = MDLabel(text=f"Salva em: {self.get_path_visual()}",
                           halign="center", font_style="Overline", opacity=0.6)

        card.add_widget(lbl)
        card.add_widget(box_input)
        card.add_widget(self.btn_vid)
        card.add_widget(self.btn_aud)
        card.add_widget(self.lbl_status)
        card.add_widget(self.btn_cancel)
        card.add_widget(lbl_path)

        content.add_widget(card)
        main_layout.add_widget(MDBoxLayout())
        main_layout.add_widget(content)
        main_layout.add_widget(MDBoxLayout())

        screen.add_widget(main_layout)
        return screen

    def on_start(self):
        if platform == 'android':
            request_permissions(
                [Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

    def definir_caminho(self):
        if platform == 'android':
            self.save_path = os.path.join(
                primary_external_storage_path(), 'Download')
        else:
            self.save_path = os.path.join(os.getcwd(), 'downloads_bry')
            os.makedirs(self.save_path, exist_ok=True)

    def get_path_visual(self):
        return "Pasta Downloads" if platform == 'android' else "Pasta do Projeto"

    def colar(self, instance):
        try:
            self.input_url.text = Clipboard.paste()
        except:
            pass

    def start(self, tipo):
        if not self.input_url.text:
            return toast("Link vazio")
        self.stop_download_flag = False
        self.toggle(True)
        threading.Thread(target=self.download, args=(
            self.input_url.text, tipo)).start()

    def cancelar(self, x):
        self.stop_download_flag = True
        self.lbl_status.text = "Cancelando..."

    def toggle(self, downloading):
        self.btn_vid.disabled = self.btn_aud.disabled = downloading
        self.btn_cancel.disabled = not downloading
        self.btn_cancel.opacity = 1 if downloading else 0

    def download(self, url, tipo):
        Clock.schedule_once(lambda x: setattr(
            self.lbl_status, 'text', "Conectando..."))

        def hook(d):
            if self.stop_download_flag:
                raise Exception("CANCEL")
            if d['status'] == 'downloading':
                try:
                    p = d.get('_percent_str', '0%').replace('%', '')
                    Clock.schedule_once(lambda x: setattr(
                        self.lbl_status, 'text', f"Baixando: {p}%"))
                except:
                    pass

        opts = {
            'outtmpl': {'default': f'{self.save_path}/%(title)s.%(ext)s', 'pl_thumbnail': f'{self.save_path}/%(playlist)s/%(title)s.%(ext)s'},
            'logger': MyLogger(),
            'ignoreerrors': True, 'nocheckcertificate': True, 'quiet': True, 'noplaylist': False,
            'progress_hooks': [hook],
            'format': 'bestaudio[ext=m4a]/bestaudio/best' if tipo == 'audio' else 'best[ext=mp4]/best'
        }

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                Clock.schedule_once(lambda x: setattr(
                    self.lbl_status, 'text', "Processando..."))
                if self.stop_download_flag:
                    raise Exception("CANCEL")
                ydl.download([url])
            if not self.stop_download_flag:
                Clock.schedule_once(lambda x: setattr(
                    self.lbl_status, 'text', "Sucesso!"))
                toast("Concluído!")
        except Exception as e:
            msg = "Cancelado" if "CANCEL" in str(e) else "Erro no Download"
            Clock.schedule_once(lambda x: setattr(
                self.lbl_status, 'text', msg))
        finally:
            Clock.schedule_once(lambda x: self.toggle(False))


if __name__ == '__main__':
    BryDownloadApp().run()
