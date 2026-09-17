import pygame

from core.managers.sound_player import SoundPlayer
from core.settings import Settings
from core.managers.asset_manager import AssetManager
from ui.visuals import COLORS, FloatingDecoration, get_font, make_background


class StartScreen:
    def __init__(self) -> None:
        self.background = make_background()
        self.subtitle_font = get_font(32)
        self.tagline_font = get_font(22)
        self.button_font = get_font(30)
        self.button_rect = pygame.Rect(0, 0, 300, 84)
        self.button_rect.center = (Settings.S_WIDTH // 2, 470)
        self.decorations = [FloatingDecoration() for _ in range(16)]
        self.start_sound = self._load_sound("SOUND_START", "assets/sounds/start.wav")

    def _load_sound(self, settings_key, default_path):
        path = getattr(Settings, settings_key, default_path)
        try:
            return pygame.mixer.Sound(path) if path else None
        except (pygame.error, FileNotFoundError):
            return None

    def _play_sound(self, sound):
        SoundPlayer.play_sound(sound)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._play_sound(self.start_sound)
                return "MAIN_MENU"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.button_rect.collidepoint(event.pos):
                self._play_sound(self.start_sound)
                return "MAIN_MENU"
        return None

    def update(self, dt):
        for decoration in self.decorations:
            decoration.update(dt)
        return None

    def draw(self, screen: pygame.Surface) -> None:
        time = pygame.time.get_ticks() / 1000.0
        start_background = AssetManager.get_asset("start_background")
        screen.blit(start_background if start_background else self.background, (0, 0))
        for decoration in self.decorations:
            decoration.draw(screen, time)
        banner = AssetManager.get_asset("banner")
        if banner:
            screen.blit(banner, banner.get_rect(center=(Settings.S_WIDTH // 2, 220)))
        tagline = self.tagline_font.render("¡vamos a jugar y a divertirnos!", True, (120, 108, 150))
        screen.blit(tagline, tagline.get_rect(center=(Settings.S_WIDTH // 2, 360)))

        hover = self.button_rect.collidepoint(pygame.mouse.get_pos())
        rect = self.button_rect.inflate(10 if hover else 0, 6 if hover else 0)
        pygame.draw.rect(screen, COLORS["green_shadow"], rect.move(7, 7), border_radius=rect.height // 2)
        pygame.draw.rect(screen, COLORS["green_hover"] if hover else COLORS["green"], rect, border_radius=rect.height // 2)
        label = self.button_font.render("¡EMPEZAR!", True, (255, 255, 255))
        screen.blit(label, label.get_rect(center=rect.center))
