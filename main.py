import pygame
import sys # not needed rn but maybe at some point
import random
import math
import time

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
menu_open = False
menu_slide_x = canvas.get_width()
last_move_made = None
has_moved_wK = False
has_moved_bK = False
has_moved_wR_left = False
has_moved_wR_right = False
has_moved_bR_left = False
has_moved_bR_right = False
pending_promotion = None
promotion_choices = ['Q', 'R', 'B', 'N']
promotion_rects = [pygame.Rect(228 + i * 46, 155, 40, 40) for i in range(4)]
draw_offer = None
draw_offer_rect = pygame.Rect(495, 90, 130, 35)
home_button_rect = pygame.Rect(495, 135, 130, 35)
accept_draw_rect = pygame.Rect(205, 185, 100, 35)
decline_draw_rect = pygame.Rect(335, 185, 100, 35)
inkwell_surf = pygame.image.load("graphics/inkwell.png").convert_alpha()
inkwell_rect = inkwell_surf.get_rect(center = (virtual_w // 2 + 15, virtual_h - 340))
AI_DIFFICULTIES = {
    "EASY": 2,
    "MEDIUM": 3,
    "HARD": 5
}
AI_DIFFICULTY = "MEDIUM"
player_move_start = time.time()
bot_think_start = None
bot_wait_time = 0
difficulty_buttons = {
    "EASY": pygame.Rect(180, 230, 80, 35),
    "MEDIUM": pygame.Rect(270, 230, 100, 35),
    "HARD": pygame.Rect(380, 230, 80, 35)
}
check_flash_start = None
check_flash_colour = None
CHECK_FLASH_DURATION = 500


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

left_arrow_rect = pygame.Rect(virtual_w // 2 - 90, 125, 30, 30)
right_arrow_rect = pygame.Rect(virtual_w // 2 + 60, 123, 30, 30)

back_btn_text = ui_font.render("BACK", True, (255, 255, 255))
back_btn_shadow_text = ui_font.render("BACK", True, (10, 10, 10))
back_btn_rect = back_btn_text.get_rect(center = (virtual_w // 2, 305))

menu_rect = pygame.Rect(canvas.get_width() - 35, 15, 30, 25)

# stuff on table
board_base = pygame.image.load("graphics/board.png").convert_alpha()
board_surf = pygame.transform.scale_by(board_base, 2)
board_x = ((320 - board_surf.get_width()) // 2) + 120
board_y = ((virtual_h - board_surf.get_height()) // 2) + 20
board_rect = board_surf.get_rect(topleft = (board_x, board_y))

timer_white = pygame.image.load("graphics/timer_white.png").convert_alpha()
timer_black = pygame.image.load("graphics/timer_black.png").convert_alpha()
timer_rect = timer_white.get_rect(topleft = (virtual_w // 2 + 55, virtual_h - 355))

white_king_check = pygame.transform.scale_by(pygame.image.load("graphics/wK_check.png").convert_alpha(), 2)   
black_king_check = pygame.transform.scale_by(pygame.image.load("graphics/bK_check.png").convert_alpha(), 2)

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
            if target != '--':
                return True
            if last_move_made is not None:
                lm_start, lm_end, lm_piece = last_move_made
                if lm_piece[1] == 'P' and lm_end == (s_row, s_col + dx) and abs(lm_start[0] - lm_end[0]) == 2:
                    return True
        return False

    elif piece_type == 'K':
        if 0 < (dx**2 + dy**2) <= 2:
            return True
        if dy == 0 and abs(dx) == 2 and not is_in_check('white' if piece.startswith('w') else 'black'):
            colour = piece[0]
            if colour == 'w' and not has_moved_wK:
                if dx == 2 and not has_moved_wR_right and board_layout[7][5] == '--'and board_layout[7][6] == '--':
                    return is_move_legal(start_pos, (7, 5))
                if dx == -2 and not has_moved_wR_left and board_layout[7][3] == '--' and board_layout[7][2] == '--' and board_layout[7][1] == '--':
                    return is_move_legal(start_pos, (7, 3))
            elif colour == 'b' and not has_moved_bK:
                if dx == 2 and not has_moved_bR_right and board_layout[0][5] == '--' and board_layout[0][6] == '--':
                    return is_move_legal(start_pos, (0, 5))
                if dx == -2 and not has_moved_bR_left and board_layout[0][3] == '--' and board_layout[0][2] == '--' and board_layout[0][1] == '--':
                    return is_move_legal(start_pos, (0, 3))
        return False
    
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

def opposite_colour(colour):
    return 'black' if colour == 'white' else 'white'

def piece_attacks_square(start_pos, target_pos):
    s_row, s_col = start_pos
    t_row, t_col = target_pos

    piece = board_layout[s_row][s_col]
    if piece == '--':
        return False

    dx = t_col - s_col
    dy = t_row - s_row
    piece_type = piece[1]
    colour = piece[0]

    if piece_type == 'P':
        direction = -1 if colour == 'w' else 1
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
                return is_square_attacked((row, col), opposite_colour(colour))
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

AI_PIECE_VALUES = {
    'P': 100,
    'N': 320,
    'B': 330,
    'R': 500,
    'Q': 900,
    'K': 0,
}

AI_STATE_NAMES = [
    "last_move_made",
    "has_moved_wK",
    "has_moved_bK",
    "has_moved_wR_left",
    "has_moved_wR_right",
    "has_moved_bR_left",
    "has_moved_bR_right",
]

def save_search_state():
    return (
        [row[:] for row in board_layout], {name: globals()[name] for name in AI_STATE_NAMES}
    )

def restore_search_state(state):
    saved_board, saved_variables = state
    board_layout[:] = [row[:] for row in saved_board]
    for name, value in saved_variables.items():
        globals()[name] = value

def evaluate_position():
    score = 0  # positive favours white. negative favours black
    values = AI_PIECE_VALUES

    for row in range(8):
        for col in range(8):
            piece = board_layout[row][col]
            if piece == '--':
                continue
            colour = piece[0]
            piece_type = piece[1]
            sign = 1 if colour == 'b' else -1
            score += sign * values[piece_type]
            centre_distance = abs(3.5 - col) + abs(3.5 - row)
            if piece_type in ('P', 'N', 'B', 'Q'):
                score += sign * int((7 - centre_distance)*(3 if piece_type == 'P' else 2))

            if piece_type == 'P':
                advancement = (row - 1) if colour == 'b' else (6 - row)
                score += sign * advancement * 8

            if piece_type in ('N', 'B'):
                starting_row = 0 if colour == 'b' else 7
                if row != starting_row:
                    score += sign * 20

            if piece_type == 'K':
                home_row = 0 if colour == 'b' else 7
                if row == home_row and col in (2, 6):
                    score += sign * 40

    return score

def generate_ai_moves(colour):
    prefix = 'w' if colour == 'white' else 'b'
    moves = []
    for row in range(8):
        for col in range(8):
            piece = board_layout[row][col]
            if not piece.startswith(prefix):
                continue
            start = (row, col)
            for end_row in range(8):
                for end_col in range(8):
                    end = (end_row, end_col)
                    if is_move_legal(start, end):
                        target = board_layout[end_row][end_col]
                        capture_value = (AI_PIECE_VALUES[target[1]] if target != "--" else 0)
                        moves.append((start, end, capture_value))
    moves.sort(key = lambda move: move[2], reverse = True)
    return [(start, end) for start, end, _ in moves]

def apply_search_move(start, end):
    s_row, s_col = start
    e_row, e_col = end
    piece = board_layout[s_row][s_col]
    if (
        piece[1] == 'P' and
        s_col != e_col and
        board_layout[e_row][e_col] == '--'
    ):
        board_layout[s_row][s_col] = '--'
    if piece[1] == 'K' and abs(e_col - s_col) == 2:
        if piece.startswith('w'):
            rook_row = 7#
        else:
            rook_row = 0
        if e_col == 6:
            board_layout[rook_row][5] = (
                'wR' if piece.startswith('w') else 'bR'
            )
            board_layout[rook_row][7] = '--'
        else:
            board_layout[rook_row][3] = (
                'wR' if piece.startswith('w') else 'bR'
            )
            board_layout[rook_row][0] = '--'
    board_layout[s_row][s_col] = '--'
    board_layout[e_row][e_col] = piece

    if piece == 'wK':
        globals()['has_moved_wK'] = True
    elif piece == 'bK':
        globals()['has_moved_bK'] = True
    elif piece == 'wR' and s_row == 7:
        if s_col == 0:
            globals()['has_moved_wR_left'] = True
        elif s_col == 7:
            globals()['has_moved_wR_right'] = True
    elif piece == 'bR' and s_row == 0:
        if s_col == 0:
            globals()['has_moved_bR_left'] = True
        elif s_col == 7:
            globals()['has_moved_bR_right'] = True
    captured = None
    if piece[1] == 'P' and e_row in (0, 7):
        board_layout[e_row][e_col] = (
            'wQ' if piece.startswith('w') else 'bQ'
        )
    globals()['last_move_made'] = (start, end, piece)

def minimax(depth, alpha, beta, colour, position_hisotry = None):
    if position_hisotry is None:
        position_hisotry = []
    position_key = get_position_key(colour)
    if position_key in position_hisotry:
        return 0, None
    position_history = position_hisotry + [position_key]

    if depth == 0:
        return evaluate_position(), None
    moves = generate_ai_moves(colour)
    if not moves:
        if is_in_check(colour):
            if colour == 'white':
                return 100000 + depth, None
            return -100000 - depth, None
        return 0, None
    best_move = None

    if colour == 'black':
        best_score = float('-inf')
        for start, end in moves:
            state = save_search_state()
            apply_search_move(start, end)
            score, _ = minimax(depth - 1, alpha, beta, 'white')
            restore_search_state(state)
            if score > best_score:
                best_score = score
                best_move = (start, end)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score, best_move
    else:
        best_score = float('inf')
        for start, end in moves:
            state = save_search_state()
            apply_search_move(start, end)
            score, _ = minimax(depth - 1, alpha, beta, 'black')
            restore_search_state(state)
            if score < best_score:
                best_score = score
                best_move = (start, end)
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score, best_move

def get_game_position_key():
    board_key = tuple(tuple(row) for row in board_layout)
    castling_rights = (
        has_moved_wK,
        has_moved_bK,
        has_moved_wR_left,
        has_moved_wR_right,
        has_moved_bR_left,
        has_moved_bR_right,
    )
    ep_target = None
    if last_move_made is not None:
        start, end, piece = last_move_made
        if piece in ('wP', 'bP') and abs(start[0] - end[0]) == 2:
            end_row, end_col = end
            capturing_pawn = 'wP' if piece.startswith('w') else 'bP'
            for col in (end_col - 1, end_col + 1):
                if (
                    0 <= col < 8
                    and board_layout[end_row][col] == capturing_pawn
                ):
                    ep_target = ((start[0] + end_row) // 2, end_col)
                    break
    return board_key, castling_rights, ep_target, turn

def record_position():
    key = get_game_position_key()
    position_history[key] = position_history.get(key, 0) + 1
    return position_history[key] >= 3

position_history = {}
record_position()

def find_best_move(colour='black', depth=None):
    if depth is None:
        depth = AI_DIFFICULTIES[AI_DIFFICULTY]
    _, best_move = minimax(depth, float('-inf'), float('inf'), colour)
    return best_move

def get_position_key(colour):
    return (
        tuple(tuple(row) for row in board_layout),
        colour
    )

def make_iso_text(text_string, font, text_colour, shear_y = 0.5):

    flat_timer_text = font.render(text_string, True, text_colour)
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
    raw_mx, raw_my = pygame.mouse.get_pos()
    mx = int(raw_mx * (virtual_w / window_w))
    my = int(raw_my * (virtual_h / window_h))

    hovered_tile = iso_to_grid(mx, my)

    start_hover = start_rect.collidepoint(mx, my)
    setup_hover = setup_rect.collidepoint(mx, my)

    if game_state == "play" and not menu_open and not game_over:
        current_time = pygame.time.get_ticks()
        elasped_seconds = (current_time - last_time) / 1000
        last_time = current_time

        if turn == 'white':
            white_time = max(0, white_time - elasped_seconds)
            if white_time <= 0:
                game_message = "Time, Black wins!"
                game_over = True
                possible_moves = []
                selected_tile = None
                dragging_piece = None
        else:
            black_time = max(0, black_time - elasped_seconds)
            if black_time <= 0:
                game_message = "Time, White wins!"
                game_over = True
                possible_moves = []
                selected_tile = None
                dragging_piece = None
    else:
        last_time = pygame.time.get_ticks() 

    if (
        game_state == "play"
        and turn == "black"
        and not game_over
        and not menu_open
        and pending_promotion is None
    ):
        

        if turn == "black" and bot_think_start is not None:
            if time.time() - bot_think_start >= bot_wait_time:
                ai_move = find_best_move('black')
                if ai_move is not None:
                    start_pos, end_pos = ai_move
                    apply_search_move(start_pos, end_pos)
                    turn = "white"
                    if is_in_check("white"):
                        if not has_legal_moves("white"):
                            game_message = "Checkmate! Black wins"
                            game_over = True
                        else:
                            game_message = ""
                    elif not has_legal_moves("white"):
                        game_message = "Stalemate!"
                        game_over = True
                    else:
                                    game_message = ""
                player_move_start = time.time()
                bot_think_start = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:

                if game_state == "play" and draw_offer is not None:
                    if accept_draw_rect.collidepoint(mx, my):
                        game_message = "Draw Agreed"
                        game_over = True
                        draw_offer = None
                    elif decline_draw_rect.collidepoint(mx, my):
                        draw_offer = None
                    continue

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

                if game_state == "play":
                    
                    if pending_promotion is not None:
                        row, col, colour = pending_promotion
                        for i, choice in enumerate(promotion_choices):
                            if promotion_rects[i].collidepoint(mx, my):
                                
                                board_layout[row][col] = colour + choice
                                pending_promotion = None
                                turn = opposite_colour(turn)

                                if is_in_check(turn):
                                    if not has_legal_moves(turn):
                                        winner = opposite_colour(turn).upper()
                                        game_message = f"Checkmate!{winner} wins"
                                        game_over = True
                                    else:
                                        game_message = f""
                                else:
                                    if not has_legal_moves(turn):
                                        game_message = 'Stalemate!'
                                        game_over = True
                                    else:
                                        game_message = ""
                                if not game_over and record_position():
                                    game_message = "Draw by Repetition!"
                                    game_over = True
                                break
                        continue
                    
                    if menu_rect.collidepoint(mx, my):
                        menu_open = not menu_open
                        continue
                    if menu_open:
                        if draw_offer_rect.collidepoint(mx, my):
                            game_message = "Draw Agreed"
                            game_over = True
                            draw_offer = None
                            menu_open = False

                        elif home_button_rect.collidepoint(mx, my):
                            game_state = "title"
                            menu_open = False
                            draw_offer = None
                            board_layout[:] = [
                                ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
                                ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
                                ['--', '--', '--', '--', '--', '--', '--', '--'],
                                ['--', '--', '--', '--', '--', '--', '--', '--'],
                                ['--', '--', '--', '--', '--', '--', '--', '--'],
                                ['--', '--', '--', '--', '--', '--', '--', '--'],
                                ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
                                ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
                             ]

                        if mx < 480:
                            menu_open = False
                        continue 

                    if not game_over and hovered_tile is not None:
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
                    else:
                        for name, rect in difficulty_buttons.items():
                            if rect.collidepoint(mx, my):
                                AI_DIFFICULTY = name
                                break

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and game_state == "play":
                if dragging_piece is not None:
                    if hovered_tile is not None:
                        s_row, s_col = selected_tile
                        board_layout[s_row][s_col] = dragging_piece
                        possible_moves = []

                        move_is_valid = is_move_legal(selected_tile, hovered_tile)

                        board_layout[s_row][s_col] = "--"

                        target_row = hovered_tile[0]
                        target_col = hovered_tile[1]

                        if move_is_valid:

                            if (dragging_piece[1] == 'P' and s_col != target_col and board_layout[target_row][target_col] == '--'):  
                                board_layout[s_row][target_col] = '--'

                           
                            if dragging_piece == 'wK' and abs(target_col - s_col) == 2:
                                if target_col == 6:
                                    board_layout[7][5] = 'wR'
                                    board_layout[7][7] = '--'
                                elif target_col == 2:
                                    board_layout[7][3] = 'wR'
                                    board_layout[7][0] = '--'

                            elif dragging_piece == 'bK' and abs(target_col - s_col) == 2:
                                if target_col == 6:
                                    board_layout[0][5] = 'bR'
                                    board_layout[0][7] = '--'
                                elif target_col == 2:
                                    board_layout[0][3] = 'bR'
                                    board_layout[0][0] = '--'

                            board_layout[hovered_tile[0]][hovered_tile[1]] = dragging_piece
                            last_move_made = (selected_tile, hovered_tile, dragging_piece)

                            if dragging_piece == 'wP' and hovered_tile[0] == 0:
                                pending_promotion = (target_row, target_col, 'w')
                            elif dragging_piece == 'bP' and hovered_tile[0] == 7:
                                pending_promotion = (target_row, target_col, 'b')

                            if dragging_piece == 'wK': has_moved_wK = True
                            elif dragging_piece == 'bK': has_moved_bK = True
                            elif dragging_piece == 'wR' and s_row == 7:
                                if s_col == 0: has_moved_wR_left = True
                                if s_col == 7: has_moved_wR_right = True
                            elif dragging_piece == 'bR' and s_row == 0:
                                if s_col == 0: has_moved_bR_left = True
                                if s_col == 7: has_moved_bR_right = True

                            if selected_tile != hovered_tile and pending_promotion is None:

                                player_move_time = time.time() - player_move_start
                                bot_wait_time = player_move_time * random.uniform(0.7, 1.2) # testing, change back later
                                bot_think_start = time.time()

                                turn = opposite_colour(turn)

                                if is_in_check(turn):
                                    if not has_legal_moves(turn):
                                        winner = opposite_colour(turn).upper()
                                        game_message = f"Checkmate!{winner} wins"
                                        game_over = True
                                    else:
                                        game_message = f""

                                else:
                                    if not has_legal_moves(turn):
                                        game_message = 'Stalemate!'
                                        game_over = True
                                    else:
                                        game_message = ""
                                if not game_over and record_position():
                                    game_message = "Draw by Repetition!"
                                    game_over = True
                        else:
                            board_layout[selected_tile[0]][selected_tile[1]] = dragging_piece
                            if is_piece_move_valid(selected_tile, hovered_tile):
                                state = save_search_state()
                                try:
                                    apply_search_move(selected_tile, hovered_tile)
                                    if is_in_check(turn):
                                        check_flash_start = pygame.time.get_ticks()
                                        check_flash_colour = (turn)
                                finally:
                                    restore_search_state(state)

                    else:
                        board_layout[selected_tile[0]][selected_tile[1]] = dragging_piece
                    dragging_piece = None
                    selected_tile = None
           
    canvas.blit(pygame.image.load("graphics/chess_bg.png"), (0,0))

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
        mins_rect = mins_text.get_rect(center = (virtual_w // 2, 140))
        canvas.blit(mines_shadow_text, mins_rect.move(3, 3))
        canvas.blit(mins_text, mins_rect)

        left_arrow_text = ui_font.render('<', True, (255, 255, 255) if not left_arrow_rect.collidepoint(mx, my) else (238, 220, 130))
        right_arrow_text = ui_font.render('>', True, (255, 255, 255) if not right_arrow_rect.collidepoint(mx, my) else (238, 220, 130))
        back_btn_text = ui_font.render('BACK', True, (255, 255, 255) if not back_btn_rect.collidepoint(mx, my) else (238, 220, 130))

        canvas.blit(left_arrow_text, left_arrow_text.get_rect(center = left_arrow_rect.center))
        canvas.blit(right_arrow_text, right_arrow_text.get_rect(center = right_arrow_rect.center))

        difficulty_title = ui_font.render("DIFFICULTY", True, (255, 255, 255))
        difficulty_title_shadow = ui_font.render("DIFFICULTY", True, (10, 10, 10))
        difficulty_rect = difficulty_title.get_rect(center = (virtual_w // 2, 190))
        canvas.blit(difficulty_title_shadow, difficulty_rect.move(3, 3))
        canvas.blit(difficulty_title, difficulty_rect)

        for name, rect in difficulty_buttons.items():
            selected = name == AI_DIFFICULTY
            hovered = rect.collidepoint(mx, my)

            if selected:
                colour = (120, 100, 55)
            elif hovered:
                colour = (80, 100, 135)
            else:
                colour = (42, 42, 58)

            pygame.draw.rect(canvas, colour, rect, 0, border_radius=4)

            pygame.draw.rect(canvas, (238, 220, 130) if selected else (190, 180, 200), rect, 2, border_radius=4)
            label = ui_font.render(name, True, (255, 255, 255))
            canvas.blit(label, label.get_rect(center = rect.center))

        canvas.blit(back_btn_shadow_text, back_btn_rect.move(3,3))
        canvas.blit(back_btn_text, back_btn_text.get_rect(center = back_btn_rect.center))
       
    if game_state == "play":
  
        canvas.blit(bg, (0,0))
        canvas.blit(board_surf, board_rect)
        if turn == 'white':
            canvas.blit(timer_black, timer_rect) # accidentally swapped the file names
        else:
            canvas.blit(timer_white, timer_rect)
        w_mins, w_secs = int(white_time // 60), int(white_time % 60)
        b_mins, b_secs = int(black_time // 60), int(black_time % 60)


        canvas.blit(inkwell_surf, inkwell_rect)

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
        canvas.blit(smooth_timer_text, smooth_timer_text.get_rect(left = clock_screen_centre[0] - 36, top = clock_screen_centre[1] - 32))

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
                sprite.set_alpha(255)
                drag_x = mx - (sprite.get_width() // 2)
                drag_y = my - sprite.get_height() + 7
                canvas.blit(sprite, (drag_x, drag_y))

            for col in range(8):
                piece = board_layout[row][col]

                if piece != "--":
                    base_x, base_y = grid_to_iso(row, col)
                    now = pygame.time.get_ticks()
                    flash_active = (
                        check_flash_start is not None
                        and now - check_flash_start < CHECK_FLASH_DURATION
                    )
                    sprite = pieces_sprite[piece]
                    if piece == 'wK':
                        if flash_active and check_flash_colour == 'white':
                            sprite = white_king_check
                        elif is_in_check('white'):
                            sprite = white_king_check
                    elif piece == 'bK':
                        if flash_active and check_flash_colour == 'black':
                            sprite = black_king_check
                        elif is_in_check('black'):
                            sprite = black_king_check
                        
                    render_x = base_x - (sprite.get_width() // 2)
                    if sprite is white_king_check or sprite is black_king_check:
                        render_x -= 1
                    render_y = base_y - sprite.get_height() + 7 

                    if selected_tile == (row, col):
                        render_y -= 10

                    is_white_piece = piece.startswith('w')
                    if (turn == 'white' and is_white_piece) or (turn == 'black' and not is_white_piece):
                        sprite.set_alpha(255)
                    else:
                        sprite.set_alpha(210)
                    canvas.blit(sprite, (render_x, render_y))

            if dragging_piece is not None and mouse_row >= 7:
                sprite = pieces_sprite[dragging_piece]
                sprite.set_alpha(255)
                drag_x = mx - (sprite.get_width() // 2)
                drag_y = my - sprite.get_height() + 7
                canvas.blit(sprite, (drag_x, drag_y))

        if pending_promotion is not None:
            row, col, colour = pending_promotion

            panel_surf = pygame.Surface((210, 62), pygame.SRCALPHA)
            pygame.draw.rect(panel_surf, (20, 20, 25, 195), (0, 0, 210, 62), 0, 5,)
            canvas.blit(panel_surf, (215, 144))

            for i, choice in enumerate(promotion_choices):
                rect = promotion_rects[i]
                box_colour = (238, 220, 130) if rect.collidepoint(mx, my) else (190, 180, 200)
                pygame.draw.rect(canvas, box_colour, rect, 2, 5)
                sprite = pieces_sprite[colour + choice]
                sprite_rect = sprite.get_rect(center = rect.center).move(0, -8)
                canvas.blit(sprite, sprite_rect)

        if game_message:
            message_colour = ((255, 100, 100) if 'Check' in game_message or 'Wins' in game_message else (238, 220, 130))

            message_surf = ui_font.render(game_message, True, message_colour)
            canvas.blit(message_surf, (12,12))

        menu_hover = menu_rect.collidepoint(mx, my)
        line_colour = (238, 220, 130) if menu_hover else (200, 190, 210)

        pygame.draw.line(canvas, line_colour, (menu_rect.x + 10, menu_rect.y - 3), (menu_rect.x + 25, menu_rect.y - 3), 2)
        pygame.draw.line(canvas, line_colour, (menu_rect.x + 10, menu_rect.y + 3), (menu_rect.x + 25, menu_rect.y + 3), 2)
        pygame.draw.line(canvas, line_colour, (menu_rect.x + 10, menu_rect.y + 9), (menu_rect.x + 25, menu_rect.y + 9), 2)

        target_panel_x = (canvas.get_width() - 160) if menu_open else canvas.get_width()
        menu_slide_x += (target_panel_x - menu_slide_x) * 0.2
        if menu_slide_x < canvas.get_width():
            panel_surface = pygame.Surface((160, canvas.get_height()), pygame.SRCALPHA)
            panel_surface.fill((20, 20, 25, 180))
            pygame.draw.line(panel_surface, (238, 220, 130), (0, 0), (0, canvas.get_height()), 1)
            panel_title = ui_font.render("PAUSED", True, (255, 255, 255))
            panel_shadow_title = ui_font.render("PAUSED", True, (10, 10, 10))
            panel_surface.blit(panel_shadow_title, panel_title.get_rect(center = (85, 50)))
            panel_surface.blit(panel_title, panel_title.get_rect(center = (82, 47)))

            for rect, label in[(draw_offer_rect, "DRAW"), (home_button_rect, "HOME")]:
                local_rect = rect.move(-480, 0)
                hovered = rect.collidepoint(mx, my)
                colour = ((80, 100, 135) if hovered else (42, 42, 58))
                pygame.draw.rect(panel_surface, colour, local_rect, 0, 5)
                label_surf = pygame.font.Font("fonts/ThaleahFat.ttf", 32).render(label, True, (255, 255, 255))
                panel_surface.blit(label_surf, label_surf.get_rect(center = local_rect.center))
            canvas.blit(panel_surface, (int(menu_slide_x), 0))

    # draw cursor cross hair rn
    pygame.draw.line(canvas, (255, 255, 255), (mx, my - 4), (mx, my + 4), 1)
    pygame.draw.line(canvas, (255, 255, 255), (mx - 4, my), (mx + 4, my), 1)
    # want to make it like expand when hovering a piece or maybe hoding a piece or smthn

    pygame.transform.scale(canvas, (window_w, window_h), window)

    pygame.display.update()
    clock.tick(120)

pygame.quit()

