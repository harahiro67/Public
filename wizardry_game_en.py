import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wizardry-style Dungeon")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)

# Font settings
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

# Dungeon map (0=corridor, 1=wall)
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

# Player state
player = {
    "x": 1,
    "y": 1,
    "direction": 0,  # 0=North, 1=East, 2=South, 3=West
    "hp": 100,
    "max_hp": 100,
    "mp": 50,
    "max_mp": 50,
    "level": 1,
    "exp": 0,
    "next_level": 100,
    "gold": 0
}

# Enemy definitions
enemies = [
    {"name": "Slime", "hp": 20, "attack": 5, "exp": 10, "gold": 5},
    {"name": "Goblin", "hp": 30, "attack": 8, "exp": 15, "gold": 10},
    {"name": "Orc", "hp": 50, "attack": 12, "exp": 25, "gold": 15},
    {"name": "Skeleton", "hp": 40, "attack": 10, "exp": 20, "gold": 12},
    {"name": "Dark Mage", "hp": 35, "attack": 15, "exp": 30, "gold": 20}
]

# Spells
spells = [
    {"name": "Fireball", "mp_cost": 10, "min_damage": 10, "max_damage": 20, "level_req": 1},
    {"name": "Ice Spike", "mp_cost": 15, "min_damage": 15, "max_damage": 25, "level_req": 2},
    {"name": "Lightning", "mp_cost": 20, "min_damage": 20, "max_damage": 35, "level_req": 3}
]

# Current enemy (only set during battle)
current_enemy = None
battle_mode = False
message = ""

# Direction definitions
DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # North, East, South, West

# 3D display settings
FOV = math.pi / 3  # Field of view
HALF_FOV = FOV / 2
NUM_RAYS = 120
MAX_DEPTH = 8
WALL_HEIGHT = 100

# Minimap settings
CELL_SIZE = 20
MAP_OFFSET_X = 600
MAP_OFFSET_Y = 400

def draw_minimap():
    """Draw the minimap"""
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
    
    # Show player position
    player_x = MAP_OFFSET_X + player["x"] * CELL_SIZE + CELL_SIZE // 2
    player_y = MAP_OFFSET_Y + player["y"] * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(screen, RED, (player_x, player_y), 5)
    
    # Show player direction
    dx, dy = DIRECTIONS[player["direction"]]
    end_x = player_x + dx * 10
    end_y = player_y + dy * 10
    pygame.draw.line(screen, GREEN, (player_x, player_y), (end_x, end_y), 2)

def cast_rays():
    """3D perspective ray casting"""
    start_angle = player["direction"] * (math.pi / 2) - HALF_FOV
    
    for ray in range(NUM_RAYS):
        angle = start_angle + ray * FOV / NUM_RAYS
        
        # Ray direction vector
        ray_dir_x = math.cos(angle)
        ray_dir_y = math.sin(angle)
        
        # Ray length
        distance = 0
        hit_wall = False
        
        while not hit_wall and distance < MAX_DEPTH:
            distance += 0.1
            
            # Ray endpoint coordinates
            test_x = int(player["x"] + ray_dir_x * distance)
            test_y = int(player["y"] + ray_dir_y * distance)
            
            # Check if out of map range
            if test_x < 0 or test_x >= len(dungeon_map[0]) or test_y < 0 or test_y >= len(dungeon_map):
                hit_wall = True
                distance = MAX_DEPTH
            # Check if hit wall
            elif dungeon_map[test_y][test_x] == 1:
                hit_wall = True
        
        # Calculate wall height
        ceiling = HEIGHT / 2 - HEIGHT / distance
        floor = HEIGHT - ceiling
        
        # Darken wall color based on distance
        wall_color = (
            min(255, max(0, 255 - distance * 30)),
            min(255, max(0, 255 - distance * 30)),
            min(255, max(0, 255 - distance * 30))
        )
        
        # Draw wall
        wall_width = WIDTH // NUM_RAYS
        wall_rect = pygame.Rect(
            ray * wall_width,
            ceiling,
            wall_width,
            floor - ceiling
        )
        pygame.draw.rect(screen, wall_color, wall_rect)
        
        # Draw floor
        floor_rect = pygame.Rect(
            ray * wall_width,
            floor,
            wall_width,
            HEIGHT - floor
        )
        pygame.draw.rect(screen, DARK_GRAY, floor_rect)
        
        # Draw ceiling
        ceiling_rect = pygame.Rect(
            ray * wall_width,
            0,
            wall_width,
            ceiling
        )
        pygame.draw.rect(screen, GRAY, ceiling_rect)

