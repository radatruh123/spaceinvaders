import pygame
import sys
import random
import time
import math

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()

# ===== BARVY =====
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# ===== FONTY =====
font = pygame.font.Font(None, 32)
big_font = pygame.font.Font(None, 72)

# ===== STAVY =====
MENU = "menu"
SETTINGS = "settings"
GAME = "game"
PAUSE = "pause"
state = MENU

# ===== OBRÁZKY =====
player_img = pygame.transform.scale(
    pygame.image.load("player.png").convert_alpha(), (50, 40)
)
enemy_img = pygame.transform.scale(
    pygame.image.load("enemy.png").convert_alpha(), (45, 35)
)
meteor_img = pygame.image.load("meteor.png").convert_alpha()
base_img = pygame.transform.scale(
    pygame.image.load("base.png").convert_alpha(), (300, 60)
)

# ===== MENU =====
menu_items = ["Start", "Settings", "Quit"]
menu_rects = []

# ===== HRÁČ =====
player = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 120, 50, 40)
player_speed = 6
player_bullets = []
lives = 3

# ===== ZÁKLADNA =====
base_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT - 70, 300, 60)
base_hp = 5

# ===== SCORE & TIME =====
score = 0
start_time = 0

# ===== PAUSE =====
pause_button = pygame.Rect(10, 10, 100, 40)
countdown_start = None

# ===== NEPŘÁTELÉ =====
class Enemy:
    def __init__(self):
        self.rect = pygame.Rect(
            random.randint(50, WIDTH - 90), -40, 45, 35
        )
        self.hp = random.choice([1, 2])
        self.dir = random.choice([-1, 1])
        self.speed = 2

    def move(self):
        self.rect.y += self.speed
        self.rect.x += self.dir
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.dir *= -1

    def shoot(self):
        return pygame.Rect(self.rect.centerx - 2, self.rect.bottom, 4, 10)

enemies = []
enemy_bullets = []

# ===== METEORITY =====
class Meteor:
    def __init__(self, x, y, size, vx):
        self.size = size
        self.radius = size * 18
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = 2 + (3 - size)

    def move(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self):
        img = pygame.transform.scale(
            meteor_img,
            (self.radius * 2, self.radius * 2)
        )
        screen.blit(img, (self.x - self.radius, self.y - self.radius))

meteors = []

def spawn_meteor():
    size = random.choice([2, 3])
    x = random.randint(50, WIDTH - 50)
    meteors.append(Meteor(x, -50, size, random.choice([-1, 1])))

# ===== FUNKCE =====
def draw_hearts():
    for i in range(lives):
        pygame.draw.circle(screen, RED, (30 + i * 30, HEIGHT - 30), 10)

def reset_game():
    global lives, score, start_time, base_hp
    lives = 3
    base_hp = 5
    score = 0
    start_time = time.time()
    enemies.clear()
    meteors.clear()
    player_bullets.clear()
    enemy_bullets.clear()

# ===== HLAVNÍ SMYČKA =====
enemy_timer = 0
meteor_timer = 0
running = True

