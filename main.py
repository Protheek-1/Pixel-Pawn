import pygame
import sys
import random
import math

pygame.init()

window_w = 1440
window_h = 810
virtual_w = 640
virtual_h = 360

window = pygame.display.set_mode((window_w, window_h))
canvas = pygame.Surface((virtual_w, virtual_h))
clock = pygame.time.Clock()
pygame.display.set_caption("Pixel Pawn: DELUXE EDITION")


game_state  = "title"
running = True

title_font = pygame.font.Font("fonts/ThaleahFat.ttf", 48)
shadow_text = title_font.render("Pixel Pawn", True, (10, 10, 10))
title_text = title_font.render("Pixel Pawn", True, (255, 255, 255))
title_rect = title_text.get_rect(center = (virtual_w // 2, 100))

board_base = pygame.image.load("graphics/board.png").convert_alpha()
board_surf = pygame.transform.scale_by(board_base, 2)
board_x = ((320 - board_surf.get_width()) // 2) + 120
board_y = ((virtual_h - board_surf.get_height()) // 2) + 20
board_rect = board_surf.get_rect(topleft = (board_x, board_y))


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_state = "play"

    canvas.fill((44, 44, 60))

    if game_state == "title":
       
        canvas.blit(shadow_text, title_rect.move(3, 3))
        canvas.blit(title_text, title_rect)

    if game_state == "play":
        canvas.blit(board_surf, board_rect)

    pygame.transform.scale(canvas, (window_w, window_h), window)

    pygame.display.update()
    clock.tick(60)

pygame.quit()

