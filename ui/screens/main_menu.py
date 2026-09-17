import math
from typing import List

import pygame

from core.managers.asset_manager import AssetManager
from core.managers.sound_player import SoundPlayer
from core.settings import Settings
from ui.visuals import COLORS, FloatingDecoration, draw_animated_text, get_font, make_background


class MainMenu:
    def __init__(self, games_list: List[dict]) -> None:
        self.background = make_background()
        self.games_list = list(games_list)
        self.title_font = get_font(42)
        self.card_title_font = get_font(24)
        self.card_subtitle_font = get_font(16)
        self.back_font = get_font(22)
        self.selected_index = 0
        self.page_start = 0
        self.message = None
        self.message_time = 0.0
        self.decorations = [FloatingDecoration() for _ in range(16)]
        self.nav_sound = self._load_sound("SOUND_NAV", "assets/sounds/nav_move.wav")
        self.select_sound = self._load_sound("SOUND_SELECT", "assets/sounds/select.wav")
        self.quit_sound = self._load_sound("SOUND_QUIT", "assets/sounds/quit.wav")

        card_width, card_height, gap = 230, 240, 34
        count = max(1, min(4, len(self.games_list)))
        total_width = card_width * count + gap * (count - 1)
        start_x = (Settings.S_WIDTH - total_width) // 2
        self.card_rects = [pygame.Rect(start_x + index * (card_width + gap), 250, card_width, card_height)
                           for index in range(count)]
        self.back_rect = pygame.Rect(35, 24, 150, 54)
        self.previous_button = self._prepare_navigation_button("previous_button", (70, 370))
        self.next_button = self._prepare_navigation_button("next_button", (Settings.S_WIDTH - 70, 370))

    def _prepare_navigation_button(self, asset_name, center):
        image = AssetManager.get_asset(asset_name)
        if image is None:
            return pygame.Rect(center[0] - 30, center[1] - 30, 60, 60)
        size = min(76, max(48, min(image.get_size())))
        scaled = pygame.transform.smoothscale(image, (size, size))
        return {"image": scaled, "rect": scaled.get_rect(center=center)}

    def _button_rect(self, button):
        return button["rect"] if isinstance(button, dict) else button

    def _change_page(self, direction):
        page_size = len(self.card_rects)
        page_start = max(0, self.page_start + direction * page_size)
        last_page_start = max(0, ((len(self.games_list) - 1) // page_size) * page_size) if self.games_list else 0
        self.page_start = min(page_start, last_page_start)
        self.selected_index = self.page_start

    def _load_sound(self, settings_key, default_path):
        path = getattr(Settings, settings_key, default_path)
        try:
            return pygame.mixer.Sound(path) if path else None
        except (pygame.error, FileNotFoundError):
            return None

    def _play_sound(self, sound):
        if sound:
            SoundPlayer.play_sound(sound)

    def _launch_selected(self):
        if not self.games_list:
            return None
        if self.games_list[self.selected_index].get("is_ghost"):
            self._play_sound(self.select_sound)
            return "TEST_GAME"
        self._play_sound(self.select_sound)
        return {"action": "LAUNCH", "game_data": self.games_list[self.selected_index]}

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_UP):
                    previous_index = self.selected_index
                    self.selected_index = max(0, self.selected_index - 1)
                    if self.selected_index != previous_index:
                        self._play_sound(self.nav_sound)
                elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
                    previous_index = self.selected_index
                    self.selected_index = min(max(0, len(self.games_list) - 1), self.selected_index + 1)
                    if self.selected_index != previous_index:
                        self._play_sound(self.nav_sound)
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    self.page_start = (self.selected_index // 4) * 4
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return self._launch_selected()
                elif event.key == pygame.K_ESCAPE:
                    self._play_sound(self.quit_sound)
                    return "QUIT"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.back_rect.collidepoint(event.pos):
                    self._play_sound(self.quit_sound)
                    return "START"
                if self._button_rect(self.previous_button).collidepoint(event.pos):
                    self._play_sound(self.nav_sound)
                    self._change_page(-1)
                    return None
                if self._button_rect(self.next_button).collidepoint(event.pos):
                    self._play_sound(self.nav_sound)
                    self._change_page(1)
                    return None
                for index, rect in enumerate(self.card_rects):
                    game_index = self.page_start + index
                    if rect.collidepoint(event.pos) and game_index < len(self.games_list):
                        self.selected_index = game_index
                        return self._launch_selected()
        return None

    def update(self, dt):
        for decoration in self.decorations:
            decoration.update(dt)
        if self.message_time > 0:
            self.message_time -= dt
            if self.message_time <= 0:
                self.message = None
        return None

    def _draw_card(self, screen, game, rect, index, selected, time):
        hover = rect.collidepoint(pygame.mouse.get_pos())
        offset = -6 if hover or selected else 0
        animated_rect = rect.move(0, offset + int(math.sin(time * 1.6 + index) * 2))
        pygame.draw.rect(screen, (210, 205, 225), animated_rect.move(0, 8), border_radius=24)
        pygame.draw.rect(screen, (255, 255, 255), animated_rect, border_radius=24)
        border = (255, 140, 130) if index % 3 == 0 else (98, 190, 200)
        pygame.draw.rect(screen, border, animated_rect, width=4, border_radius=24)
        cover = pygame.transform.smoothscale(AssetManager.get_cover(game.get("folder", "")), (150, 105))
        screen.blit(cover, cover.get_rect(center=(animated_rect.centerx, animated_rect.top + 68)))
        title = self.card_title_font.render(str(game.get("title", "Juego sin nombre"))[:18], True, COLORS["text"])
        screen.blit(title, title.get_rect(center=(animated_rect.centerx, animated_rect.top + 145)))
        group = self.card_subtitle_font.render(str(game.get("group_number", "Juego disponible"))[:24], True, (150, 145, 165))
        screen.blit(group, group.get_rect(center=(animated_rect.centerx, animated_rect.top + 178)))
        if selected:
            pygame.draw.circle(screen, COLORS["green"], (animated_rect.centerx, animated_rect.bottom - 24), 6)

    def draw(self, screen: pygame.Surface) -> None:
        time = pygame.time.get_ticks() / 1000.0
        selection_background = AssetManager.get_asset("selection_background")
        if selection_background:
            screen.blit(selection_background, (0, 0))
        else:
            screen.blit(self.background, (0, 0))
        for decoration in self.decorations:
            decoration.draw(screen, time)
        draw_animated_text(screen, "¿QUÉ QUIERES JUGAR?", self.title_font, (Settings.S_WIDTH // 2, 120), time, amplitude=5)
        for index, rect in enumerate(self.card_rects):
            game_index = self.page_start + index
            if game_index < len(self.games_list):
                self._draw_card(screen, self.games_list[game_index], rect, game_index, game_index == self.selected_index, time)
        self._draw_navigation_button(screen, self.previous_button, self.page_start > 0)
        self._draw_navigation_button(
            screen,
            self.next_button,
            self.page_start + len(self.card_rects) < len(self.games_list),
        )
        if not self.games_list:
            empty = get_font(26).render("Todavía no hay juegos disponibles", True, COLORS["muted"])
            screen.blit(empty, empty.get_rect(center=(Settings.S_WIDTH // 2, 350)))
        pygame.draw.rect(screen, COLORS["green_shadow"], self.back_rect.move(5, 5), border_radius=27)
        pygame.draw.rect(screen, COLORS["green"], self.back_rect, border_radius=27)
        label = self.back_font.render("← Volver", True, (255, 255, 255))
        screen.blit(label, label.get_rect(center=self.back_rect.center))
        if self.message:
            message = self.card_subtitle_font.render(self.message, True, (255, 255, 255))
            message_rect = message.get_rect(center=(Settings.S_WIDTH // 2, 575)).inflate(36, 22)
            pygame.draw.rect(screen, (108, 92, 160), message_rect, border_radius=16)
            screen.blit(message, message.get_rect(center=message_rect.center))

    def _draw_navigation_button(self, screen, button, enabled):
        rect = self._button_rect(button)
        if isinstance(button, dict):
            image = button["image"].copy()
            image.set_alpha(255 if enabled else 80)
            screen.blit(image, rect)
        else:
            pygame.draw.circle(screen, (210, 205, 225), rect.center, rect.width // 2)