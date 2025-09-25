import pygame
import sys

# --- 초기 설정 ---
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
# 폰트 미리 로드
try:
    FONT_NAME = 'malgungothic'
    UI_FONT = pygame.font.SysFont(FONT_NAME, 30)
    WIN_FONT = pygame.font.SysFont(FONT_NAME, 60)
    BIG_FONT = pygame.font.SysFont(FONT_NAME, 80)
    SMALL_UI_FONT = pygame.font.SysFont(FONT_NAME, 24)
except pygame.error:
    FONT_NAME = None
    UI_FONT = pygame.font.Font(FONT_NAME, 30)
    WIN_FONT = pygame.font.Font(FONT_NAME, 60)
    BIG_FONT = pygame.font.Font(FONT_NAME, 80)
    SMALL_UI_FONT = pygame.font.Font(FONT_NAME, 24)

# --- 색상 정의 ---
BG_TOP, BG_BOTTOM = (220, 230, 240), (180, 200, 220)
WHITE, TEXT_COLOR = (255, 255, 255), (40, 40, 40)
PEG_COLOR, BASE_COLOR = (100, 149, 237), (80, 100, 150)
BORDER_COLOR = (50, 50, 50)
BUTTON_COLOR, BUTTON_HOVER_COLOR = (240, 240, 240), (200, 200, 200)
SUCCESS_COLOR = (60, 179, 113)
DISK_COLORS = [
    (255, 99, 71), (255, 165, 0), (255, 215, 0), (152, 251, 152),
    (100, 149, 237), (138, 43, 226), (238, 130, 238), (255, 192, 203),
    (192, 192, 192), (128, 128, 128)
]

# --- 재사용 가능한 버튼 클래스 ---
class Button:
    """UI 버튼의 생성, 그리기, 이벤트 처리를 담당하는 클래스"""
    def __init__(self, rect, text, font):
        """버튼 객체를 초기화합니다."""
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.is_hovered = False

    def draw(self, surface):
        """버튼을 화면에 그립니다."""
        color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, 0, 10)
        pygame.draw.rect(surface, BORDER_COLOR, self.rect, 2, 10)
        
        text_surf = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        """마우스 커서가 버튼 위에 있는지 확인합니다."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        """버튼 클릭 이벤트를 감지합니다."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            return True
        return False

