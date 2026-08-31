import os
import pygame
from typing import List

from core.managers.asset_manager import AssetManager
from core.managers.sound_player import SoundPlayer
from core.settings import Settings


def _get_font(size: int) -> pygame.font.Font:
    if hasattr(AssetManager, "get_font"):
        return AssetManager.get_font(size)
    return pygame.font.Font(None, size)


class MainMenu:
    def __init__(self, games_list: List[dict]) -> None:
        # Capa de entrada progresiva (Fade In)
        self.fade_alpha = 255  # Comienza totalmente opaco/negro
        self.fade_speed = 8    # Velocidad de desvanecimiento de la sombra negra
        self.fade_surface = pygame.Surface((Settings.S_WIDTH, Settings.S_HEIGHT))
        self.fade_surface.fill((0, 0, 0))
        self.games_list = list(games_list)
        self.selected_index = 0
        self.quit_button_rect = pygame.Rect(Settings.S_WIDTH - 140, 20, 120, 40)
        self.menu_top = 120
        self.row_height = 60
        self.visible_rows = max(1, (Settings.S_HEIGHT - 260) // self.row_height)
        self.scroll_offset = 0

        # Control de desplazamiento para el panel de detalles
        self.details_scroll_offset = 0
        self.max_details_scroll = 0

        # Cargar sonidos de la interfaz
        self.move_sound = self._load_sound("SOUND_MOVE", os.path.join("assets", "sounds", "nav_move.wav"))
        self.select_sound = self._load_sound("SOUND_SELECT", os.path.join("assets", "sounds", "select.wav"))
        self.quit_sound = self._load_sound("SOUND_QUIT", os.path.join("assets", "sounds", "quit.wav"))

    def _load_sound(self, settings_key: str, default_path: str) -> pygame.mixer.Sound | None:
        """Carga un archivo de sonido desde Settings o una ruta por defecto."""
        path = getattr(Settings, settings_key, default_path)
        if path and os.path.exists(path):
            try:
                return pygame.mixer.Sound(path)
            except Exception:
                return None
        return None

    def _play_sound(self, sound: pygame.mixer.Sound | None) -> None:
        """Envía el efecto de sonido a SoundPlayer si existe."""
        if sound:
            SoundPlayer.play_sound(sound)

    def _render_multiline(self, screen, text, font, color, x, y, max_width, line_height):
        paragraphs = str(text).split('\n')
        for paragraph in paragraphs:
            words = paragraph.split(' ')
            line = ""
            for word in words:
                if not word: 
                    continue
                test_line = (line + " " + word).strip()
                if font.size(test_line)[0] <= max_width:
                    line = test_line
                else:
                    screen.blit(font.render(line, True, color), (x, y))
                    y += line_height
                    line = word
            if line:
                screen.blit(font.render(line, True, color), (x, y))
                y += line_height
        return y

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    prev_index = self.selected_index
                    self.selected_index = max(0, self.selected_index - 1)
                    
                    if prev_index != self.selected_index:
                        self.details_scroll_offset = 0
                        self._play_sound(self.move_sound)  # Sonido de navegación

                    self._ensure_selection_visible()

                elif event.key == pygame.K_DOWN:
                    prev_index = self.selected_index
                    self.selected_index = min(len(self.games_list) - 1, self.selected_index + 1)
                    
                    if prev_index != self.selected_index:
                        self.details_scroll_offset = 0
                        self._play_sound(self.move_sound)  # Sonido de navegación

                    self._ensure_selection_visible()

                elif event.key == pygame.K_PAGEUP:
                    self.details_scroll_offset = max(0, self.details_scroll_offset - 40)

                elif event.key == pygame.K_PAGEDOWN:
                    self.details_scroll_offset = min(self.max_details_scroll, self.details_scroll_offset + 40)

                elif event.key == pygame.K_RETURN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.quit_button_rect.collidepoint(mouse_pos):
                        self._play_sound(self.quit_sound)
                        return "QUIT"
                    
                    if self.games_list:
                        self._play_sound(self.select_sound)  # Sonido de selección / Enter
                        selected = self.games_list[self.selected_index]
                        return {"action": "LAUNCH", "game_data": selected}
                        
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.quit_button_rect.collidepoint(event.pos):
                    self._play_sound(self.quit_sound)
                    return "QUIT"

            elif event.type == pygame.MOUSEWHEEL:
                mouse_pos = pygame.mouse.get_pos()
                details_panel_rect = pygame.Rect(Settings.S_WIDTH - 440, 100, 420, 560)
                
                if details_panel_rect.collidepoint(mouse_pos):
                    scroll_speed = 30
                    self.details_scroll_offset -= event.y * scroll_speed
                    self.details_scroll_offset = max(0, min(self.max_details_scroll, self.details_scroll_offset))

        return None

    def _ensure_selection_visible(self):
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.visible_rows:
            self.scroll_offset = self.selected_index - self.visible_rows + 1

    def update(self, dt):
    # Reducir la opacidad de la capa negra hasta desaparecer
        if self.fade_alpha > 0:
            self.fade_alpha = max(0, self.fade_alpha - self.fade_speed)
        return None

    def draw(self, screen: pygame.Surface) -> None:
        background = AssetManager.get_asset("menu_background")
        if background and isinstance(background, pygame.surface.Surface):
            screen.blit(pygame.transform.scale(background, (Settings.S_WIDTH, Settings.S_HEIGHT)), (0, 0))
        else:
            screen.fill(Settings.BACKGROUND_COLOR)

        # Panel lateral izquierdo (Lista de juegos)
        list_panel_rect = pygame.Rect(40, self.menu_top - 20, 620, self.visible_rows * self.row_height + 60)
        pygame.draw.rect(screen, (25, 25, 25), list_panel_rect, border_radius=18)
        pygame.draw.rect(screen, Settings.HIGHLIGHT_COLOR, list_panel_rect, 2, border_radius=18)

        title_label_font = _get_font(30)
        title_label = title_label_font.render("Juegos", True, (255, 255, 255))
        screen.blit(title_label, (list_panel_rect.x + 24, list_panel_rect.y - 36))

        # Panel lateral derecho (Detalles del juego)
        details_panel_rect = pygame.Rect(Settings.S_WIDTH - 440, 100, 420, 560)
        pygame.draw.rect(screen, (25, 25, 25), details_panel_rect, border_radius=18)
        pygame.draw.rect(screen, Settings.HIGHLIGHT_COLOR, details_panel_rect, 2, border_radius=18)

        details_content_rect = pygame.Rect(details_panel_rect.x + 18, details_panel_rect.y + 18, details_panel_rect.width - 36, details_panel_rect.height - 36)
        pygame.draw.rect(screen, (35, 35, 35), details_content_rect, border_radius=16)

        font = _get_font(28)

        # Dibujar lista de juegos
        visible_end = min(self.scroll_offset + self.visible_rows, len(self.games_list))
        for index in range(self.scroll_offset, visible_end):
            game = self.games_list[index]
            label = f"> {game.get('title', 'Juego sin nombre')}" if index == self.selected_index else game.get('title', 'Juego sin nombre')
            color = Settings.HIGHLIGHT_COLOR if index == self.selected_index else Settings.TEXT_COLOR
            y = self.menu_top + (index - self.scroll_offset) * self.row_height
            if index == self.selected_index:
                row_rect = pygame.Rect(60, y - 4, 560, self.row_height - 8)
                pygame.draw.rect(screen, (45, 45, 45), row_rect, border_radius=12)
            text = font.render(label, True, color)
            screen.blit(text, (80, y))

        # Botón Salir
        pygame.draw.rect(screen, (220, 50, 50), self.quit_button_rect)
        pygame.draw.rect(screen, Settings.HIGHLIGHT_COLOR, self.quit_button_rect, 2)
        quit_text = font.render("Salir", True, (255, 255, 255))
        screen.blit(
            quit_text,
            (
                self.quit_button_rect.x + self.quit_button_rect.width // 2 - quit_text.get_width() // 2,
                25
            )
        )

        # Dibujar contenido del juego seleccionado
        if self.games_list:
            selected = self.games_list[self.selected_index]
            
            title_text = selected.get("title", "")
            description = selected.get("description", "")
            authors = selected.get("authors", ["Desconocido"])
            group = selected.get("group_number", "")

            # Carátula del juego (Estática)
            cover = AssetManager.get_cover(selected.get("folder", ""))
            cover = pygame.transform.scale(cover, (380, 260))
            cover_x = Settings.S_WIDTH - 420
            cover_y = 120
            cover_card_rect = pygame.Rect(cover_x - 6, cover_y - 6, 392, 272)
            pygame.draw.rect(screen, (10, 10, 10), cover_card_rect, border_radius=20)
            pygame.draw.rect(screen, Settings.HIGHLIGHT_COLOR, cover_card_rect, 2, border_radius=20)
            screen.blit(cover, (cover_x, cover_y))
            pygame.draw.rect(screen, Settings.HIGHLIGHT_COLOR, (cover_x, cover_y, 380, 260), 2, border_radius=18)

            # Área reservada para el texto descriptivo
            info_area_x = cover_x
            info_area_y = cover_y + 280
            info_area_w = 380
            info_area_h = details_content_rect.bottom - info_area_y - 10
            
            info_rect = pygame.Rect(info_area_x, info_area_y, info_area_w, info_area_h)

            screen.set_clip(info_rect)

            # Renderizado con offset de desplazamiento
            info_x = info_area_x
            info_y = info_area_y - self.details_scroll_offset

            title_font = pygame.font.Font(None, 40)
            text_font = _get_font(20)

            title_lines = str(title_text).split('\n')
            for t_line in title_lines:
                screen.blit(title_font.render(t_line, True, Settings.HIGHLIGHT_COLOR), (info_x, info_y))
                info_y += 36
            info_y += 8

            info_y = self._render_multiline(screen, description, text_font, Settings.TEXT_COLOR, info_x, info_y, 360, 26)
            info_y += 8
            
            screen.blit(text_font.render("Autores:", True, Settings.TEXT_COLOR), (info_x, info_y))
            info_y += 32
            
            if isinstance(authors, list):
                authors_str = ", ".join([str(a) for a in authors])
            else:
                authors_str = str(authors)
            
            info_y = self._render_multiline(screen, authors_str, text_font, Settings.TEXT_COLOR, info_x, info_y, 360, 26)
            
            info_y += 14 
            screen.blit(text_font.render(f"Grupo: {group}", True, Settings.TEXT_COLOR), (info_x, info_y))
            info_y += 30

            total_content_height = info_y - (info_area_y - self.details_scroll_offset)
            self.max_details_scroll = max(0, total_content_height - info_area_h)

            screen.set_clip(None)

        # Indicador de controles en múltiples líneas
        hint_font = _get_font(18)
        hint_text = "ENTER para jugar\nFlechas ARRIBA/ABAJO para cambiar\nRueda del ratón para scroll de descripción"
        self._render_multiline(screen, hint_text, hint_font, Settings.TEXT_COLOR, 80, Settings.S_HEIGHT - 100, 500, 22)
        if self.fade_alpha > 0:
            self.fade_surface.set_alpha(self.fade_alpha)
            screen.blit(self.fade_surface, (0, 0))