import os
import random
import ctypes
import pygame
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.properties import NumericProperty

pygame.mixer.init()

Window.size = (380, 700)

COLOR_BG = get_color_from_hex("#0d0d0d")
COLOR_CARD = get_color_from_hex("#1a1a1a")
COLOR_PINK = get_color_from_hex("#ff2a6d")
COLOR_TEXT = get_color_from_hex("#f0f0f0")
COLOR_MUTED = get_color_from_hex("#777777")

Window.clearcolor = COLOR_BG

DOSSIER_APP = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
dossier_musiques = os.path.join(DOSSIER_APP, "musiques")


# Forcer l'icône sous Windows via l'API système
def forcer_icone_windows(dt):
    try:
        chemin_ico = os.path.join(DOSSIER_APP, "icon.ico")
        if os.path.exists(chemin_ico):
            hwnd = ctypes.windll.user32.FindWindowW(None, "OnzeMobile")
            if hwnd:
                hicon = ctypes.windll.user32.LoadImageW(None, chemin_ico, 1, 32, 32, 0x00000010 | 0x00008000)
                if hicon:
                    ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, hicon)
                    ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, hicon)
    except Exception:
        pass


def format_temps(secondes, est_playlist=False):
    sec = max(0, int(secondes))
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    
    if est_playlist and h > 0:
        return f"{h}h{m:02d}min"
    elif est_playlist:
        return f"{m}min"
    else:
        return f"{m:02d}:{s:02d}"


class CyberSlider(Widget):
    value = NumericProperty(0)
    min = NumericProperty(0)
    max = NumericProperty(100)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas, value=self.update_canvas)
        self.update_canvas()

    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.25, 0.25, 0.25, 1)
            track_y = self.y + self.height / 2 - 2
            Rectangle(pos=(self.x + 10, track_y), size=(self.width - 20, 4))
            
            if self.max > self.min:
                val_ratio = (self.value - self.min) / (self.max - self.min)
            else:
                val_ratio = 0
            active_width = (self.width - 20) * val_ratio
            Color(1, 0.16, 0.42, 1)
            Rectangle(pos=(self.x + 10, track_y), size=(active_width, 4))
            
            thumb_x = self.x + 10 + active_width - 10
            thumb_y = self.y + self.height / 2 - 10
            Color(1, 0.16, 0.42, 1)
            Ellipse(pos=(thumb_x, thumb_y), size=(20, 20))
            Color(0.05, 0.05, 0.05, 1)
            Ellipse(pos=(thumb_x + 6, thumb_y + 6), size=(8, 8))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._dragging = True
            self.update_value_from_touch(touch)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if getattr(self, '_dragging', False):
            self.update_value_from_touch(touch)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if getattr(self, '_dragging', False):
            self._dragging = False
            if hasattr(self, 'on_custom_touch_up'):
                self.on_custom_touch_up()
            return True
        return super().on_touch_up(touch)

    def update_value_from_touch(self, touch):
        local_x = touch.x - self.x - 10
        track_w = self.width - 20
        if track_w > 0:
            ratio = max(0.0, min(1.0, local_x / track_w))
            self.value = self.min + ratio * (self.max - self.min)


