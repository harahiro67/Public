import pygame
import sys
import random
import math

# 初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ウィザードリー風ダンジョン")

# 色の定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# フォント設定
font = pygame.font.SysFont(None, 36)

# ダンジョンマップ（0=通路、1=壁）
dungeon_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# プレイヤーの状態
player = {
    "x": 1,
    "y": 1,
    "direction": 0,  # 0=北, 1=東, 2=南, 3=西
    "hp": 100,
    "max_hp": 100,
    "level": 1,
    "exp": 0,
    "next_level": 100
}

# 敵の定義
enemies = [
    {"name": "スライム", "hp": 20, "attack": 5, "exp": 10},
    {"name": "ゴブリン", "hp": 30, "attack": 8, "exp": 15},
    {"name": "オーク", "hp": 50, "attack": 12, "exp": 25}
]

# 現在の敵（戦闘中のみ設定）
current_enemy = None
battle_mode = False
message = ""

# 方向キーの定義
DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # 北、東、南、西

# 3D表示用の設定
FOV = math.pi / 3  # 視野角
HALF_FOV = FOV / 2
NUM_RAYS = 120
MAX_DEPTH = 8
WALL_HEIGHT = 100

# ミニマップ設定
CELL_SIZE = 20
MAP_OFFSET_X = 600
MAP_OFFSET_Y = 400

def draw_minimap():
    """ミニマップを描画する"""
    for y in range(len(dungeon_map)):
        for x in range(len(dungeon_map[y])):
            rect = pygame.Rect(
                MAP_OFFSET_X + x * CELL_SIZE,
                MAP_OFFSET_Y + y * CELL_SIZE,
                CELL_SIZE - 1,
                CELL_SIZE - 1
            )
            color = BLACK if dungeon_map[y][x] == 1 else WHITE
            pygame.draw.rect(screen, color, rect)
    
    # プレイヤーの位置を表示
    player_x = MAP_OFFSET_X + player["x"] * CELL_SIZE + CELL_SIZE // 2
    player_y = MAP_OFFSET_Y + player["y"] * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(screen, RED, (player_x, player_y), 5)
    
    # プレイヤーの向きを表示
    dx, dy = DIRECTIONS[player["direction"]]
    end_x = player_x + dx * 10
    end_y = player_y + dy * 10
    pygame.draw.line(screen, GREEN, (player_x, player_y), (end_x, end_y), 2)

def cast_rays():
    """3D視点のレイキャスティング"""
    start_angle = player["direction"] * (math.pi / 2) - HALF_FOV
    
    for ray in range(NUM_RAYS):
        angle = start_angle + ray * FOV / NUM_RAYS
        
        # レイの方向ベクトル
        ray_dir_x = math.cos(angle)
        ray_dir_y = math.sin(angle)
        
        # レイの長さ
        distance = 0
        hit_wall = False
        
        while not hit_wall and distance < MAX_DEPTH:
            distance += 0.1
            
            # レイの先端の座標
            test_x = int(player["x"] + ray_dir_x * distance)
            test_y = int(player["y"] + ray_dir_y * distance)
            
            # マップ範囲外チェック
            if test_x < 0 or test_x >= len(dungeon_map[0]) or test_y < 0 or test_y >= len(dungeon_map):
                hit_wall = True
                distance = MAX_DEPTH
            # 壁にヒットしたかチェック
            elif dungeon_map[test_y][test_x] == 1:
                hit_wall = True
        
        # 壁の高さを計算
        ceiling = HEIGHT / 2 - HEIGHT / distance
        floor = HEIGHT - ceiling
        
        # 距離に応じて壁の色を暗くする
        wall_color = (
            min(255, max(0, 255 - distance * 30)),
            min(255, max(0, 255 - distance * 30)),
            min(255, max(0, 255 - distance * 30))
        )
        
        # 壁を描画
        wall_width = WIDTH // NUM_RAYS
        wall_rect = pygame.Rect(
            ray * wall_width,
            ceiling,
            wall_width,
            floor - ceiling
        )
        pygame.draw.rect(screen, wall_color, wall_rect)
        
        # 床を描画
        floor_rect = pygame.Rect(
            ray * wall_width,
            floor,
            wall_width,
            HEIGHT - floor
        )
        pygame.draw.rect(screen, DARK_GRAY, floor_rect)
        
        # 天井を描画
        ceiling_rect = pygame.Rect(
            ray * wall_width,
            0,
            wall_width,
            ceiling
        )
        pygame.draw.rect(screen, GRAY, ceiling_rect)

def move_player(dx, dy):
    """プレイヤーを移動する"""
    new_x = player["x"] + dx
    new_y = player["y"] + dy
    
    # 移動先が壁でなければ移動
    if 0 <= new_x < len(dungeon_map[0]) and 0 <= new_y < len(dungeon_map):
        if dungeon_map[new_y][new_x] == 0:
            player["x"] = new_x
            player["y"] = new_y
            # ランダムエンカウント
            if random.random() < 0.2:  # 20%の確率で敵に遭遇
                start_battle()

def rotate_player(direction):
    """プレイヤーの向きを変える"""
    player["direction"] = (player["direction"] + direction) % 4

