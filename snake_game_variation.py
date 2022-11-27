import pygame
import os
import sys
import random
from time import sleep

# 게임 스크린 전역변수
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 700

# 게임 화면 전역변수
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH / GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT / GRID_SIZE

# 방향 전역변수
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# 색상 전역변수
WHITE = (255, 255, 255)
ORANGE = (250, 150, 0)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# 뱀 객체
class Snake(object):
    def __init__(self):
        self.best_length = 2
        self.create()

    # 뱀 생성
    def create(self):
        self.died = False
        x = GRID_WIDTH//2
        y = GRID_HEIGHT//2
        self.length = 2
        self.positions = [(int(x*GRID_SIZE ), int(y*GRID_SIZE))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

    # 뱀 방향 조정
    def control(self, xy):
        if (xy[0] * -1, xy[1] * -1) == self.direction:
            return
        else:
            self.direction = xy

    # 뱀 이동
    def move(self):
        cur = self.positions[0]
        x, y = self.direction
        new = (cur[0] + (x * GRID_SIZE)), (cur[1] + (y * GRID_SIZE))

        # 뱀이 자기 몸통에 닿았을 경우 뱀 처음부터 다시 생성
        if new in self.positions[2:]:
            sleep(1)
            self.create()
            self.died = True
        # 뱀이 게임화면을 넘어갈 경우 뱀 처음부터 다시 생성
        elif new[0] < 0 or new[0] >= SCREEN_WIDTH or \
                new[1] < 0 or new[1] >= SCREEN_HEIGHT:
            sleep(1)
            self.create()
            self.died = True
        # 뱀이 정상적으로 이동하는 경우
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()

    # 뱀이 먹이를 먹을 때 호출
    def eat(self):
        self.length += 1
        if self.length > self.best_length:
            self.best_length = self.length

    # 뱀 그리기
    def draw(self, screen):
        red, green, blue = 50 / (self.length - 1), 150, 150 / (self.length - 1)
        for i, p in enumerate(self.positions):
            color = (100 + red * i, green, blue * i)
            rect = pygame.Rect((p[0], p[1]), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, color, rect)


# 먹이 객체
class Feed(object):
    def __init__(self):
        self.positions = []
        self.colors = [ORANGE]
        self.last_color = ORANGE
        self.last_speed = 0
        self.extra_speed = 0
        self.n = 3
        self.create()
        
    # 먹이 생성
    def create(self):
        for i in range(self.n):
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            self.extra_speed = self.last_speed
            self.positions.append((x * GRID_SIZE, y * GRID_SIZE))
            self.n = 1

    # 먹이 그리기
    def draw(self, screen):
        for i in range(len(self.positions)):
            rect = pygame.Rect((self.positions[i][0], self.positions[i][1]), (GRID_SIZE, GRID_SIZE))
            self.colors.append(random.choice([ORANGE, ORANGE, ORANGE, RED, GREEN]))
            pygame.draw.rect(screen, self.colors[i], rect)


    # 먹이가 파란색 혹은 초록색이면 추가적인 속도 반환
    def extraSpeed(self):
        self.extra_speed = self.last_speed
        if self.last_color == RED:
            self.extra_speed += 2
        elif self.last_color == GREEN:
            self.extra_speed -= 2
        elif self.last_color == 0:
            self.extra_speed = 0
        return self.extra_speed
                



# 게임 객체
class Game(object):
    def __init__(self, sound):
        self.snake = Snake()
        self.feed = Feed()
        self.speed = 5
        self.original_speed = 5
        self.sound = sound
        self.level = 1

    # 게임 이벤트 처리 및 조작
    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snake.control(UP)
                elif event.key == pygame.K_DOWN:
                    self.snake.control(DOWN)
                elif event.key == pygame.K_LEFT:
                    self.snake.control(LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.snake.control(RIGHT)
        return False

    # 게임 로직 수행
    def run_logic(self):
        self.snake.move()
        self.if_died_init_setting()
        self.check_eat(self.snake, self.feed)
        self.speed = (20 + self.snake.length) / 4 + self.feed.extraSpeed()
        self.original_speed = (20 + self.snake.length) / 4
        self.create_feed(self.snake, self.feed)

    # 뱀이 먹이를 먹었는지 확인
    def check_eat(self, snake, feed):
        if snake.positions[0] in feed.positions:
            snake.eat()
            self.sound.play()
            index = feed.positions.index(snake.positions[0])
            feed.last_color = feed.colors[index]
            feed.last_speed = feed.extra_speed
    
    # 뱀이 먹이를 먹었으면 새로운 위치에 먹이 생성        
    def create_feed(self, snake, feed):
        if snake.positions[0] in feed.positions:
            self.check_level()
            index = feed.positions.index(snake.positions[0])
            feed.positions.remove(snake.positions[0])
            feed.colors.pop(index)
            feed.create()

    # 뱀이 죽으면 추가 속도 설정을 초기화
    def if_died_init_setting(self):
        if self.snake.died:
            self.feed.last_color = 0
            self.snake.died = False
            self.feed.positions = []
            self.level = 1
            self.feed.n = 3
            self.feed.create()

    # 게임 레벨 확인
    def check_level(self):
        self.last_level = self.level
        self.level = self.snake.length//10 + 1
        if self.last_level < self.level:
            self.feed.n = 3

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    # 게임 정보 출력
    def draw_info(self, level, length, speed, screen, best_length):
        # 레벨, 길이, 속도, 추가 속도
        info = "Level " + str(level) + "    " + "Length: " + str(length) + "    " +\
                "Speed: " + str(round(speed, 2)) + " + " + str(round(self.feed.extraSpeed(), 2))
        font_path = resource_path("assets/NanumGothicCoding-Bold.ttf")
        font = pygame.font.Font(font_path, 26)
        text_obj = font.render(info, 1, GRAY)
        text_rect = text_obj.get_rect()
        text_rect.x, text_rect.y = 10, 10
        screen.blit(text_obj, text_rect)
        
        # 최고 기록
        info2 = 'Best Lenght: ' + str(best_length) 
        if self.snake.length == self.snake.best_length:
            font_color = RED
        else:
            font_color = GRAY
        text_obj2 = font.render(info2, 1, font_color)
        text_rect2 = text_obj2.get_rect()
        text_rect2.x, text_rect2.y = SCREEN_WIDTH-250, 10
        screen.blit(text_obj2, text_rect2)

        # 아이콘


    # 게임 프레임 처리
    def display_frame(self, screen):
        screen.fill(WHITE)
        self.draw_info(self.level, self.snake.length, self.original_speed, screen, self.snake.best_length)
        self.snake.draw(screen)
        self.feed.draw(screen)
        screen.blit(screen, (0, 0))

# 리소스 경로 설정
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def main():
    # 게임 초기화 및 환경 설정
    pygame.init()
    pygame.display.set_caption('Snake Game')
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    current_path = os.path.dirname(__file__)
    assets_path = os.path.join(current_path, 'assets')
    pygame.mixer.music.load(os.path.join(assets_path, '8bit_music.mp3'))
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.2)
    sound = pygame.mixer.Sound(os.path.join(assets_path, 'sound.mp3'))
    sound.set_volume(0.2)
    game = Game(sound)

    done = False
    while not done:
        done = game.process_events()
        game.run_logic()
        game.display_frame(screen)
        pygame.display.flip()
        clock.tick(game.speed)

    pygame.quit()


if __name__ == '__main__':
    main()
