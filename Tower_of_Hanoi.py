import pygame
import sys
import math

# --- 초기 설정 ---
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("하노이의 탑 (Tower of Hanoi)")

# --- 색상 정의 ---
BG_TOP = (220, 230, 240)
BG_BOTTOM = (180, 200, 220)
WHITE = (255, 255, 255)
PEG_COLOR = (100, 149, 237)
BASE_COLOR = (80, 100, 150)

DISK_COLORS = [
    (255, 99, 71), (255, 165, 0), (255, 215, 0), (152, 251, 152),
    (100, 149, 237), (138, 43, 226), (238, 130, 238), (255, 192, 203),
    (192, 192, 192), (128, 128, 128)
]
BORDER_COLOR = (50, 50, 50)
TEXT_COLOR = (40, 40, 40)
BUTTON_COLOR = (240, 240, 240)
BUTTON_HOVER_COLOR = (200, 200, 200)
SUCCESS_COLOR = (60, 179, 113)

# 폰트 설정
try:
    font_name = 'malgungothic'
    ui_font = pygame.font.SysFont(font_name, 30)
    win_font = pygame.font.SysFont(font_name, 60)
    big_font = pygame.font.SysFont(font_name, 80)
    small_ui_font = pygame.font.SysFont(font_name, 24)
except pygame.error:
    font_name = None
    ui_font = pygame.font.Font(font_name, 30)
    win_font = pygame.font.Font(font_name, 60)
    big_font = pygame.font.Font(font_name, 80)
    small_ui_font = pygame.font.Font(font_name, 24)

# --- 버튼 사각형 정의 ---
menu_button_rect = pygame.Rect(SCREEN_WIDTH - 150, 25, 120, 45)
next_level_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 55)

popup_restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40, 200, 55)
popup_prev_level_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 30, 200, 55)
popup_resume_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 55)

# --- 전역 변수 선언 ---
towers, NUMBER_OF_DISKS = [], 0
selected_disk, source_peg_index, game_won, move_count = None, -1, False, 0
min_moves = 0  
show_menu_popup = False

peg_width, peg_height = 15, 280
peg_y = SCREEN_HEIGHT - 330
peg_positions = [SCREEN_WIDTH // 4, SCREEN_WIDTH // 2, SCREEN_WIDTH * 3 // 4]
base_height = 25
disk_height = 25
min_disk_width = 70
disk_width_increment = 22

# --- 함수 정의 ---

def reset_game(num_disks):
    global towers, NUMBER_OF_DISKS, selected_disk, source_peg_index, game_won, move_count, min_moves, show_menu_popup
    NUMBER_OF_DISKS = num_disks
    towers = [[], [], []]
    towers[0] = list(range(NUMBER_OF_DISKS, 0, -1))
    selected_disk, source_peg_index, game_won, move_count = None, -1, False, 0
    min_moves = 2**NUMBER_OF_DISKS - 1
    show_menu_popup = False

def show_start_screen():
    selected_disks = 4
    while True:
        for y in range(SCREEN_HEIGHT):
            color = [int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * y / SCREEN_HEIGHT) for i in range(3)]
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))

        title_text = win_font.render("하노이의 탑", True, TEXT_COLOR)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 80))
        prompt_text = ui_font.render("원반 개수를 선택하세요", True, TEXT_COLOR)
        screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, 200))
        disk_count_text = big_font.render(str(selected_disks), True, PEG_COLOR)
        screen.blit(disk_count_text, (SCREEN_WIDTH // 2 - disk_count_text.get_width() // 2, 270))
        instruction_text = ui_font.render("▲/▼ 로 조절, Enter 로 시작", True, TEXT_COLOR)
        screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 400))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: selected_disks = min(10, selected_disks + 1)
                elif event.key == pygame.K_DOWN: selected_disks = max(3, selected_disks - 1)
                elif event.key == pygame.K_RETURN: return selected_disks