def start_battle():
    """戦闘を開始する"""
    global battle_mode, current_enemy, message
    battle_mode = True
    enemy_type = random.choice(enemies)
    current_enemy = {
        "name": enemy_type["name"],
        "hp": enemy_type["hp"],
        "attack": enemy_type["attack"],
        "exp": enemy_type["exp"]
    }
    message = f"{current_enemy['name']}が現れた！"

def player_attack():
    """プレイヤーの攻撃"""
    global battle_mode, current_enemy, message
    
    damage = random.randint(5, 15) + player["level"] * 2
    current_enemy["hp"] -= damage
    message = f"あなたの攻撃！ {current_enemy['name']}に{damage}のダメージ！"
    
    if current_enemy["hp"] <= 0:
        player["exp"] += current_enemy["exp"]
        message = f"{current_enemy['name']}を倒した！ {current_enemy['exp']}の経験値を獲得！"
        
        # レベルアップチェック
        if player["exp"] >= player["next_level"]:
            player["level"] += 1
            player["max_hp"] += 20
            player["hp"] = player["max_hp"]
            player["next_level"] = int(player["next_level"] * 1.5)
            message += f" レベルアップ！ レベル{player['level']}になった！"
        
        battle_mode = False
        current_enemy = None
    else:
        # 敵の攻撃
        enemy_attack()

def enemy_attack():
    """敵の攻撃"""
    global message
    
    damage = random.randint(1, current_enemy["attack"])
    player["hp"] -= damage
    message += f"\n{current_enemy['name']}の攻撃！ あなたに{damage}のダメージ！"
    
    if player["hp"] <= 0:
        message += "\nあなたは倒れた... ゲームオーバー"

def draw_battle_screen():
    """戦闘画面を描画する"""
    # 背景
    screen.fill(BLACK)
    
    # 敵の表示
    enemy_text = font.render(f"{current_enemy['name']} HP: {current_enemy['hp']}", True, WHITE)
    screen.blit(enemy_text, (WIDTH // 2 - enemy_text.get_width() // 2, 100))
    
    # プレイヤーステータス
    player_text = font.render(f"あなた Lv.{player['level']} HP: {player['hp']}/{player['max_hp']}", True, WHITE)
    screen.blit(player_text, (WIDTH // 2 - player_text.get_width() // 2, HEIGHT - 150))
    
    # メッセージ
    lines = message.split('\n')
    for i, line in enumerate(lines):
        msg_text = font.render(line, True, WHITE)
        screen.blit(msg_text, (WIDTH // 2 - msg_text.get_width() // 2, 200 + i * 40))
    
    # コマンド
    attack_text = font.render("Aキー: 攻撃", True, WHITE)
    screen.blit(attack_text, (50, HEIGHT - 80))
    
    run_text = font.render("Rキー: 逃げる", True, WHITE)
    screen.blit(run_text, (50, HEIGHT - 40))

def draw_status_bar():
    """ステータスバーを描画する"""
    # HPバー
    hp_percent = player["hp"] / player["max_hp"]
    hp_bar_width = 150 * hp_percent
    pygame.draw.rect(screen, RED, (20, 20, hp_bar_width, 20))
    pygame.draw.rect(screen, WHITE, (20, 20, 150, 20), 2)
    
    hp_text = font.render(f"HP: {player['hp']}/{player['max_hp']}", True, WHITE)
    screen.blit(hp_text, (180, 20))
    
    # レベルと経験値
    level_text = font.render(f"Lv: {player['level']} EXP: {player['exp']}/{player['next_level']}", True, WHITE)
    screen.blit(level_text, (20, 50))

# ゲームループ
clock = pygame.time.Clock()
running = True

while running:
    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if battle_mode:
                if event.key == pygame.K_a:  # 攻撃
                    player_attack()
                elif event.key == pygame.K_r:  # 逃げる
                    if random.random() < 0.5:  # 50%の確率で逃げられる
                        battle_mode = False
                        message = "うまく逃げ出した！"
                    else:
                        message = "逃げられない！"
                        enemy_attack()
            else:
                if event.key == pygame.K_UP:  # 前進
                    dx, dy = DIRECTIONS[player["direction"]]
                    move_player(dx, dy)
                elif event.key == pygame.K_DOWN:  # 後退
                    dx, dy = DIRECTIONS[player["direction"]]
                    move_player(-dx, -dy)
                elif event.key == pygame.K_LEFT:  # 左回転
                    rotate_player(-1)
                elif event.key == pygame.K_RIGHT:  # 右回転
                    rotate_player(1)
    
    # 描画処理
    screen.fill(BLACK)
    
    if battle_mode:
        draw_battle_screen()
    else:
        # 3D視点の描画
        cast_rays()
        
        # ミニマップの描画
        draw_minimap()
        
        # ステータスバーの描画
        draw_status_bar()
        
        # メッセージがあれば表示
        if message:
            msg_text = font.render(message, True, WHITE)
            screen.blit(msg_text, (WIDTH // 2 - msg_text.get_width() // 2, HEIGHT - 50))
    
    pygame.display.flip()
    clock.tick(30)

# ゲーム終了
pygame.quit()
sys.exit()