def move_player(dx, dy):
    """Move the player"""
    new_x = player["x"] + dx
    new_y = player["y"] + dy
    
    # Move if destination is not a wall
    if 0 <= new_x < len(dungeon_map[0]) and 0 <= new_y < len(dungeon_map):
        if dungeon_map[new_y][new_x] == 0:
            player["x"] = new_x
            player["y"] = new_y
            # Random encounter
            if random.random() < 0.2:  # 20% chance to encounter enemy
                start_battle()

def rotate_player(direction):
    """Change player direction"""
    player["direction"] = (player["direction"] + direction) % 4

def start_battle():
    """Start battle"""
    global battle_mode, current_enemy, message
    battle_mode = True
    enemy_type = random.choice(enemies)
    current_enemy = {
        "name": enemy_type["name"],
        "hp": enemy_type["hp"],
        "attack": enemy_type["attack"],
        "exp": enemy_type["exp"],
        "gold": enemy_type["gold"]
    }
    message = f"A {current_enemy['name']} appears!"

def player_attack():
    """Player's physical attack"""
    global battle_mode, current_enemy, message
    
    damage = random.randint(5, 15) + player["level"] * 2
    current_enemy["hp"] -= damage
    message = f"You attack! {damage} damage to {current_enemy['name']}!"
    
    if current_enemy["hp"] <= 0:
        end_battle()
    else:
        # Enemy's attack
        enemy_attack()

def cast_spell(spell_index):
    """Cast a spell"""
    global battle_mode, current_enemy, message
    
    if spell_index >= len(spells) or player["level"] < spells[spell_index]["level_req"]:
        message = "You can't cast that spell yet!"
        return
    
    spell = spells[spell_index]
    
    if player["mp"] < spell["mp_cost"]:
        message = "Not enough MP!"
        return
    
    player["mp"] -= spell["mp_cost"]
    damage = random.randint(spell["min_damage"], spell["max_damage"]) + player["level"]
    current_enemy["hp"] -= damage
    message = f"You cast {spell['name']}! {damage} damage to {current_enemy['name']}!"
    
    if current_enemy["hp"] <= 0:
        end_battle()
    else:
        # Enemy's attack
        enemy_attack()

def end_battle():
    """End battle with victory"""
    global battle_mode, current_enemy, message
    
    player["exp"] += current_enemy["exp"]
    player["gold"] += current_enemy["gold"]
    message = f"You defeated the {current_enemy['name']}! Gained {current_enemy['exp']} EXP and {current_enemy['gold']} gold!"
    
    # Level up check
    if player["exp"] >= player["next_level"]:
        player["level"] += 1
        player["max_hp"] += 20
        player["max_mp"] += 10
        player["hp"] = player["max_hp"]
        player["mp"] = player["max_mp"]
        player["next_level"] = int(player["next_level"] * 1.5)
        message += f" Level up! You are now level {player['level']}!"
    
    battle_mode = False
    current_enemy = None

def enemy_attack():
    """Enemy's attack"""
    global message
    
    damage = random.randint(1, current_enemy["attack"])
    player["hp"] -= damage
    message += f"\nThe {current_enemy['name']} attacks! {damage} damage to you!"
    
    if player["hp"] <= 0:
        message += "\nYou have been defeated... Game Over"