class EqualizerBars(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bars_count = 16
        Clock.schedule_interval(self.update_bars, 0.1)

    def update_bars(self, dt):
        self.canvas.clear()
        app = App.get_running_app()
        with self.canvas:
            Color(1, 0.16, 0.42, 1)
            total_width = self.width
            spacing = 4
            bar_width = (total_width - (self.bars_count * spacing)) / self.bars_count
            
            for i in range(self.bars_count):
                x = self.x + i * (bar_width + spacing)
                y = self.y
                if app.is_playing:
                    h = random.randint(6, int(self.height * 0.9))
                else:
                    h = 3
                Rectangle(pos=(x, y), size=(bar_width, h))


class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=25, spacing=15)
        
        # Intégration de ton image à la place du dessin (mets ton nom de fichier image, ex: logo.png)
        logo_layout = BoxLayout(size_hint=(1, 0.22))
        chemin_image_logo = os.path.join(DOSSIER_APP, "logo.png")  # Modifie "logo.png" par ton fichier image si besoin
        if os.path.exists(chemin_image_logo):
            img_logo = Image(source=chemin_image_logo, keep_ratio=True)
        else:
            # Fallback par défaut si l'image n'est pas trouvée
            img_logo = Image(source="icon.ico", keep_ratio=True)
        logo_layout.add_widget(img_logo)
        layout.add_widget(logo_layout)
        
        lbl_titre = Label(
            text="OnzeMobile", font_size=32, bold=True,
            color=COLOR_PINK, size_hint=(1, 0.08), halign="center"
        )
        lbl_titre.bind(size=lbl_titre.setter('text_size'))
        layout.add_widget(lbl_titre)
        
        lbl_sous_titre = Label(
            text="Lecteur audio mobile", font_size=12, bold=True,
            color=COLOR_MUTED, size_hint=(1, 0.05), halign="center"
        )
        lbl_sous_titre.bind(size=lbl_sous_titre.setter('text_size'))
        layout.add_widget(lbl_sous_titre)
        
        desc_card = BoxLayout(
            orientation='vertical', padding=14, spacing=6,
            size_hint=(1, 0.32)
        )
        with desc_card.canvas.before:
            Color(rgba=COLOR_CARD)
            self.rect_card = Rectangle(pos=desc_card.pos, size=desc_card.size)
        desc_card.bind(pos=lambda inst, val: setattr(self.rect_card, 'pos', val),
                       size=lambda inst, val: setattr(self.rect_card, 'size', val))
        
        lbl_card_title = Label(
            text="Comment ça marche ?", font_size=12, bold=True,
            color=COLOR_PINK, size_hint=(1, 0.25), halign="center"
        )
        lbl_card_title.bind(size=lbl_card_title.setter('text_size'))
        desc_card.add_widget(lbl_card_title)
        
        texte_aide_accueil = (
            "• Fichiers .mp3 détectés automatiquement.\n"
            "• Touchez un titre pour le lancer.\n"
            "• Bouton DOSSIER pour changer de répertoire.\n"
            "• Fait partie de l'écosystème OnzeMusique\n"
            "  (avec OnzeHeure et OnzePinguin)."
        )
        lbl_pub_desc = Label(
            text=texte_aide_accueil, font_size=11, color=COLOR_TEXT,
            halign="left", valign="middle", size_hint=(1, 0.75)
        )
        lbl_pub_desc.bind(size=lbl_pub_desc.setter('text_size'))
        desc_card.add_widget(lbl_pub_desc)
        
        layout.add_widget(desc_card)
        
        btn_lancer = Button(
            text="LANCER LE LECTEUR ▸", font_size=13, bold=True,
            background_normal='', background_color=COLOR_PINK,
            color=get_color_from_hex("#000000"), size_hint=(1, 0.12)
        )
        btn_lancer.bind(on_press=lambda x: setattr(self.manager, 'current', 'player'))
        layout.add_widget(btn_lancer)
        
        lbl_version = Label(
            text="v4.5", font_size=9, color=COLOR_MUTED,
            size_hint=(1, 0.05), halign="center"
        )
        lbl_version.bind(size=lbl_version.setter('text_size'))
        layout.add_widget(lbl_version)
        
        self.add_widget(layout)


class PlayerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_dragging = False
        self.playlist_buttons = []
        
        layout = BoxLayout(orientation='vertical', padding=8, spacing=4)
        
        header = BoxLayout(size_hint=(1, 0.045), spacing=5)
        self.lbl_dossier = Label(text="MUSIQUES • 0 titres • 00:00", font_size=10, bold=True, color=COLOR_PINK, halign="left")
        self.lbl_dossier.bind(size=self.lbl_dossier.setter('text_size'))
        header.add_widget(self.lbl_dossier)
        
        btn_dossier = Button(text="DOSSIER", font_size=9, bold=True, background_normal='', background_color=COLOR_CARD, color=COLOR_PINK, size_hint_x=0.22)
        btn_dossier.bind(on_press=self.changer_dossier_popup)
        header.add_widget(btn_dossier)
        
        btn_aide = Button(text="AIDE", font_size=9, bold=True, background_normal='', background_color=COLOR_CARD, color=COLOR_PINK, size_hint_x=0.18)
        btn_aide.bind(on_press=self.afficher_aide)
        header.add_widget(btn_aide)
        layout.add_widget(header)
        
        self.lbl_titre = Label(text="Aucune chanson chargée", font_size=11, bold=True, color=COLOR_TEXT, size_hint=(1, 0.045), halign="center")
        self.lbl_titre.bind(size=self.lbl_titre.setter('text_size'))
        layout.add_widget(self.lbl_titre)
        
        self.equalizer = EqualizerBars(size_hint=(1, 0.055))
        layout.add_widget(self.equalizer)
        
        prog_container = BoxLayout(orientation='horizontal', size_hint=(1, 0.04), spacing=4)
        self.lbl_temps_courant = Label(text="00:00", font_size=9, bold=True, color=COLOR_PINK, size_hint_x=0.15)
        
        self.progress_slider = CyberSlider(min=0, max=100, value=0, size_hint_x=0.7)
        self.progress_slider.bind(on_touch_down=self.debut_seek, on_custom_touch_up=self.fin_seek)
        
        self.lbl_temps_total = Label(text="00:00", font_size=9, bold=True, color=COLOR_MUTED, size_hint_x=0.15)
        
        prog_container.add_widget(self.lbl_temps_courant)
        prog_container.add_widget(self.progress_slider)
        prog_container.add_widget(self.lbl_temps_total)
        layout.add_widget(prog_container)
        
        self.scroll = ScrollView(size_hint=(1, 0.62))
        self.playlist_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=3)
        self.playlist_layout.bind(minimum_height=self.playlist_layout.setter('height'))
        self.scroll.add_widget(self.playlist_layout)
        layout.add_widget(self.scroll)
        
        vol_layout = BoxLayout(size_hint=(1, 0.045), spacing=5)
        vol_layout.add_widget(Label(text="VOL", font_size=9, bold=True, color=COLOR_PINK, size_hint_x=0.15))
        self.volume_slider = CyberSlider(min=0, max=1, value=0.1, size_hint_x=0.85)
        self.volume_slider.bind(value=self.changer_volume)
        vol_layout.add_widget(self.volume_slider)
        layout.add_widget(vol_layout)
        
        controls = BoxLayout(size_hint=(1, 0.09), spacing=4)
        
        self.btn_prev = Button(text="PREC", font_size=10, bold=True, background_normal='', background_color=COLOR_CARD, color=COLOR_TEXT, size_hint_x=0.22)
        self.btn_prev.bind(on_press=self.action_precedent)
        controls.add_widget(self.btn_prev)
        
        self.btn_play = Button(text="JOUER", font_size=10, bold=True, background_normal='', background_color=COLOR_PINK, color=get_color_from_hex("#000000"), size_hint_x=0.28)
        self.btn_play.bind(on_press=self.toggle_play)
        controls.add_widget(self.btn_play)
        
        self.btn_next = Button(text="SUIV", font_size=10, bold=True, background_normal='', background_color=COLOR_CARD, color=COLOR_TEXT, size_hint_x=0.22)
        self.btn_next.bind(on_press=self.action_suivant)
        controls.add_widget(self.btn_next)
        
        self.btn_shuffle = Button(text="ALEATOIRE", font_size=8, bold=True, background_normal='', background_color=COLOR_CARD, color=COLOR_PINK, size_hint_x=0.28)
        self.btn_shuffle.bind(on_press=self.toggle_shuffle)
        controls.add_widget(self.btn_shuffle)
        
        layout.add_widget(controls)
        self.add_widget(layout)
        
        Clock.schedule_interval(self.mettre_a_jour_progression, 0.2)

    def on_enter(self):
        App.get_running_app().peupler_playlist()
        pygame.mixer.music.set_volume(self.volume_slider.value)
        Clock.schedule_once(forcer_icone_windows, 0.3)

    def changer_volume(self, instance, value):
        pygame.mixer.music.set_volume(value)

    def changer_dossier_popup(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        filechooser = FileChooserListView(path=DOSSIER_APP, dirselect=True)
        content.add_widget(filechooser)
        
        btn_layout = BoxLayout(size_hint=(1, 0.15), spacing=10)
        btn_valider = Button(text="VALIDER", font_size=11, bold=True, background_normal='', background_color=COLOR_PINK, color=get_color_from_hex("#000000"))
        btn_annuler = Button(text="ANNULER", font_size=11, bold=True, background_normal='', background_color=COLOR_CARD, color=COLOR_TEXT)
        
        btn_layout.add_widget(btn_valider)
        btn_layout.add_widget(btn_annuler)
        content.add_widget(btn_layout)
        
        popup = Popup(title="Sélectionner un dossier de musiques", content=content, size_hint=(0.9, 0.8), auto_dismiss=True)
        
        def valider_selection(btn):
            selection = filechooser.selection
            if selection and os.path.isdir(selection[0]):
                global dossier_musiques
                dossier_musiques = selection[0]
                App.get_running_app().peupler_playlist()
            popup.dismiss()

        btn_valider.bind(on_press=valider_selection)
        btn_annuler.bind(on_press=popup.dismiss)
        popup.open()

    def surligner_morceau_actif(self, index):
        for idx, btn in enumerate(self.playlist_buttons):
            if idx == index:
                btn.background_color = COLOR_PINK
                btn.color = get_color_from_hex("#000000")
                self.scroll.scroll_to(btn)
            else:
                btn.background_color = COLOR_CARD
                btn.color = COLOR_TEXT

    def debut_seek(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.is_dragging = True

    def fin_seek(self):
        self.is_dragging = False
        app = App.get_running_app()
        if app.current_duration > 0:
            pourcentage = self.progress_slider.value / 100.0
            nouvelle_position = pourcentage * app.current_duration
            app.playback_position = nouvelle_position
            if app.is_playing:
                pygame.mixer.music.play(start=nouvelle_position)

    def mettre_a_jour_progression(self, dt):
        app = App.get_running_app()
        if app.is_playing and not self.is_dragging:
            if app.current_duration > 0:
                app.playback_position += dt
                if app.playback_position >= app.current_duration:
                    app.changer_musique(1)
                    return
                self.progress_slider.value = (app.playback_position / app.current_duration) * 100
                self.lbl_temps_courant.text = format_temps(app.playback_position)

    def action_precedent(self, instance):
        self.btn_prev.background_color = COLOR_PINK
        self.btn_prev.color = get_color_from_hex("#000000")
        Clock.schedule_once(lambda dt: self.reset_couleur_btn(self.btn_prev, COLOR_CARD, COLOR_TEXT), 0.2)
        App.get_running_app().changer_musique(-1)

    def action_suivant(self, instance):
        self.btn_next.background_color = COLOR_PINK
        self.btn_next.color = get_color_from_hex("#000000")
        Clock.schedule_once(lambda dt: self.reset_couleur_btn(self.btn_next, COLOR_CARD, COLOR_TEXT), 0.2)
        App.get_running_app().changer_musique(1)

    def reset_couleur_btn(self, bouton, bg_color, text_color):
        bouton.background_color = bg_color
        bouton.color = text_color

    def toggle_shuffle(self, instance):
        app = App.get_running_app()
        app.mode_aleatoire = not getattr(app, 'mode_aleatoire', False)
        if app.mode_aleatoire:
            self.btn_shuffle.background_color = COLOR_PINK
            self.btn_shuffle.color = get_color_from_hex("#000000")
        else:
            self.btn_shuffle.background_color = COLOR_CARD
            self.btn_shuffle.color = COLOR_PINK

    def afficher_aide(self, instance):
        content = BoxLayout(orientation='vertical', padding=18, spacing=12)
        lbl_titre_aide = Label(text="Besoin d'aide ?", font_size=18, bold=True, color=COLOR_PINK, size_hint=(1, 0.12), halign="center")
        lbl_titre_aide.bind(size=lbl_titre_aide.setter('text_size'))
        content.add_widget(lbl_titre_aide)
        
        texte_aide = (
            "OnzeMobile fait partie de l'écosystème OnzeMusique (avec OnzeHeure et OnzePinguin).\n\n"
            "Comment profiter de votre application mobile ?\n\n"
            "1. Format requis : Vos fichiers audio doivent être au format .mp3.\n\n"
            "2. Changer de dossier : Appuyez sur le bouton 'DOSSIER' en haut pour cibler vos propres musiques.\n\n"
            "3. Navigation tactile : Touchez un morceau pour le lancer directement."
        )
        lbl_desc = Label(text=texte_aide, font_size=11, color=COLOR_TEXT, halign="left", valign="top", size_hint=(1, 0.7))
        lbl_desc.bind(size=lbl_desc.setter('text_size'))
        content.add_widget(lbl_desc)
        
        btn_fermer = Button(text="COMPRIS", font_size=13, bold=True, background_normal='', background_color=COLOR_PINK, color=get_color_from_hex("#000000"), size_hint=(1, 0.18))
        popup = Popup(title="Aide - OnzeMobile", content=content, size_hint=(0.9, 0.75), auto_dismiss=True)
        btn_fermer.bind(on_press=popup.dismiss)
        content.add_widget(btn_fermer)
        popup.open()

    def toggle_play(self, instance):
        app = App.get_running_app()
        if app.playlist_fichiers:
            if app.is_playing:
                pygame.mixer.music.pause()
                app.is_playing = False
                self.btn_play.text = "JOUER"
            else:
                if app.playback_position > 0:
                    pygame.mixer.music.unpause()
                else:
                    app.charger_et_jouer(app.currentIndex)
                app.is_playing = True
                self.btn_play.text = "PAUSE"


class OnzeMobileApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.playlist_fichiers = []
        self.currentIndex = 0
        self.mode_aleatoire = False
        self.playback_position = 0.0
        self.current_duration = 0.0
        self.is_playing = False

    def build(self):
        self.title = "OnzeMobile"
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(PlayerScreen(name='player'))
        return sm

    def peupler_playlist(self):
        self.playlist_fichiers = []
        player_screen = self.root.get_screen('player')
        player_screen.playlist_layout.clear_widgets()
        player_screen.playlist_buttons = []
        
        if os.path.exists(dossier_musiques):
            fichiers = sorted(f for f in os.listdir(dossier_musiques) if f.endswith('.mp3'))
            self.playlist_fichiers = fichiers
            total_seconds = sum(pygame.mixer.Sound(os.path.join(dossier_musiques, f)).get_length() for f in fichiers if f.endswith('.mp3'))
            
            temps_total_str = format_temps(total_seconds, est_playlist=True)
            player_screen.lbl_dossier.text = f"MUSIQUES • {len(fichiers)} titres • {temps_total_str}"
            
            for idx, nom_fichier in enumerate(fichiers):
                btn = Button(
                    text=nom_fichier, size_hint_y=None, height=36, font_size=11, bold=True,
                    background_normal='', background_color=COLOR_CARD, color=COLOR_TEXT,
                    halign='left', valign='middle', text_size=(Window.size[0] - 40, None)
                )
                btn.bind(on_press=lambda instance, i=idx: self.charger_et_jouer(i))
                player_screen.playlist_layout.add_widget(btn)
                player_screen.playlist_buttons.append(btn)

    def charger_et_jouer(self, index):
        if 0 <= index < len(self.playlist_fichiers):
            self.currentIndex = index
            nom_fichier = self.playlist_fichiers[index]
            chemin_complet = os.path.join(dossier_musiques, nom_fichier)
            try:
                sound_obj = pygame.mixer.Sound(chemin_complet)
                self.current_duration = sound_obj.get_length()
            except Exception:
                self.current_duration = 180.0
                
            pygame.mixer.music.load(chemin_complet)
            pygame.mixer.music.play()
            
            player_screen = self.root.get_screen('player')
            pygame.mixer.music.set_volume(player_screen.volume_slider.value)
            
            self.playback_position = 0.0
            self.is_playing = True
            player_screen.lbl_titre.text = nom_fichier
            player_screen.btn_play.text = "PAUSE"
            player_screen.progress_slider.value = 0
            player_screen.lbl_temps_total.text = format_temps(self.current_duration)
            player_screen.surligner_morceau_actif(index)

    def changer_musique(self, direction):
        if not self.playlist_fichiers:
            return
        if self.mode_aleatoire:
            self.currentIndex = random.randint(0, len(self.playlist_fichiers) - 1)
        else:
            self.currentIndex = (self.currentIndex + direction) % len(self.playlist_fichiers)
        self.charger_et_jouer(self.currentIndex)

if __name__ == '__main__':
    OnzeMobileApp().run()