while running:
    dt = clock.tick(60)
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == GAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player_bullets.append(
                        pygame.Rect(player.centerx - 3, player.top, 6, 12)
                    )
                if event.key == pygame.K_ESCAPE:
                    state = PAUSE

            if event.type == pygame.MOUSEBUTTONDOWN:
                if pause_button.collidepoint(event.pos):
                    state = PAUSE

        elif state == PAUSE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    countdown_start = time.time()
                if event.key == pygame.K_m:
                    state = MENU

    # ===== MENU =====
    if state == MENU:
        title = big_font.render("SPACE INVADERS", True, GREEN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))

        menu_rects.clear()
        for i, item in enumerate(menu_items):
            text = font.render(item, True, WHITE)
            rect = text.get_rect(center=(WIDTH//2, 300 + i*60))
            screen.blit(text, rect)
            menu_rects.append((item, rect))

        if pygame.mouse.get_pressed()[0]:
            for item, rect in menu_rects:
                if rect.collidepoint(pygame.mouse.get_pos()):
                    if item == "Start":
                        reset_game()
                        state = GAME
                    elif item == "Settings":
                        state = SETTINGS
                    elif item == "Quit":
                        pygame.quit()
                        sys.exit()

    # ===== SETTINGS =====
    elif state == SETTINGS:
        text = big_font.render("SETTINGS", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))
        screen.blit(font.render("ESC - Back", True, WHITE),
                    (WIDTH//2 - 60, 300))
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            state = MENU

    # ===== GAME =====
    elif state == GAME:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: player.x -= player_speed
        if keys[pygame.K_d]: player.x += player_speed
        if keys[pygame.K_w]: player.y -= player_speed
        if keys[pygame.K_s]: player.y += player_speed
        player.clamp_ip(screen.get_rect())

        enemy_timer += dt
        meteor_timer += dt

        if enemy_timer > 1500:
            enemies.append(Enemy())
            enemy_timer = 0

        if meteor_timer > 3000:
            spawn_meteor()
            meteor_timer = 0

        for e in enemies[:]:
            e.move()
            if random.randint(0, 120) == 1:
                enemy_bullets.append(e.shoot())
            if e.rect.colliderect(base_rect):
                enemies.remove(e)
                base_hp -= 1

        for m in meteors[:]:
            m.move()
            if base_rect.collidepoint(m.x, m.y):
                meteors.remove(m)
                base_hp -= 1

        for b in player_bullets[:]:
            b.y -= 8
            if b.bottom < 0:
                player_bullets.remove(b)

        for b in enemy_bullets[:]:
            b.y += 5
            if b.colliderect(player):
                enemy_bullets.remove(b)
                lives -= 1

        for b in player_bullets[:]:
            for e in enemies[:]:
                if b.colliderect(e.rect):
                    player_bullets.remove(b)
                    e.hp -= 1
                    if e.hp <= 0:
                        enemies.remove(e)
                        score += 15
                    break

            for m in meteors[:]:
                if math.hypot(b.centerx - m.x, b.centery - m.y) < m.radius:
                    player_bullets.remove(b)
                    meteors.remove(m)
                    score += 5
                    if m.size > 1:
                        meteors.append(Meteor(m.x, m.y, m.size-1, -3))
                        meteors.append(Meteor(m.x, m.y, m.size-1, 3))
                    break

        # ===== KRESLENÍ =====
        screen.blit(player_img, player)
        for e in enemies:
            screen.blit(enemy_img, e.rect)
        for m in meteors:
            m.draw()
        for b in player_bullets:
            pygame.draw.rect(screen, YELLOW, b)
        for b in enemy_bullets:
            pygame.draw.rect(screen, RED, b)

        screen.blit(base_img, base_rect)
        screen.blit(font.render(f"Base HP: {base_hp}", True, WHITE),
                    (base_rect.x, base_rect.y - 20))

        pygame.draw.rect(screen, GRAY, pause_button)
        screen.blit(font.render("PAUSE", True, BLACK), (18, 18))

        screen.blit(font.render(f"Score: {score}", True, WHITE),
                    (WIDTH - 160, 10))

        game_time = int(time.time() - start_time)
        screen.blit(font.render(f"Time: {game_time}s", True, WHITE),
                    (WIDTH//2 - 60, 10))

        draw_hearts()

        if lives <= 0 or base_hp <= 0:
            state = MENU

    # ===== PAUSE =====
    elif state == PAUSE:
        screen.blit(big_font.render("PAUSE", True, WHITE),
                    (WIDTH//2 - 100, 200))
        screen.blit(font.render("C - Continue", True, WHITE),
                    (WIDTH//2 - 80, 280))
        screen.blit(font.render("M - Main Menu", True, WHITE),
                    (WIDTH//2 - 100, 320))

        if countdown_start:
            remaining = 3 - int(time.time() - countdown_start)
            if remaining <= 0:
                countdown_start = None
                state = GAME
            else:
                screen.blit(big_font.render(str(remaining), True, RED),
                            (WIDTH//2 - 20, 380))

    pygame.display.flip()

pygame.quit()
sys.exit()
