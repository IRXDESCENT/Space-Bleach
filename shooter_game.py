from random import randint

import pygame

# Константы
WIDTH = 1024
HEIGHT = 720
TICKRATE = (150)
RED = (225, 0, 0)
AZURE = (0, 127, 255)

# Инициализация библиотеки
pygame.init()

# Создание окна
window = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Space Bleach")

# Игровые часы
clock = pygame.time.Clock()

# Базовый класс спрайта

class Sprite(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, speed, image, cd):
        super().__init__()
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (w, h))
        self.rect = self.image.get_rect(center = (x,y))
        self.speed = speed
        self.cd = cd
        self.base_cd = cd

    # Отрисовка спрайта
    def draw(self):
        window.blit(self.image, self.rect.topleft)

class Player(Sprite):
    def update(self, events):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.centerx -= self.speed
        
        if keys[pygame.K_d] and self.rect.right < WIDTH:
            self.rect.centerx += self.speed

        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.centery -= self.speed
        
        if keys[pygame.K_s] and self.rect.bottom < HEIGHT:
            self.rect.centery += self.speed

        if self.cd > 0:
            self.cd -= 1

        for e in events: 
            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.cd == 0: 
                    self.cd = self.base_cd
                    laser_sound.play()
                    lasers.add(Laser(self.rect.centerx, self.rect.top, -10))

class Enemy(Sprite):
    def update(self):
        self.rect.centery += self.speed

        if self.rect.top > HEIGHT:
            self.kill()


class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((3, 15))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center = (x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT or self.rect.bottom < 0:
            self.kill()

    def draw(self):
        window.blit(self.image, self.rect.topleft)

class GameManager():
    def __init__(self):
        self.state = "play"
        self.score = 0
        self.score_font = pygame.font.SysFont("consolas", 30)
        self.score_text = self.score_font.render("0", True, AZURE)

    def show_score(self):
        window.blit(self.score_text, (10, 10))

    def update_score(self):
        self.score += 1
        self.score_text = self.score_font.render(str(self.score), True, AZURE)

    def restart(self):
        self.state = "play"
        self.score = 0
        self.score_text = self.score_font.render("0", True, AZURE)
        player.rect.center = (WIDTH // 2, HEIGHT - 100)
        for e in enemies:
            e.kill()
    
    def update(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE and self.state == "game_over":
                    self.restart()

game = GameManager()

# Спрайты
player = Player(WIDTH // 2, HEIGHT - 100, 60, 80, 5, "rocket.png", TICKRATE // 3)

enemies = pygame.sprite.Group()
enemy_spawn_cd = TICKRATE

# Задний фон
background = pygame.image.load("galaxy.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

my_font = pygame.font.SysFont("Arial", 70)
game_over_text = my_font.render("Game over", True, AZURE)

my_font = pygame.font.SysFont("Arial", 45)
restart_text = my_font.render("Press any key to restart", True, AZURE)

pygame.mixer.init()

laser_sound = pygame.mixer.Sound("fire.ogg")
laser_sound.set_volume(0.2)

lasers = pygame.sprite.Group()

# Управляющая переменная
run = True

# Игровой цикл 
while run:
    events = pygame.event.get()
    # Перебор событий
    for e in events:
        if e.type == pygame.QUIT:
            run = False
        
        if e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:
                laser_sound.play()

    game.update(events)                

    if game.state == "play":

        # Отрисовка фона
        window.blit(background, (0,0))

        if enemy_spawn_cd == 0:
            enemy_spawn_cd = TICKRATE
            enemies.add(Enemy(randint(100, WIDTH - 100), -100, 100, 100, 3, "ufo.png", TICKRATE // 3))
        else:
            enemy_spawn_cd -= 1

        # Обновление спрайтов
        game.update(events)
        player.update(events)
        lasers.update()
        enemies.update()

        # Отрисовка игрока
        player.draw()
        lasers.draw(window)
        enemies.draw(window)
        game.show_score()

        if pygame.sprite.spritecollideany(player, enemies):
            game.state = "game_over"

        shots = pygame.sprite.groupcollide(lasers, enemies, True, True)

        if len(shots) > 0:
            game.update_score()

    if game.state == "game_over":
        window.blit(background, (0, 0))
        window.blit(game_over_text, (WIDTH // 4, (HEIGHT // 2) - 70 ))
        window.blit(restart_text, (WIDTH // 5, (HEIGHT // 2) + 90 ))

    # Обновление игры
    pygame.display.flip()

    # Тикрейт
    clock.tick(TICKRATE)
    