def draw_game_elements():
    for y in range(SCREEN_HEIGHT):
        color = [int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * y / SCREEN_HEIGHT) for i in range(3)]
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))

    pygame.draw.rect(screen, BASE_COLOR, (50, peg_y + peg_height, SCREEN_WIDTH - 100, base_height))
    for x in peg_positions:
        pygame.draw.rect(screen, PEG_COLOR, (x - peg_width // 2, peg_y, peg_width, peg_height), 0, 5)
        pygame.draw.rect(screen, BORDER_COLOR, (x - peg_width // 2, peg_y, peg_width, peg_height), 2, 5)

    for peg_idx, peg in enumerate(towers):
        for disk_idx, disk_size in enumerate(peg):
            disk_width = min_disk_width + (disk_size - 1) * disk_width_increment
            disk_x = peg_positions[peg_idx] - disk_width // 2
            disk_y = (peg_y + peg_height) - (disk_idx + 1) * disk_height
            color = DISK_COLORS[(disk_size - 1) % len(DISK_COLORS)]
            pygame.draw.rect(screen, color, (disk_x, disk_y, disk_width, disk_height), 0, 8)
            pygame.draw.rect(screen, BORDER_COLOR, (disk_x, disk_y, disk_width, disk_height), 2, 8)
            
    if selected_disk is not None and not show_menu_popup and not game_won:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        disk_width = min_disk_width + (selected_disk - 1) * disk_width_increment
        color = DISK_COLORS[(selected_disk - 1) % len(DISK_COLORS)]
        pygame.draw.rect(screen, color, (mouse_x - disk_width // 2, mouse_y - disk_height // 2 - 10, disk_width, disk_height), 0, 8)
        pygame.draw.rect(screen, BORDER_COLOR, (mouse_x - disk_width // 2, mouse_y - disk_height // 2 - 10, disk_width, disk_height), 2, 8)

    move_text = ui_font.render(f"이동 횟수: {move_count}", True, TEXT_COLOR)
    screen.blit(move_text, (20, 25))

    mouse_pos = pygame.mouse.get_pos()
    button_color = BUTTON_HOVER_COLOR if menu_button_rect.collidepoint(mouse_pos) and not game_won else BUTTON_COLOR
    pygame.draw.rect(screen, button_color, menu_button_rect, 0, 10)
    pygame.draw.rect(screen, BORDER_COLOR, menu_button_rect, 2, 10)
    menu_text = ui_font.render("메뉴", True, TEXT_COLOR)
    screen.blit(menu_text, (menu_button_rect.centerx - menu_text.get_width() // 2, menu_button_rect.centery - menu_text.get_height() // 2))
    
    if show_menu_popup:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        popup_width, popup_height = 400, 400
        popup_rect = pygame.Rect(SCREEN_WIDTH // 2 - popup_width // 2, SCREEN_HEIGHT // 2 - popup_height // 2, popup_width, popup_height)
        pygame.draw.rect(screen, WHITE, popup_rect, 0, 15)
        pygame.draw.rect(screen, BORDER_COLOR, popup_rect, 3, 15)
        popup_title = win_font.render("메뉴", True, TEXT_COLOR)
        screen.blit(popup_title, (popup_rect.centerx - popup_title.get_width() // 2, popup_rect.top + 30))
        button_color = BUTTON_HOVER_COLOR if popup_restart_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, button_color, popup_restart_button_rect, 0, 10)
        pygame.draw.rect(screen, BORDER_COLOR, popup_restart_button_rect, 2, 10)
        restart_text = ui_font.render("다시하기", True, TEXT_COLOR)
        screen.blit(restart_text, (popup_restart_button_rect.centerx - restart_text.get_width() // 2, popup_restart_button_rect.centery - restart_text.get_height() // 2))
        button_color = BUTTON_HOVER_COLOR if popup_prev_level_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, button_color, popup_prev_level_button_rect, 0, 10)
        pygame.draw.rect(screen, BORDER_COLOR, popup_prev_level_button_rect, 2, 10)
        prev_text = ui_font.render("이전 단계", True, TEXT_COLOR)
        screen.blit(prev_text, (popup_prev_level_button_rect.centerx - prev_text.get_width() // 2, popup_prev_level_button_rect.centery - prev_text.get_height() // 2))
        button_color = BUTTON_HOVER_COLOR if popup_resume_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, button_color, popup_resume_button_rect, 0, 10)
        pygame.draw.rect(screen, BORDER_COLOR, popup_resume_button_rect, 2, 10)
        resume_text = ui_font.render("계속하기", True, TEXT_COLOR)
        screen.blit(resume_text, (popup_resume_button_rect.centerx - resume_text.get_width() // 2, popup_resume_button_rect.centery - resume_text.get_height() // 2))

    if game_won:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        win_text = win_font.render("SUCCESS!", True, SUCCESS_COLOR)
        screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 170))
        min_moves_text = small_ui_font.render(f"최소 이동: {min_moves}", True, WHITE)
        user_moves_text = small_ui_font.render(f"나의 이동: {move_count}", True, WHITE)
        screen.blit(min_moves_text, (SCREEN_WIDTH // 2 - min_moves_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
        screen.blit(user_moves_text, (SCREEN_WIDTH // 2 - user_moves_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
        button_color = BUTTON_HOVER_COLOR if next_level_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, button_color, next_level_button_rect, 0, 10)
        pygame.draw.rect(screen, BORDER_COLOR, next_level_button_rect, 2, 10)
        next_text = ui_font.render("다음 단계", True, TEXT_COLOR)
        screen.blit(next_text, (next_level_button_rect.centerx - next_text.get_width() // 2, next_level_button_rect.centery - next_text.get_height() // 2))

def get_peg_from_pos(pos):
    for i, peg_x in enumerate(peg_positions):
        if abs(pos[0] - peg_x) < 60: return i
    return None

def check_win_condition():
    return len(towers[1]) == NUMBER_OF_DISKS or len(towers[2]) == NUMBER_OF_DISKS

# --- 메인 로직 ---
if __name__ == "__main__":
    initial_disks = show_start_screen()
    reset_game(initial_disks)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            
            if show_menu_popup or game_won: 
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if game_won:
                        if next_level_button_rect.collidepoint(mouse_pos):
                            if NUMBER_OF_DISKS < 10: 
                                reset_game(NUMBER_OF_DISKS + 1)
                            else:
                                print("최대 원반 개수에 도달했습니다!")
                        continue
                    
                    if show_menu_popup:
                        if popup_restart_button_rect.collidepoint(mouse_pos):
                            reset_game(NUMBER_OF_DISKS)
                        elif popup_prev_level_button_rect.collidepoint(mouse_pos):
                            if NUMBER_OF_DISKS > 3:
                                reset_game(NUMBER_OF_DISKS - 1)
                            else:
                                print("더 이상 이전 단계로 갈 수 없습니다. (최소 3개)")
                        elif popup_resume_button_rect.collidepoint(mouse_pos):
                            show_menu_popup = False
                        continue
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        show_menu_popup = not show_menu_popup
                continue

            # --- 일반 게임 플레이 로직 ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                if menu_button_rect.collidepoint(mouse_pos):
                    show_menu_popup = True
                    continue

                clicked_peg_index = get_peg_from_pos(mouse_pos)
                if clicked_peg_index is not None:
                    if selected_disk is None:
                        if towers[clicked_peg_index]:
                            selected_disk = towers[clicked_peg_index].pop()
                            source_peg_index = clicked_peg_index
                    else:
                        # --- 🔄 여기가 수정된 로직입니다 ---
                        target_peg_index = clicked_peg_index
                        target_peg = towers[target_peg_index]

                        # 조건 1: 다른 기둥으로 옮기는가?
                        is_different_peg = (target_peg_index != source_peg_index)
                        # 조건 2: 규칙에 맞는 위치인가? (빈 곳 또는 더 큰 원반 위)
                        is_valid_placement = (not target_peg or selected_disk < target_peg[-1])

                        # 두 조건이 모두 참일 때만 이동 횟수 증가
                        if is_different_peg and is_valid_placement:
                            target_peg.append(selected_disk)
                            move_count += 1
                            if check_win_condition(): game_won = True
                        else:
                            # 같은 위치에 놓거나 규칙에 어긋나면 원래 자리로 복귀 (횟수 증가 없음)
                            towers[source_peg_index].append(selected_disk)
                        
                        selected_disk = None # 손에 든 원반 비우기
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    show_menu_popup = not show_menu_popup

        draw_game_elements()
        pygame.display.flip()

    pygame.quit()
    sys.exit()
