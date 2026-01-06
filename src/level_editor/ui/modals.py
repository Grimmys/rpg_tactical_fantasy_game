"""Modal rendering and state helpers for save/load dialogs."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import pygame


def draw_save_modal(screen: pygame.Surface, total_w: int, grid_h: int, font: pygame.font.Font, path_input: str, message: str) -> None:
    modal_w = min(760, total_w - 40)
    modal_h = 180
    modal_x = (total_w - modal_w) // 2
    modal_y = (grid_h - modal_h) // 2
    pygame.draw.rect(screen, (30, 30, 30), (modal_x, modal_y, modal_w, modal_h))
    pygame.draw.rect(screen, (200, 200, 200), (modal_x, modal_y, modal_w, modal_h), 2)
    label = font.render("Save As", True, (240, 240, 240))
    screen.blit(label, (modal_x + 12, modal_y + 12))
    input_rect = pygame.Rect(modal_x + 12, modal_y + 50, modal_w - 24, 28)
    pygame.draw.rect(screen, (50, 50, 50), input_rect)
    pygame.draw.rect(screen, (200, 200, 200), input_rect, 1)
    txt = font.render(path_input, True, (240, 240, 240))
    screen.blit(txt, (input_rect.x + 6, input_rect.y + 6))
    if message:
        msg = font.render(message, True, (200, 200, 120))
        screen.blit(msg, (modal_x + 12, modal_y + modal_h - 32))


def draw_load_modal(
    screen: pygame.Surface,
    total_w: int,
    grid_h: int,
    font: pygame.font.Font,
    files: List[Path],
    active_index: int,
    path_input: str,
    message: str,
) -> None:
    modal_w = min(760, total_w - 40)
    modal_h = min(420, grid_h - 40)
    modal_x = (total_w - modal_w) // 2
    modal_y = (grid_h - modal_h) // 2
    pygame.draw.rect(screen, (30, 30, 30), (modal_x, modal_y, modal_w, modal_h))
    pygame.draw.rect(screen, (200, 200, 200), (modal_x, modal_y, modal_w, modal_h), 2)
    label = font.render("Load", True, (240, 240, 240))
    screen.blit(label, (modal_x + 12, modal_y + 12))
    input_rect = pygame.Rect(modal_x + 12, modal_y + 40, modal_w - 24, 28)
    pygame.draw.rect(screen, (50, 50, 50), input_rect)
    pygame.draw.rect(screen, (200, 200, 200), input_rect, 1)
    txt = font.render(path_input, True, (240, 240, 240))
    screen.blit(txt, (input_rect.x + 6, input_rect.y + 6))

    list_top = modal_y + 80
    list_h = modal_h - 120
    item_h = 22
    visible = max(1, list_h // item_h)
    start = max(0, active_index - visible + 1) if active_index >= visible else 0
    end = min(len(files), start + visible)
    for idx in range(start, end):
        y = list_top + (idx - start) * item_h
        bg = (60, 60, 60) if idx == active_index else (40, 40, 40)
        pygame.draw.rect(screen, bg, (modal_x + 12, y, modal_w - 24, item_h - 2))
        name = str(files[idx])
        txt = font.render(name, True, (230, 230, 230))
        screen.blit(txt, (modal_x + 16, y + 2))

    if message:
        msg = font.render(message, True, (200, 200, 120))
        screen.blit(msg, (modal_x + 12, modal_y + modal_h - 32))


def handle_save_input(state, event: pygame.event.Event) -> bool:
    if event.key == pygame.K_ESCAPE:
        state.save_as_active = False
        state.save_message = ""
    elif event.key == pygame.K_RETURN:
        return False  # signal to perform save
    elif event.key == pygame.K_BACKSPACE:
        state.save_input = state.save_input[:-1]
    else:
        if event.unicode and 31 < ord(event.unicode) < 127:
            state.save_input += event.unicode
    return True


def handle_load_input(state, event: pygame.event.Event) -> bool:
    if event.key == pygame.K_ESCAPE:
        state.load_active = False
        state.load_message = ""
    elif event.key == pygame.K_RETURN:
        return False  # signal to perform load
    elif event.key == pygame.K_BACKSPACE:
        state.load_input = state.load_input[:-1]
    elif event.key == pygame.K_UP:
        if state.load_files:
            state.load_index = max(0, state.load_index - 1)
    elif event.key == pygame.K_DOWN:
        if state.load_files:
            state.load_index = min(len(state.load_files) - 1, state.load_index + 1)
    else:
        if event.unicode and 31 < ord(event.unicode) < 127:
            state.load_input += event.unicode
    return True
