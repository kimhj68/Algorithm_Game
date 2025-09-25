import pygame
import sys
from collections import deque
import random

# --- 초기화 ---
pygame.init()

# --- 상수 정의 ---
# 화면 크기
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700
HEADER_HEIGHT = 100

# 보드 크기 및 셀 크기
BOARD_ROWS = 3
BOARD_COLS = 3
CELL_SIZE = SCREEN_WIDTH // BOARD_COLS

# 색상 (깔끔한 테마로 변경)
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
WHITE = (255, 255, 255)
X_COLOR = (84, 84, 84)
O_COLOR = (242, 235, 211)
BUTTON_COLOR = (220, 220, 220)
BUTTON_TEXT_COLOR = (50, 50, 50)


# 선 두께
LINE_WIDTH = 15
MARKER_WIDTH = 15
WIN_LINE_WIDTH = 10

# --- 화면 설정 ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Pygame 순환 틱택토')

# --- 폰트 설정 ---
font = pygame.font.SysFont("malgun gothic", 50, bold=True)
button_font = pygame.font.SysFont("malgun gothic", 40)
small_font = pygame.font.SysFont("malgun gothic", 30)

# --- 게임 변수 ---
board = [[0] * BOARD_COLS for _ in range(BOARD_ROWS)] # 0: 빈 칸, 1: 플레이어 1(X), -1: 플레이어 2(O)
player = random.choice([1, -1])  # 시작 플레이어를 랜덤으로 설정
winner = 0  # 0: 게임 중, 1: 플레이어 1 승, -1: 플레이어 2 승
game_over = False
win_line_info = None

# 새로운 규칙: 각 플레이어의 말 위치를 순서대로 저장 (최대 3개)
player_moves = {1: deque(), -1: deque()} # 1: X, -1: O

# '다시 시작' 버튼 Rect
button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 125, SCREEN_HEIGHT // 2 - 25, 250, 60)


# --- 함수 정의 ---

def draw_grid():
    """격자무늬를 그리는 함수"""
    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, LINE_COLOR, (0, 0, SCREEN_WIDTH, HEADER_HEIGHT))
    for i in range(1, BOARD_ROWS):
        pygame.draw.line(screen, LINE_COLOR, (0, i * CELL_SIZE + HEADER_HEIGHT), (SCREEN_WIDTH, i * CELL_SIZE + HEADER_HEIGHT), LINE_WIDTH)
    for i in range(1, BOARD_COLS):
        pygame.draw.line(screen, LINE_COLOR, (i * CELL_SIZE, HEADER_HEIGHT), (i * CELL_SIZE, SCREEN_HEIGHT), LINE_WIDTH)

