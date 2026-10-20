import pygame
import sys # not needed rn but maybe at some point
import random
import math

pygame.init()

window_w = 1440
window_h = 810
virtual_w = 640 # using a virtual scaling system to keep pixel art crispy
virtual_h = 360

window = pygame.display.set_mode((window_w, window_h))
canvas = pygame.Surface((virtual_w, virtual_h))
clock = pygame.time.Clock()
pygame.display.set_caption("Pixel Pawn: DELUXE EDITION")
pygame.mouse.set_visible(False) # so that i can make a custom cursor

game_state  = "title" # global variables
running = True
time_control_minutes = 10
white_time = time_control_minutes * 60
black_time = time_control_minutes * 60
last_time = 0
turn = 'white'
selected_tile = None
dragging_piece = None
game_message = ""
game_over = False
possible_moves = []


# text stuff
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

left_arrow_rect = pygame.Rect(virtual_w // 2 - 90, 150, 30, 30)
right_arrow_rect = pygame.Rect(virtual_w // 2 + 60, 148, 30, 30)

back_btn_text = ui_font.render("BACK", True, (255, 255, 255))
back_btn_shadow_text = ui_font.render("BACK", True, (10, 10, 10))
back_btn_rect = back_btn_text.get_rect(center = (virtual_w // 2, 235))


# stuff on table
board_base = pygame.image.load("graphics/board.png").convert_alpha()
board_surf = pygame.transform.scale_by(board_base, 2)
board_x = ((320 - board_surf.get_width()) // 2) + 120
board_y = ((virtual_h - board_surf.get_height()) // 2) + 20
board_rect = board_surf.get_rect(topleft = (board_x, board_y))

timer_surf = pygame.image.load("graphics/timer.png").convert_alpha()
timer_rect = timer_surf.get_rect(topleft = (virtual_w // 2 + 55, virtual_h - 355))

# actual board layout
board_layout = [
    ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
    ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
    ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
]

pieces_sprite = {}
sprite_sheet = pygame.image.load("graphics/chess_pieces.png").convert_alpha()

sprite_w = 11
sprite_h = sprite_sheet.get_height() 
sheet_order = ['bP', 'bR', 'bN', 'skip','bB', 'skip', 'bQ', 'bK', 'wP', 'wR', 'wN', 'skip', 'wB', 'skip', 'wQ', 'wK']

for index, piece in enumerate(sheet_order):
    if piece == "skip":
        continue
    crop_x = index * sprite_w
    crop_y = 0
    sub_surf = sprite_sheet.subsurface(pygame.Rect(crop_x, crop_y, sprite_w, sprite_h))
    pieces_sprite[piece] = pygame.transform.scale_by(sub_surf, 2)

bg = pygame.image.load('graphics/bg.png')

# mapping grid to the board and the back cause isometric is weird also hard  
def iso_to_grid(mx, my):
    start_x = 282
    start_y = 61
    tile_w = 64
    tile_h = 32

    dx = mx - start_x
    dy = (my + 7) - start_y

    rot_col = int((dx / (tile_w / 2) + dy / (tile_h / 2)) / 2)
    rot_row = int((dy / (tile_h / 2) - dx / (tile_w / 2)) / 2)

    row = rot_col
    col = 7 - rot_row

    if 0 <= row < 8 and 0 <= col < 8:
        return row, col

    return None

def grid_to_iso(row, col): # turns the grid back into iso cords
    start_x = 282
    start_y = 61
    tile_w = 64
    tile_h = 32

    rot_row = 7 - col
    rot_col = row

    iso_x = start_x + (rot_col - rot_row) * (tile_w // 2)
    iso_y = start_y + (rot_row + rot_col) * (tile_h // 2)

    return iso_x, iso_y + 16

# move limitations for pieces
def is_piece_move_valid(start_pos, end_pos):
    s_row, s_col = start_pos
    e_row, e_col = end_pos
    piece = board_layout[s_row][s_col]
    target = board_layout[e_row][e_col]

    if target != "--" and target[0] == piece[0]:
        return False

    dx = e_col - s_col
    dy = e_row - s_row

    piece_type = piece[1]

    if piece_type == 'N':
        return (dx**2 + dy**2) == 5

    elif piece_type == 'P':
        direction = -1 if piece.startswith('w') else 1
        start_row = 6 if piece.startswith('w') else 1
        if dx == 0 and dy == direction:
            return target == '--'
        if dx == 0  and  s_row == start_row and dy == (2 * direction):
            return target == '--' and board_layout[s_row + direction][s_col] == '--'
        if dx**2 == 1 and dy == direction:
            return target != '--'
        return False

    elif piece_type == 'K':
        return 0 < (dx**2 + dy**2) <= 2

    elif piece_type in ('R', 'B', 'Q'):
        is_rook_move = (dx * dy == 0)
        is_bishop_move = (dx**2 == dy**2)

        if piece_type == 'R' and not is_rook_move:
            return False
        if piece_type == 'B' and not is_bishop_move:
            return False
        if piece_type == 'Q' and not (is_bishop_move or is_rook_move):
            return False

        step_x = 0 if dx == 0 else dx // abs(dx)
        step_y = 0 if dy == 0 else dy // abs(dy)

        check_row = s_row + step_y
        check_col = s_col + step_x

        while (check_row, check_col) != (e_row, e_col):
            if board_layout[check_row][check_col] != '--':
                return False
            check_row += step_y
            check_col += step_x
        return True
    
    return False

def opposite_color(color):
    return 'black' if color == 'white' else 'white'

def piece_attacks_square(start_pos, target_pos):
    s_row, s_col = start_pos
    t_row, t_col = target_pos

    piece = board_layout[s_row][s_col]
    if piece == '--':
        return False

    dx = t_col - s_col
    dy = t_row - s_row
    piece_type = piece[1]
    color = piece[0]

    if piece_type == 'P':
        direction = -1 if color == 'w' else 1
        return abs(dx) == 1 and dy == direction

    if piece_type == 'N':
        return dx**2 + dy**2 == 5

    if piece_type == 'K':
        return 0 < max(abs(dx), abs(dy)) <= 1

    if piece_type in ('R', 'B', 'Q'):
        rook_move = dx == 0 or dy == 0
        bishop_move = abs(dx) == abs(dy)

        if piece_type == 'R' and not rook_move:
            return False
        if piece_type == 'B' and not bishop_move:
            return False
        if piece_type == 'Q' and not (rook_move or bishop_move):
            return False

        step_col = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_row = 0 if dy == 0 else (1 if dy > 0 else -1)

        row = s_row + step_row
        col = s_col + step_col

        while (row, col) != (t_row, t_col):
            if board_layout[row][col] != '--':
                return False
            row += step_row
            col += step_col
        return True
    return False

def is_square_attacked(pos, by_colour):
    prefix = 'w' if by_colour == 'white' else 'b'
    for row in range(8):
        for col in range(8):
            piece = board_layout[row][col]
            if piece.startswith(prefix) and piece_attacks_square((row, col), pos):
                return True
    return False

def is_in_check(colour):
    king = 'wK' if colour == 'white' else 'bK'
    
    for row in range(8):
        for col in range(8):
            if board_layout[row][col] == king:
                return is_square_attacked((row, col), opposite_color(colour))
    print(f"DEBUG: {king} not found on board!")
    return False

def is_move_legal(start_pos, end_pos):
    s_row, s_col = start_pos
    e_row, e_col = end_pos
    piece = board_layout[s_row][s_col]
    target = board_layout[e_row][e_col]

    if piece == '--':
        return False

    if target != '--' and target[1] == 'K':
        return False

    if not is_piece_move_valid(start_pos, end_pos):
        return False

    colour = 'white' if piece.startswith('w') else 'black'

    board_layout[s_row][s_col] = '--'
    board_layout[e_row][e_col] = piece

    safe = not is_in_check(colour)

    board_layout[s_row][s_col] = piece
    board_layout[e_row][e_col] = target

    return safe

def get_legal_moves(start_pos):
    legal_moves = []

    for row in range(8):
        for col in range(8):
            if is_move_legal(start_pos, (row, col)):
                legal_moves.append((row, col))
    return legal_moves

def has_legal_moves(colour):
    prefix = 'w' if colour == 'white' else 'b'
    for row in range(8):
        for col in range(8):
            piece = board_layout[row][col]
            if not piece.startswith(prefix):
                continue
            start_pos = (row, col)
            for end_row in range(8):
                for end_col in range(8):
                    if is_move_legal(start_pos, (end_row, end_col)):
                        return True
    return False

def make_iso_text(text_string, font, text_color, shear_y = 0.5):

    flat_timer_text = font.render(text_string, True, text_color)
    width, height = flat_timer_text.get_size()
    slant_stretch = int(abs(shear_y) * width)
    new_height = height + slant_stretch + 12
    iso_surface = pygame.Surface((width, new_height), pygame.SRCALPHA)

    for x in range(width):
        offset_y = int(shear_y * (x))
        if shear_y < 0:
            offset_y += slant_stretch
  
        iso_surface.blit(flat_timer_text, (x, offset_y + 6), (x, 0, 1, height))

    return iso_surface

# main loop
while running:
    # get mouse position cause were doing the virtual canvas thing and mouse pos is messed up

    if game_state == 'play':
        current_time = pygame.time.get_ticks()
        elasped_seconds = (current_time - last_time) / 1000
        last_time = current_time

        if turn == 'white':
            white_time = max(0, white_time - elasped_seconds)
        else:
            black_time = max(0, black_time - elasped_seconds)

    raw_mx, raw_my = pygame.mouse.get_pos()
    mx = int(raw_mx * (virtual_w / window_w))
    my = int(raw_my * (virtual_h / window_h))

    hovered_tile = iso_to_grid(mx, my)

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
                        last_time = pygame.time.get_ticks()
                        game_message = ""
                        game_over = False
                        game_state = "play"
                    elif setup_hover:
                        game_state = "setup"

                if game_state == "play" and not game_over and hovered_tile is not None:
                    click_row, click_col = hovered_tile
                    clicked_piece = board_layout[click_row][click_col]

                    if selected_tile is None:  #  all the code for selecting a piece and like moving it
                        if clicked_piece != "--" and ((turn == 'white' and clicked_piece.startswith('w')) or (turn == 'black' and clicked_piece.startswith('b'))):
                            selected_tile = hovered_tile
                            dragging_piece = clicked_piece
                            possible_moves = get_legal_moves(selected_tile)
                            board_layout[click_row][click_col] = "--"

                elif game_state == "setup": # code for setup screen but like i havent actually added buttosn so its invisible, spooky
                    if left_arrow_rect.collidepoint(mx, my):
                        time_control_minutes = max(1, time_control_minutes - 1)
                    elif right_arrow_rect.collidepoint(mx, my):
                        time_control_minutes = min(60, time_control_minutes + 1)
                    elif back_btn_rect.collidepoint(mx, my):
                        game_state = "title"

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and game_state == "play":
                if dragging_piece is not None:
                    if hovered_tile is not None:
                        s_row, s_col = selected_tile
                        board_layout[s_row][s_col] = dragging_piece
                        possible_moves = []

                        move_is_valid = is_move_legal(selected_tile, hovered_tile)

                        board_layout[s_row][s_col] = "--"

                        if move_is_valid:
                        # if is_move_legal(selected_tile, hovered_tile):
                            board_layout[hovered_tile[0]][hovered_tile[1]] = dragging_piece
                            if selected_tile != hovered_tile:
                                turn = opposite_color(turn)

                                if is_in_check(turn):
                                    if not has_legal_moves(turn):
                                        winner = opposite_color(turn).upper()
                                        game_message = f"Checkmate!{winner} wins"
                                        game_over = True
                                    else:
                                        game_message = f"{turn.upper()} is in check"

                                else:
                                    if not has_legal_moves(turn):
                                        game_message = 'Stalemate!'
                                        game_over = True
                                    else:
                                        game_message = ""
                        else:
                            board_layout[selected_tile[0]][selected_tile[1]] = dragging_piece
                    else:
                        board_layout[selected_tile[0]][selected_tile[1]] = dragging_piece
                    dragging_piece = None
                    selected_tile = None
           
    canvas.fill((42, 42, 58))

    if game_state == "title": # basically done
       
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

    if game_state == "setup": # TODO: Add setup screen
        setup_title = title_font.render("TIME CONTROL", True, (255, 255, 255))
        setup_title_shadow = title_font.render("TIME CONTROL", True, (10, 10, 10))
        setup_title_rect = setup_title.get_rect(center = (virtual_w // 2 + 10, 70))
        canvas.blit(setup_title_shadow, setup_title_rect.move(4, 4))
        canvas.blit(setup_title, setup_title_rect)

        mins_text = ui_font.render(f'{time_control_minutes}Min', True, (255, 255, 255))
        mines_shadow_text = ui_font.render(f'{time_control_minutes}Min', True, (10, 10, 10))
        mins_rect = mins_text.get_rect(center = (virtual_w // 2, 165))
        canvas.blit(mines_shadow_text, mins_rect.move(3, 3))
        canvas.blit(mins_text, mins_rect)

        left_arrow_text = ui_font.render('<', True, (255, 255, 255) if not left_arrow_rect.collidepoint(mx, my) else (238, 220, 130))
        right_arrow_text = ui_font.render('>', True, (255, 255, 255) if not right_arrow_rect.collidepoint(mx, my) else (238, 220, 130))
        back_btn_text = ui_font.render('BACK', True, (255, 255, 255) if not back_btn_rect.collidepoint(mx, my) else (238, 220, 130))

        canvas.blit(left_arrow_text, left_arrow_text.get_rect(center = left_arrow_rect.center))
        canvas.blit(right_arrow_text, right_arrow_text.get_rect(center = right_arrow_rect.center))
        canvas.blit(back_btn_shadow_text, back_btn_rect.move(3,3))
        canvas.blit(back_btn_text, back_btn_text.get_rect(center = back_btn_rect.center))
       
    if game_state == "play":
  
        canvas.blit(bg, (0,0))
        canvas.blit(board_surf, board_rect)
        canvas.blit(timer_surf, timer_rect)
        w_mins, w_secs = int(white_time // 60), int(white_time % 60)
        b_mins, b_secs = int(black_time // 60), int(black_time % 60)

        if turn == 'white':
            active_time = white_time    
        else:
            active_time = black_time

        text_colour = (190, 180, 200)
        minutes = int(active_time // 60)
        seconds = int(active_time % 60)

        time_str = f"{minutes:02d} {seconds:02d}"

        hr_font = pygame.font.Font("fonts/ThaleahFat.ttf", 64)

        iso_hr_text = make_iso_text(time_str, hr_font, text_colour, shear_y = 0.5)

        final_w = iso_hr_text.get_width() // 2
        final_h = iso_hr_text.get_height() // 2
        smooth_timer_text = pygame.transform.scale(iso_hr_text, (final_w, final_h))

        clock_screen_centre = (timer_rect.x + 60, timer_rect.y + 76)
        canvas.blit(smooth_timer_text, smooth_timer_text.get_rect(center = clock_screen_centre))

        if hovered_tile is not None:
            hover_surf = pygame.Surface((64, 32), pygame.SRCALPHA)
            pygame.draw.polygon(hover_surf, (255, 235, 150, 80), [(32, 0), (64, 16), (32, 32), (0, 16)])
            h_row, h_col = hovered_tile
            iso_x, iso_y = grid_to_iso(h_row, h_col)
            canvas.blit(hover_surf, (iso_x - 34, iso_y - 15))

        if selected_tile is not None:
            select_surf = pygame.Surface((64, 32), pygame.SRCALPHA)
            pygame.draw.polygon(select_surf, (100, 149, 237, 100), [(32, 0), (64, 16), (32, 32), (0, 16)])
            s_row, s_col = selected_tile
            iso_x, iso_y = grid_to_iso(s_row, s_col)
            canvas.blit(select_surf, (iso_x - 34, iso_y - 15))

        shadow_surf = pygame.Surface((15,8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (20, 15, 10, 90), (0,0,15,8))
        shadow_surf = pygame.transform.scale_by(shadow_surf, 2)

        mouse_grid = iso_to_grid(mx, my)
        mouse_row = mouse_grid[0] if mouse_grid is not None else -1

        for move_row, move_col in possible_moves:
                    iso_x, iso_y = grid_to_iso(move_row, move_col)
                    canvas.blit(select_surf, (iso_x - 34, iso_y - 15))

        for row in range(8):
            for col in range(8):
                piece = board_layout[row][col]
                if piece != "--":
                    base_x, base_y = grid_to_iso(row, col)
                    canvas.blit(shadow_surf, (base_x - 16, base_y - 7))

        if dragging_piece is not None:
                    sprite = pieces_sprite[dragging_piece]
                    drag_x = mx - (sprite.get_width() // 2)
                    drag_y = my - sprite.get_height() + 7
                    canvas.blit(shadow_surf, (drag_x - 5, drag_y + 60))
                    canvas.blit(sprite, (drag_x, drag_y))

        for row in range(8):

            if dragging_piece is not None and mouse_row == row :
                sprite = pieces_sprite[dragging_piece]
                drag_x = mx - (sprite.get_width() // 2)
                drag_y = my - sprite.get_height() + 7
                canvas.blit(sprite, (drag_x, drag_y))

            for col in range(8):
                piece = board_layout[row][col]

                if piece != "--":
                    base_x, base_y = grid_to_iso(row, col)
                    sprite = pieces_sprite[piece]
                    render_x = base_x - (sprite.get_width() // 2)
                    render_y = base_y - sprite.get_height() + 7 

                    if selected_tile == (row, col):
                        render_y -= 10
                    canvas.blit(sprite, (render_x, render_y))

            if dragging_piece is not None and mouse_row >= 7:
                sprite = pieces_sprite[dragging_piece]
                drag_x = mx - (sprite.get_width() // 2)
                drag_y = my - sprite.get_height() + 7
                canvas.blit(sprite, (drag_x, drag_y))

        if game_message:
            message_colour = ((255, 100, 100) if 'Check' in game_message or 'Wins' in game_message else (238, 220, 130))

            message_surf = ui_font.render(game_message, True, message_colour)
            canvas.blit(message_surf, (12,12))

    # draw cursor cross hair rn
    pygame.draw.line(canvas, (255, 255, 255), (mx, my - 4), (mx, my + 4), 1)
    pygame.draw.line(canvas, (255, 255, 255), (mx - 4, my), (mx + 4, my), 1)
    # want to make it like expand when hovering a piece or maybe hoding a piece or smthn

    pygame.transform.scale(canvas, (window_w, window_h), window)

    pygame.display.update()
    clock.tick(120)

pygame.quit()

