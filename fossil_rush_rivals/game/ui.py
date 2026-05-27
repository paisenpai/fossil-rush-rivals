from typing import Tuple

import pygame


def build_fonts() -> Tuple[pygame.font.Font, pygame.font.Font]:
    title_font = pygame.font.SysFont("georgia", 28)
    label_font = pygame.font.SysFont("georgia", 18)
    return title_font, label_font
