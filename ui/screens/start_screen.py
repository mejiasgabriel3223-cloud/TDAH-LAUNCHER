import os
import pygame

from core.managers.asset_manager import AssetManager
from core.managers.sound_player import SoundPlayer
from core.settings import Settings


def _get_font(size: int) -> pygame.font.Font:
    if hasattr(AssetManager, "get_font"):
        return AssetManager.get_font(size)
    return pygame.font.Font(None, size)


class StartScreen:
    def __init__(self) -> None:
        self.font_title = pygame.font.Font(None, 64)
        self.font_text = _get_font(32)
        
        # Variables de parpadeo del texto
        self.alfa = 0
        self.velocidad = 8
        self.aumentando = True
        self.ejecutando = True

        # Variables para la transición (Fade to black)
        self.transicionando = False
        self.fade_alpha = 0
        self.fade_speed = 10  # Controla qué tan rápido se oscurece la pantalla
        
        # Superficie negra reutilizable para la transición
        self.fade_surface = pygame.Surface((Settings.S_WIDTH, Settings.S_HEIGHT))
        self.fade_surface.fill((0, 0, 0))

        # Cargar efecto de sonido al presionar ENTER
        self.start_sound = self._load_sound("SOUND_SELECT", os.path.join("assets", "sounds", "start.wav"))

    def _load_sound(self, settings_key: str, default_path: str) -> pygame.mixer.Sound | None:
        """Carga un efecto de sonido de forma segura."""
        path = getattr(Settings, settings_key, default_path)
        if path and os.path.exists(path):
            try:
                return pygame.mixer.Sound(path)
            except Exception:
                return None
        return None

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if not self.transicionando:
                    self.transicionando = True
                    self.velocidad = 60  # Aumenta drásticamente la velocidad del parpadeo
                    
                    if self.start_sound:
                        SoundPlayer.play_sound(self.start_sound)
                        
        # No cambiamos de pantalla aquí directamente, dejamos que update() maneje la animación
        return None

    def update(self, dt):
        # 1. Animación de parpadeo del texto
        if self.aumentando:
            self.alfa += self.velocidad
            if self.alfa >= 255:
                self.alfa = 255
                self.aumentando = False
        else:
            self.alfa -= self.velocidad
            if self.alfa <= 0:
                self.alfa = 0
                self.aumentando = True

        # 2. Control de la transición a negro
        if self.transicionando:
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                return "MAIN_MENU"  # Cambia al menú principal cuando la pantalla está totalmente negra

        return None

    def draw(self, screen: pygame.Surface) -> None:
        # Dibujar imagen de fondo o color por defecto
        if os.path.exists(Settings.MAIN_TITLE_IMAGE):
            try:
                bg = pygame.image.load(Settings.MAIN_TITLE_IMAGE)
                try:
                    bg = bg.convert_alpha()
                except pygame.error:
                    pass
                bg_scaled = pygame.transform.smoothscale(bg, (Settings.S_WIDTH, Settings.S_HEIGHT))
                screen.blit(bg_scaled, (0, 0))
            except Exception:
                screen.fill(Settings.BACKGROUND_COLOR)
        else:
            screen.fill(Settings.BACKGROUND_COLOR)

        # Dibujar texto parpadeante
        subtitle = _get_font(32).render("Presiona ENTER para inicializar el launcher", True, Settings.TEXT_COLOR)
        texto_copia = subtitle.copy()
        texto_copia.set_alpha(self.alfa)
        screen.blit(texto_copia, (Settings.S_WIDTH // 2 - subtitle.get_width() // 2, 500))

        # Dibujar la capa de difuminado a negro si la transición está activa
        if self.fade_alpha > 0:
            self.fade_surface.set_alpha(self.fade_alpha)
            screen.blit(self.fade_surface, (0, 0))