import pygame
import random
import sys

# 初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("スペースインベーダー")

# 色の定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# プレイヤークラス
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 8

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

# 敵クラス
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 2
        self.direction = 1

    def update(self):
        self.rect.x += self.speed * self.direction

# 弾クラス
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# スプライトグループの作成
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# プレイヤーの作成
player = Player()
all_sprites.add(player)

# 敵の作成
for row in range(5):
    for column in range(8):
        enemy = Enemy(100 + column * 70, 50 + row * 50)
        all_sprites.add(enemy)
        enemies.add(enemy)

# ゲームループ
clock = pygame.time.Clock()
score = 0
game_over = False

while not game_over:
    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # 更新処理
    all_sprites.update()

    # 敵の移動方向の変更
    for enemy in enemies:
        if enemy.rect.right >= WIDTH or enemy.rect.left <= 0:
            for e in enemies:
                e.direction *= -1
                e.rect.y += 20
            break

    # 弾と敵の衝突判定
    hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
    for hit in hits:
        score += 10

    # 敵がプレイヤーに到達したらゲームオーバー
    for enemy in enemies:
        if enemy.rect.bottom >= HEIGHT - 30:
            game_over = True

    # 敵がすべていなくなったら勝利
    if len(enemies) == 0:
        font = pygame.font.SysFont(None, 74)
        text = font.render("You Win!", True, WHITE)
        screen.blit(text, (WIDTH//2 - 100, HEIGHT//2 - 30))
        pygame.display.flip()
        pygame.time.wait(2000)
        game_over = True

    # 描画処理
    screen.fill(BLACK)
    all_sprites.draw(screen)
    
    # スコア表示
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)

# ゲーム終了
pygame.quit()
sys.exit()
