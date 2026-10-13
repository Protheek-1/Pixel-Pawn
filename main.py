import pygame
import sys
import random
import math

pygame.init()

window_w = 1440
window_h = 810
virtual_w = 480
virtual_h = 270

window = pygame.display.set_mode((window_w, window_h))
canvas = pygame.Surface((virtual_w, virtual_h))
clock = pygame.time.Clock()
pygame.display.set_caption("Pixel Pawn")

game_state  = "title"
running = True

title_font = pygame.font.Font("fonts/ThaleahFat.ttf", 175)
shadow_text = title_font.render("Pixel Pawn", True, (10, 10, 10))
title_text = title_font.render("Pixel Pawn", True, (255, 255, 255))
title_rect = title_text.get_rect(center = (720, 250))



while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    if game_state == "title":
        window.fill((44, 44, 60))
        window.blit(shadow_text, title_rect.move(12, 12))
        window.blit(title_text, title_rect)
        

    pygame.display.update()
    clock.tick(60)

pygame.quit()

