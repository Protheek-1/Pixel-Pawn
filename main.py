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

time_control_minutes = 10
white_time = time_control_minutes * 60
black_time = time_control_minutes * 60
turn = 'white'

title_font = pygame.font.Font("fonts/ThaleahFat.ttf", 80)
shadow_text = title_font.render("Pixel Pawn", True, (10, 10, 10))
title_text = title_font.render("Pixel Pawn", True, (255, 255, 255))
title_rect = title_text.get_rect(center = (virtual_w // 2, 140))

ui_font = pygame.font.Font("fonts/ThaleahFat.ttf", 32)

start_text = ui_font.render("START", True, (255, 255, 255))
start_shadow_text = ui_font.render("START", True, (10, 10, 10))
start_hover_text = ui_font.render("> START <", True, (238, 220, 130))
start_rect = start_text.get_rect(center = (virtual_w // 2 - 60, 225))
start_hover_rect = start_rect.move(-18, 0)

setup_text = ui_font.render("SETUP", True, (255, 255, 255))
setup_shadow_text = ui_font.render("SETUP", True, (10, 10, 10))
setup_hover_text = ui_font.render("> SETUP <", True, (238, 220, 130))
setup_rect = setup_text.get_rect(center = (virtual_w // 2 + 60, 225))
setup_hover_rect = setup_rect.move(-18, 0)

board_base = pygame.image.load("graphics/board.png").convert_alpha()
board_surf = pygame.transform.scale_by(board_base, 2)
board_x = ((320 - board_surf.get_width()) // 2) + 120
board_y = ((virtual_h - board_surf.get_height()) // 2) + 20
board_rect = board_surf.get_rect(topleft = (board_x, board_y))

timer_surf = pygame.image.load("graphics/timer.png").convert_alpha()
timer_rect = timer_surf.get_rect(topleft = (virtual_w // 2 + 55, virtual_h - 355))

bg = pygame.image.load('graphics/bg.png')

while running:

    raw_mx, raw_my = pygame.mouse.get_pos()
    mx = int(raw_mx * (virtual_w / window_w))
    my = int(raw_my * (virtual_h / window_h))

    start_hover = start_rect.collidepoint(mx, my)
    setup_hover = setup_rect.collidepoint(mx, my)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if game_state == "title":
                    if start_hover:
                        white_time = time_control_minutes * 60
                        black_time = time_control_minutes * 60
                        turn = 'white'
                        game_state = "play"
                    elif setup_hover:
                        game_state = "setup"

                elif game_state == "setup":
                    if pygame.Rect(virtual_w // 2 + 60, 160, 30, 30).collidepoint(mx, my):
                        time_control_minutes = min(60, time_control_minutes + 1)
                    elif pygame.Rect(virtual_w // 2 - 90, 160, 30, 30).collidepoint(mx, my):
                        time_control_minutes = max(1, time_control_minutes - 1)
                    elif pygame.Rect(virtual_w // 2 - 50, 200, 30, 30).collidepoint(mx, my):
                        game_state = "title"
           
    canvas.fill((44, 44, 60))

    if game_state == "title":
       
        canvas.blit(shadow_text, title_rect.move(4, 4))
        canvas.blit(title_text, title_rect)

        canvas.blit(setup_shadow_text, setup_rect.move(3,3))
        canvas.blit(start_shadow_text, start_rect.move(3,3))

        if start_hover:
            box_rect = start_rect.inflate(16, 12)
            canvas.blit(start_hover_text, start_hover_rect)
        else:
            box_rect = start_rect.inflate(10, 6)
            canvas.blit(start_text, start_rect)

        if setup_hover:
            box_rect = setup_rect.inflate(16, 12)
            canvas.blit(setup_hover_text, setup_hover_rect)
        else:
            box_rect = setup_rect.inflate(10, 6)
            canvas.blit(setup_text, setup_rect)

    if game_state == "setup":
        pass
       

    if game_state == "play":
        canvas.blit(bg, (0,0))
        canvas.blit(board_surf, board_rect)
        canvas.blit(timer_surf, timer_rect)

    pygame.transform.scale(canvas, (window_w, window_h), window)

    pygame.display.update()
    clock.tick(60)

pygame.quit()

