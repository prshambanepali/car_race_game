import pygame
import math
import time
from game_important import scale_image, blit_rotate_center, control_of_player1, control_of_player2, blit_text_center

pygame.init()
pygame.font.init()

FINISH = pygame.image.load('imgs/finish.png')
FINISH_MASK = pygame.mask.from_surface(FINISH)
RED_CAR = scale_image(pygame.image.load('imgs/red-car.png'), 0.4)
GREEN_CAR = scale_image(pygame.image.load('imgs/green-car.png'), 0.4)
TRACK_BORDER = scale_image(pygame.image.load('imgs/bestest-track.png'), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
TRACK = scale_image(pygame.image.load('imgs/originaltrack.png'), 0.9)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
MAIN_FONT = pygame.font.SysFont("comicsans", 30)

def main():
    pygame.display.set_caption("2 Player Racing Game")

    images = [(TRACK, (0, 0)), (FINISH, (224, 785)), (TRACK_BORDER, (0, 0))]
    running = True
    player_car1 = Player_car1(4, 2)
    player_car2 = Player_car2(4, 2)
    game_info = Game_info()
    FPS = 60
    clock = pygame.time.Clock()

    while running:
        clock.tick(FPS)

        draw(WIN, images, player_car1, player_car2, game_info)

        while not game_info.started:
            blit_text_center(WIN, MAIN_FONT, f'Press any key to start level {game_info.level}')
            # print(pygame.mouse.get_pos())
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    game_info.start_level()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        control_of_player1(player_car1)
        control_of_player2(player_car2)

        handle_collision(player_car1, player_car2, game_info)

def draw(win, images, player_car1, player_car2, game_info):
    for img, pos in images:
        win.blit(img, pos)

    level_text = MAIN_FONT.render(f'Level - {game_info.level}', 1, (255, 255, 255))
    win.blit(level_text, (10, win.get_height() - 100))

    time_text = MAIN_FONT.render(f'Time - {round(game_info.game_level_time(), 1)}', 1, (255, 255, 255))
    win.blit(time_text, (10, win.get_height() - 70))

    player1_vel_text = MAIN_FONT.render(f'Player 1 - Vel: {round(player_car1.vel, 1)}', 1, (255, 255, 255))
    win.blit(player1_vel_text, (10, win.get_height() - 50))

    player2_vel_text = MAIN_FONT.render(f'Player 2 - Vel: {round(player_car2.vel, 1)}', 1, (255, 255, 255))
    win.blit(player2_vel_text, (500, win.get_height() - 50))

    player_car1.draw(win)
    player_car2.draw(win)

    pygame.display.update()

class AbstractCar:
    def __init__(self, max_vel, resolution_vel):
        self.vel = 0
        self.max_vel = max_vel
        self.angle = 270
        self.resolution_vel = resolution_vel
        self.img = self.IMG
        self.x, self.y = self.START_POS
        self.acceleration = 0.2

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.resolution_vel
        elif right:
            self.angle -= self.resolution_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backword(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel / 2)
        self.move()

    def move(self):
        theta = math.radians(self.angle)
        vertical = math.cos(theta) * self.vel
        horizontal = math.sin(theta) * self.vel
        self.y -= vertical
        self.x -= horizontal

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 4, 0)
        self.move()

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        point = mask.overlap(car_mask, offset)
        return point

    def reset(self):
        self.vel = 0
        self.angle = 270
        self.x, self.y = self.START_POS

    def bounce(self):
        self.vel = -self.vel / 4
        self.move()

class Player_car1(AbstractCar):
    IMG = RED_CAR
    START_POS = (380, 533)

class Player_car2(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (380, 558)

class Game_info:
    LEVELS = 8

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def game_level_time(self):
        if not self.started:
            return 0
        return time.time() - self.level_start_time

def handle_collision(player_car1, player_car2, game_info):
    if player_car1.collide(TRACK_BORDER_MASK):
        player_car1.bounce()

    if player_car2.collide(TRACK_BORDER_MASK):
        player_car2.bounce()

    finish_poi_1 = player_car1.collide(FINISH_MASK, 224, 785)
    if finish_poi_1:
        blit_text_center(WIN, MAIN_FONT, 'Player 1 Wins!')
        pygame.display.update()
        pygame.time.wait(3000)
        game_info.next_level()
        player_car1.reset()
        player_car2.reset()
        return

    finish_poi_2 = player_car2.collide(FINISH_MASK, 224, 785)
    if finish_poi_2:
        blit_text_center(WIN, MAIN_FONT, 'Player 2 Wins!')
        pygame.display.update()
        pygame.time.wait(3000)
        game_info.next_level()
        player_car1.reset()
        player_car2.reset()
        return

if __name__ == "__main__":
    main()

pygame.quit()