# --- 게임 관리 클래스 ---
class Game:
    """게임의 전체적인 상태와 로직을 관리하는 메인 클래스"""
    def __init__(self, surface):
        """게임 객체를 초기화하고 기본 설정들을 구성합니다."""
        self.screen = surface
        self.clock = pygame.time.Clock()
        self.game_state = 'start' # 게임 상태: start, playing, menu, won
        
        self.towers = []
        self.num_disks = 4
        self.selected_disk = None
        self.source_peg_index = -1
        self.move_count = 0
        self.min_moves = 0

        self.create_buttons()
        self.pre_render_background()
        self.pre_render_overlay()

    def create_buttons(self):
        """게임에 사용될 모든 버튼 객체를 생성합니다."""
        self.menu_button = Button((SCREEN_WIDTH - 150, 25, 120, 45), "메뉴", UI_FONT)
        self.next_level_button = Button((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 55), "다음 단계", UI_FONT)
        self.popup_restart_button = Button((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40, 200, 55), "다시하기", UI_FONT)
        self.popup_prev_level_button = Button((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 30, 200, 55), "이전 단계", UI_FONT)
        self.popup_resume_button = Button((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 55), "계속하기", UI_FONT)

    def pre_render_background(self):
        """성능 최적화를 위해 배경 그라데이션을 미리 그려둡니다."""
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            color = [int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * y / SCREEN_HEIGHT) for i in range(3)]
            pygame.draw.line(self.background, color, (0, y), (SCREEN_WIDTH, y))

    def pre_render_overlay(self):
        """성능 최적화를 위해 반투명 오버레이를 미리 만들어둡니다."""
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 150))
    
    def reset(self, num_disks):
        """게임을 특정 원반 개수로 초기화하거나 재시작합니다."""
        self.num_disks = num_disks
        self.towers = [[], [], []]
        self.towers[0] = list(range(self.num_disks, 0, -1))
        self.selected_disk = None
        self.source_peg_index = -1
        self.move_count = 0
        self.min_moves = 2**self.num_disks - 1
        self.game_state = 'playing'

    def run(self):
        """게임의 메인 루프를 실행합니다."""
        while True:
            self.handle_events() # 사용자 입력 처리
            self.draw()          # 화면 그리기
            self.clock.tick(60)  # 초당 60프레임으로 제한

    def handle_events(self):
        """모든 사용자 입력을 감지하고 상태에 맞게 처리합니다."""
        mouse_pos = pygame.mouse.get_pos()
        
        # 현재 게임 상태에 따라 버튼 호버 효과 처리
        if self.game_state == 'playing':
            self.menu_button.check_hover(mouse_pos)
        elif self.game_state == 'menu':
            self.popup_restart_button.check_hover(mouse_pos)
            self.popup_prev_level_button.check_hover(mouse_pos)
            self.popup_resume_button.check_hover(mouse_pos)
        elif self.game_state == 'won':
            self.next_level_button.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # 게임 상태에 따라 적절한 이벤트 핸들러 호출
            if self.game_state == 'start':
                self._handle_start_events(event)
            elif self.game_state == 'playing':
                self._handle_playing_events(event)
            elif self.game_state == 'menu':
                self._handle_menu_events(event)
            elif self.game_state == 'won':
                self._handle_won_events(event)

    def _handle_start_events(self, event):
        """시작 화면에서의 입력을 처리합니다."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP: self.num_disks = min(10, self.num_disks + 1)
            elif event.key == pygame.K_DOWN: self.num_disks = max(3, self.num_disks - 1)
            elif event.key == pygame.K_RETURN: self.reset(self.num_disks)
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0: self.num_disks = min(10, self.num_disks + 1)
            elif event.y < 0: self.num_disks = max(3, self.num_disks - 1)

    def _handle_playing_events(self, event):
        """게임 플레이 중의 입력을 처리합니다."""
        if self.menu_button.handle_event(event):
            self.game_state = 'menu'
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_state = 'menu'

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            peg_idx = self._get_peg_from_pos(event.pos)
            if peg_idx is not None:
                if self.selected_disk is None:
                    if self.towers[peg_idx]:
                        self.selected_disk = self.towers[peg_idx].pop()
                        self.source_peg_index = peg_idx
                else:
                    target_peg = self.towers[peg_idx]
                    is_diff_peg = (peg_idx != self.source_peg_index)
                    is_valid_place = (not target_peg or self.selected_disk < target_peg[-1])
                    
                    if is_diff_peg and is_valid_place:
                        target_peg.append(self.selected_disk)
                        self.move_count += 1
                        if len(self.towers[1]) == self.num_disks or len(self.towers[2]) == self.num_disks:
                            self.game_state = 'won'
                    else:
                        self.towers[self.source_peg_index].append(self.selected_disk)
                    self.selected_disk = None

    def _handle_menu_events(self, event):
        """메뉴 팝업이 활성화되었을 때의 입력을 처리합니다."""
        if self.popup_restart_button.handle_event(event):
            self.reset(self.num_disks)
        elif self.popup_prev_level_button.handle_event(event):
            if self.num_disks > 3: self.reset(self.num_disks - 1)
        elif self.popup_resume_button.handle_event(event):
            self.game_state = 'playing'
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_state = 'playing'

    def _handle_won_events(self, event):
        """게임 승리 화면에서의 입력을 처리합니다."""
        if self.next_level_button.handle_event(event):
            if self.num_disks < 10: self.reset(self.num_disks + 1)

    def draw(self):
        """게임 상태에 따라 적절한 화면을 그립니다."""
        if self.game_state == 'start':
            self._draw_start_screen()
        else:
            self._draw_gameplay_screen()
            if self.game_state == 'menu':
                self._draw_menu_popup()
            elif self.game_state == 'won':
                self._draw_win_screen()
        
        pygame.display.flip()

    def _draw_start_screen(self):
        """원반 개수를 선택하는 시작 화면을 그립니다."""
        self.screen.blit(self.background, (0, 0))
        title = WIN_FONT.render("하노이의 탑", True, TEXT_COLOR)
        prompt = UI_FONT.render("원반 개수를 선택하세요", True, TEXT_COLOR)
        count = BIG_FONT.render(str(self.num_disks), True, PEG_COLOR)
        instr = UI_FONT.render("▲/▼ 또는 마우스 휠로 조절, Enter 로 시작", True, TEXT_COLOR)
        
        self.screen.blit(title, title.get_rect(centerx=SCREEN_WIDTH/2, y=80))
        self.screen.blit(prompt, prompt.get_rect(centerx=SCREEN_WIDTH/2, y=200))
        self.screen.blit(count, count.get_rect(centerx=SCREEN_WIDTH/2, y=270))
        self.screen.blit(instr, instr.get_rect(centerx=SCREEN_WIDTH/2, y=400))
        
    def _draw_gameplay_screen(self):
        """기둥, 원반 등 메인 게임 화면을 그립니다."""
        self.screen.blit(self.background, (0, 0))
        peg_y, peg_height, base_height = 270, 280, 25
        pygame.draw.rect(self.screen, BASE_COLOR, (50, peg_y + peg_height, SCREEN_WIDTH - 100, base_height))
        peg_positions = [SCREEN_WIDTH // 4, SCREEN_WIDTH // 2, SCREEN_WIDTH * 3 // 4]
        for x in peg_positions:
            pygame.draw.rect(self.screen, PEG_COLOR, (x - 7.5, peg_y, 15, peg_height), 0, 5)
            pygame.draw.rect(self.screen, BORDER_COLOR, (x - 7.5, peg_y, 15, peg_height), 2, 5)

        disk_h, min_disk_w, disk_w_inc = 25, 70, 22
        for peg_idx, peg in enumerate(self.towers):
            for disk_idx, disk_size in enumerate(peg):
                width = min_disk_w + (disk_size - 1) * disk_w_inc
                x = peg_positions[peg_idx] - width // 2
                y = (peg_y + peg_height) - (disk_idx + 1) * disk_h
                color = DISK_COLORS[(disk_size - 1) % len(DISK_COLORS)]
                pygame.draw.rect(self.screen, color, (x, y, width, disk_h), 0, 8)
                pygame.draw.rect(self.screen, BORDER_COLOR, (x, y, width, disk_h), 2, 8)

        if self.selected_disk is not None:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            width = min_disk_w + (self.selected_disk - 1) * disk_w_inc
            color = DISK_COLORS[(self.selected_disk - 1) % len(DISK_COLORS)]
            pygame.draw.rect(self.screen, color, (mouse_x - width / 2, mouse_y - disk_h / 2 - 10, width, disk_h), 0, 8)
            pygame.draw.rect(self.screen, BORDER_COLOR, (mouse_x - width / 2, mouse_y - disk_h / 2 - 10, width, disk_h), 2, 8)

        moves_text = UI_FONT.render(f"이동 횟수: {self.move_count}", True, TEXT_COLOR)
        self.screen.blit(moves_text, (20, 25))
        self.menu_button.draw(self.screen)

    def _draw_menu_popup(self):
        """일시 정지 메뉴 팝업을 그립니다."""
        self.screen.blit(self.overlay, (0, 0))
        popup_rect = pygame.Rect(0, 0, 400, 400)
        popup_rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        pygame.draw.rect(self.screen, WHITE, popup_rect, 0, 15)
        pygame.draw.rect(self.screen, BORDER_COLOR, popup_rect, 3, 15)
        title = WIN_FONT.render("메뉴", True, TEXT_COLOR)
        self.screen.blit(title, title.get_rect(centerx=popup_rect.centerx, y=popup_rect.top + 30))
        self.popup_restart_button.draw(self.screen)
        self.popup_prev_level_button.draw(self.screen)
        self.popup_resume_button.draw(self.screen)
    
    def _draw_win_screen(self):
        """게임 성공 화면을 그립니다."""
        self.screen.blit(self.overlay, (0, 0))
        win_text = WIN_FONT.render("SUCCESS!", True, SUCCESS_COLOR)
        min_moves = SMALL_UI_FONT.render(f"최소 이동: {self.min_moves}", True, WHITE)
        user_moves = SMALL_UI_FONT.render(f"나의 이동: {self.move_count}", True, WHITE)

        self.screen.blit(win_text, win_text.get_rect(centerx=SCREEN_WIDTH/2, y=SCREEN_HEIGHT/2 - 170))
        self.screen.blit(min_moves, min_moves.get_rect(centerx=SCREEN_WIDTH/2, y=SCREEN_HEIGHT/2 - 60))
        self.screen.blit(user_moves, user_moves.get_rect(centerx=SCREEN_WIDTH/2, y=SCREEN_HEIGHT/2 - 20))
        self.next_level_button.draw(self.screen)

    def _get_peg_from_pos(self, pos):
        """마우스 좌표로부터 클릭된 기둥의 인덱스를 반환합니다."""
        for i, peg_x in enumerate([SCREEN_WIDTH // 4, SCREEN_WIDTH // 2, SCREEN_WIDTH * 3 // 4]):
            if abs(pos[0] - peg_x) < 60: return i
        return None

# --- 메인 실행 ---
if __name__ == "__main__":
    """프로그램이 직접 실행될 때 호출되는 부분입니다."""
    game_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game = Game(game_surface) # Game 객체 생성
    game.run() # 게임 실행