def draw_markers():
    """보드 상태에 따라 'O'와 'X'를 그리고, 사라질 말을 깜빡이는 함수"""
    
    # 현재 턴인 플레이어의 말이 3개일 경우, 가장 오래된 말을 찾음
    oldest_move = None
    if len(player_moves[player]) == 3 and not game_over:
        oldest_move = player_moves[player][0]

    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            is_oldest = (oldest_move is not None and oldest_move == (row, col))

            # 깜빡임 효과: is_oldest가 True일 때, 시간에 따라 그릴지 말지 결정
            if is_oldest and (pygame.time.get_ticks() // 400) % 2 == 0:
                continue # 이번 프레임에서는 그리지 않고 건너뜀

            y_pos = row * CELL_SIZE + HEADER_HEIGHT
            x_pos = col * CELL_SIZE

            if board[row][col] == 1: # 플레이어 1 (X)
                pygame.draw.line(screen, X_COLOR, (x_pos + 40, y_pos + 40), 
                                 (x_pos + CELL_SIZE - 40, y_pos + CELL_SIZE - 40), MARKER_WIDTH)
                pygame.draw.line(screen, X_COLOR, (x_pos + 40, y_pos + CELL_SIZE - 40), 
                                 (x_pos + CELL_SIZE - 40, y_pos + 40), MARKER_WIDTH)
            elif board[row][col] == -1: # 플레이어 2 (O)
                pygame.draw.circle(screen, O_COLOR, (x_pos + CELL_SIZE // 2, y_pos + CELL_SIZE // 2), CELL_SIZE // 2 - 40, MARKER_WIDTH)

def check_winner():
    """승리 조건을 확인하고 게임 상태를 업데이트하는 함수"""
    global winner, game_over, win_line_info
    
    # 가로 확인
    for i in range(BOARD_ROWS):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] != 0:
            winner = board[i][0]
            win_line_info = ('row', i)
            game_over = True
            return

    # 세로 확인
    for i in range(BOARD_COLS):
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] != 0:
            winner = board[0][i]
            win_line_info = ('col', i)
            game_over = True
            return

    # 대각선 확인 (왼쪽 위 -> 오른쪽 아래)
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != 0:
        winner = board[0][0]
        win_line_info = ('diag', 1)
        game_over = True
        return

    # 대각선 확인 (오른쪽 위 -> 왼쪽 아래)
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != 0:
        winner = board[0][2]
        win_line_info = ('diag', 2)
        game_over = True
        return

def draw_win_line(win_info):
    """승리 라인을 그리는 함수"""
    line_type, index = win_info
    win_color = X_COLOR if winner == 1 else O_COLOR
    
    if line_type == 'row':
        y_pos = index * CELL_SIZE + CELL_SIZE // 2 + HEADER_HEIGHT
        pygame.draw.line(screen, win_color, (15, y_pos), (SCREEN_WIDTH - 15, y_pos), WIN_LINE_WIDTH)
    elif line_type == 'col':
        x_pos = index * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.line(screen, win_color, (x_pos, HEADER_HEIGHT + 15), (x_pos, SCREEN_HEIGHT - 15), WIN_LINE_WIDTH)
    elif line_type == 'diag':
        if index == 1:
            pygame.draw.line(screen, win_color, (15, HEADER_HEIGHT + 15), (SCREEN_WIDTH - 15, SCREEN_HEIGHT - 15), WIN_LINE_WIDTH)
        else:
            pygame.draw.line(screen, win_color, (SCREEN_WIDTH - 15, HEADER_HEIGHT + 15), (15, SCREEN_HEIGHT - 15), WIN_LINE_WIDTH)

def draw_ui_elements():
    """상태 메시지와 UI 요소를 그리는 함수"""
    if game_over:
        message = f'플레이어 {"1 (X)" if winner == 1 else "2 (O)"} 승리!'
    else:
        current_player_marker = "X" if player == 1 else "O"
        message = f"플레이어 {current_player_marker} 턴 (말 {len(player_moves[player])}/3개)"

    text = font.render(message, True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, HEADER_HEIGHT // 2))
    screen.blit(text, text_rect)

    if game_over:
        pygame.draw.rect(screen, BUTTON_COLOR, button_rect, border_radius=10)
        btn_text = button_font.render('다시 시작', True, BUTTON_TEXT_COLOR)
        btn_text_rect = btn_text.get_rect(center=button_rect.center)
        screen.blit(btn_text, btn_text_rect)

def reset_game():
    """게임을 초기 상태로 리셋하는 함수"""
    global board, player, winner, game_over, win_line_info
    board = [[0] * BOARD_COLS for _ in range(BOARD_ROWS)]
    player = random.choice([1, -1]) # 재시작 시 플레이어를 랜덤으로 설정
    winner = 0
    game_over = False
    win_line_info = None
    player_moves[1].clear()
    player_moves[-1].clear()

# --- 메인 게임 루프 ---
running = True
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouseX, mouseY = event.pos
            
            if game_over:
                if button_rect.collidepoint(event.pos):
                    reset_game()
            else:
                if mouseY > HEADER_HEIGHT:
                    clicked_row = (mouseY - HEADER_HEIGHT) // CELL_SIZE
                    clicked_col = mouseX // CELL_SIZE

                    if board[clicked_row][clicked_col] == 0:
                        # 새로운 규칙 적용
                        current_player_moves = player_moves[player]

                        if len(current_player_moves) == 3:
                            oldest_move = current_player_moves.popleft()
                            old_row, old_col = oldest_move
                            board[old_row][old_col] = 0

                        board[clicked_row][clicked_col] = player
                        current_player_moves.append((clicked_row, clicked_col))
                        
                        check_winner()

                        if not game_over:
                            player *= -1

    draw_grid()
    draw_markers()
    if game_over and win_line_info:
        draw_win_line(win_line_info)
    draw_ui_elements()
    pygame.display.update()

pygame.quit()
sys.exit()