def draw_battle_screen():
    """Draw battle screen"""
    # Background
    screen.fill(BLACK)
    
    # Enemy display
    enemy_text = font.render(f"{current_enemy['name']} HP: {current_enemy['hp']}", True, WHITE)
    screen.blit(enemy_text, (WIDTH // 2 - enemy_text.get_width() // 2, 100))
    
    # Player status
    player_text = font.render(f"You Lv.{player['level']} HP: {player['hp']}/{player['max_hp']} MP: {player['mp']}/{player['max_mp']}", True, WHITE)
    screen.blit(player_text, (WIDTH // 2 - player_text.get_width() // 2, HEIGHT - 150))
    
    # Message
    lines = message.split('\n')
    for i, line in enumerate(lines):
        msg_text = font.render(line, True, WHITE)
        screen.blit(msg_text, (WIDTH // 2 - msg_text.get_width() // 2, 200 + i * 40))
    
    # Commands
    attack_text = font.render("A: Attack", True, WHITE)
    screen.blit(attack_text, (50, HEIGHT - 120))
    
    run_text = font.render("R: Run", True, WHITE)
    screen.blit(run_text, (50, HEIGHT - 80))
    
    # Spell commands
    for i, spell in enumerate(spells):
        if player["level"] >= spell["level_req"]:
            spell_key = str(i + 1)
            spell_text = font.render(f"{spell_key}: {spell['name']} ({spell['mp_cost']} MP)", True, WHITE)
            screen.blit(spell_text, (250, HEIGHT - 120 + i * 40))

def draw_status_bar():
    """Draw status bar"""
    # HP bar
    hp_percent = player["hp"] / player["max_hp"]
    hp_bar_width = 150 * hp_percent
    pygame.draw.rect(screen, RED, (20, 20, hp_bar_width, 20))
    pygame.draw.rect(screen, WHITE, (20, 20, 150, 20), 2)
    
    hp_text = font.render(f"HP: {player['hp']}/{player['max_hp']}", True, WHITE)
    screen.blit(hp_text, (180, 20))
    
    # MP bar
    mp_percent = player["mp"] / player["max_mp"]
    mp_bar_width = 150 * mp_percent
    pygame.draw.rect(screen, BLUE, (20, 50, mp_bar_width, 20))
    pygame.draw.rect(screen, WHITE, (20, 50, 150, 20), 2)
    
    mp_text = font.render(f"MP: {player['mp']}/{player['max_mp']}", True, WHITE)
    screen.blit(mp_text, (180, 50))
    
    # Level and experience
    level_text = font.render(f"Lv: {player['level']} EXP: {player['exp']}/{player['next_level']}", True, WHITE)
    screen.blit(level_text, (20, 80))
    
    # Gold
    gold_text = font.render(f"Gold: {player['gold']}", True, GOLD)
    screen.blit(gold_text, (20, 110))

def draw_controls_help():
    """Draw controls help"""
    if not battle_mode:
        controls = [
            "Controls:",
            "Arrow keys: Move/Turn",
            "A: Attack (in battle)",
            "R: Run (in battle)",
            "1-3: Cast spells (in battle)"
        ]
        
        for i, line in enumerate(controls):
            help_text = small_font.render(line, True, WHITE)
            screen.blit(help_text, (20, HEIGHT - 150 + i * 25))

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if battle_mode:
                if event.key == pygame.K_a:  # Attack
                    player_attack()
                elif event.key == pygame.K_r:  # Run
                    if random.random() < 0.5:  # 50% chance to escape
                        battle_mode = False
                        message = "You escaped successfully!"
                    else:
                        message = "Couldn't escape!"
                        enemy_attack()
                elif event.key == pygame.K_1:  # Cast first spell
                    cast_spell(0)
                elif event.key == pygame.K_2:  # Cast second spell
                    cast_spell(1)
                elif event.key == pygame.K_3:  # Cast third spell
                    cast_spell(2)
            else:
                if event.key == pygame.K_UP:  # Move forward
                    dx, dy = DIRECTIONS[player["direction"]]
                    move_player(dx, dy)
                elif event.key == pygame.K_DOWN:  # Move backward
                    dx, dy = DIRECTIONS[player["direction"]]
                    move_player(-dx, -dy)
                elif event.key == pygame.K_LEFT:  # Turn left
                    rotate_player(-1)
                elif event.key == pygame.K_RIGHT:  # Turn right
                    rotate_player(1)
    
    # Drawing
    screen.fill(BLACK)
    
    if battle_mode:
        draw_battle_screen()
    else:
        # Draw 3D perspective
        cast_rays()
        
        # Draw minimap
        draw_minimap()
        
        # Draw status bar
        draw_status_bar()
        
        # Draw controls help
        draw_controls_help()
        
        # Show message if any
        if message:
            msg_text = font.render(message, True, WHITE)
            screen.blit(msg_text, (WIDTH // 2 - msg_text.get_width() // 2, HEIGHT - 50))
    
    pygame.display.flip()
    clock.tick(30)

# End game
pygame.quit()
sys.exit()