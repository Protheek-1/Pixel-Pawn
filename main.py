import pygame
import sys
import random
import math

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
pygame.display.set_caption("Pixel Pawn")

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((40, 40, 65))
    pygame.display.update()
    clock.tick(60)

pygame.quit()

