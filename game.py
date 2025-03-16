from pathlib import Path
import pygame
import random
import json
from typing import Tuple, List

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
SPACESHIP_SPEED = 5
BULLET_SPEED = 7
MIN_ASTEROID_SPEED = 2
MAX_ASTEROID_SPEED = 5
ASTEROID_SPAWN_RATE = 50
IMMUNITY_DURATION = 2000  # 2 seconds in milliseconds
SHATTER_DURATION = 250  # 0.25 seconds in milliseconds
POWERUP_DURATION = 5000  # 5 seconds in milliseconds
LEADERBOARD_FILE = "leaderboard.json"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asteroid Shooter")

# Load assets with transparency
def load_image_with_transparency(image_path: str):
    """Load an image with transparency from a PNG file."""
    image = pygame.image.load(image_path).convert_alpha()
    return image

spaceship_image = load_image_with_transparency("spaceship.png")
asteroid_image = load_image_with_transparency("asteroid.png")
bullet_image = load_image_with_transparency("bullet.png")
shattered_asteroid_image = load_image_with_transparency("shattered_asteroid.png")
special_item_image = load_image_with_transparency("special_item.png")
triple_bullet_image = load_image_with_transparency("triple_bullet.png")

# Font for HUD and menus
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# Clock
clock = pygame.time.Clock()

# Game objects
class Spaceship:
    def __init__(self):
        self.image = spaceship_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.is_immune = False
        self.immunity_start_time = 0
        self.has_powerup = False
        self.powerup_start_time = 0

    def move(self, dx: int, dy: int):
        """Move the spaceship by dx and dy."""
        self.rect.x += dx
        self.rect.y += dy

    def draw(self):
        """Draw the spaceship on the screen."""
        if self.is_immune:
            # Make the spaceship glow by drawing a white border
            pygame.draw.rect(screen, WHITE, self.rect.inflate(10, 10), 2)
        screen.blit(self.image, self.rect)

    def start_immunity(self):
        """Start the immunity state."""
        self.is_immune = True
        self.immunity_start_time = pygame.time.get_ticks()

    def update_immunity(self):
        """Update the immunity state."""
        if self.is_immune and pygame.time.get_ticks() - self.immunity_start_time > IMMUNITY_DURATION:
            self.is_immune = False

    def start_powerup(self):
        """Start the powerup state."""
        self.has_powerup = True
        self.powerup_start_time = pygame.time.get_ticks()

    def update_powerup(self):
        """Update the powerup state."""
        if self.has_powerup and pygame.time.get_ticks() - self.powerup_start_time > POWERUP_DURATION:
            self.has_powerup = False

class Bullet:
    def __init__(self, x: int, y: int, is_triple: bool = False):
        self.image = pygame.transform.scale(triple_bullet_image if is_triple else bullet_image, (10, 20))
        self.rect = self.image.get_rect(center=(x, y))
        self.is_triple = is_triple

    def update(self):
        """Move the bullet upwards."""
        self.rect.y -= BULLET_SPEED

    def draw(self):
        """Draw the bullet on the screen."""
        screen.blit(self.image, self.rect)

class Asteroid:
    def __init__(self):
        self.size = random.randint(30, 80)
        self.image = pygame.transform.scale(asteroid_image, (self.size, self.size))
        self.shattered_image = pygame.transform.scale(shattered_asteroid_image, (self.size, self.size))
        self.rect = self.image.get_rect(center=(random.randint(0, SCREEN_WIDTH), -50))
        self.is_shattered = False
        self.shatter_time = 0
        self.speed = random.randint(MIN_ASTEROID_SPEED, MAX_ASTEROID_SPEED)

    def update(self):
        """Move the asteroid downwards."""
        if not self.is_shattered:
            self.rect.y += self.speed

    def draw(self):
        """Draw the asteroid on the screen."""
        if self.is_shattered:
            screen.blit(self.shattered_image, self.rect)
        else:
            screen.blit(self.image, self.rect)

    def shatter(self):
        """Shatter the asteroid."""
        if not self.is_shattered:  # Only shatter if not already shattered
            self.is_shattered = True
            self.shatter_time = pygame.time.get_ticks()

    def should_disappear(self):
        """Check if the shattered asteroid should disappear."""
        return self.is_shattered and pygame.time.get_ticks() - self.shatter_time > SHATTER_DURATION

class SpecialItem:
    def __init__(self):
        self.image = special_item_image
        self.rect = self.image.get_rect(center=(random.randint(0, SCREEN_WIDTH), -50))
        self.speed = random.randint(MIN_ASTEROID_SPEED, MAX_ASTEROID_SPEED)

    def update(self):
        """Move the special item downwards."""
        self.rect.y += self.speed

    def draw(self):
        """Draw the special item on the screen."""
        screen.blit(self.image, self.rect)

# Leaderboard functions
def load_leaderboard():
    """Load the leaderboard from a file."""
    try:
        with open(LEADERBOARD_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_leaderboard(leaderboard):
    """Save the leaderboard to a file."""
    with open(LEADERBOARD_FILE, "w") as file:
        json.dump(leaderboard, file)

def add_score_to_leaderboard(name: str, score: int):
    """Add a score to the leaderboard."""
    leaderboard = load_leaderboard()
    leaderboard.append({"name": name, "score": score})
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    leaderboard = leaderboard[:10]  # Keep only the top 10 scores
    save_leaderboard(leaderboard)

# Menu functions
def draw_menu():
    """Draw the welcome menu."""
    screen.fill(BLACK)
    title_text = large_font.render("Asteroid Shooter", True, WHITE)
    start_text = font.render("Press SPACE to Start", True, WHITE)
    leaderboard_text = font.render("Press L to View Leaderboard", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 3))
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(leaderboard_text, (SCREEN_WIDTH // 2 - leaderboard_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    pygame.display.flip()

def draw_leaderboard():
    """Draw the leaderboard."""
    screen.fill(BLACK)
    title_text = large_font.render("Leaderboard", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
    leaderboard = load_leaderboard()
    for i, entry in enumerate(leaderboard):
        score_text = font.render(f"{i + 1}. {entry['name']}: {entry['score']}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 150 + i * 50))
    back_text = font.render("Press B to go Back", True, WHITE)
    screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT - 100))
    pygame.display.flip()

def draw_game_over(score: int):
    """Draw the game over screen."""
    screen.fill(BLACK)
    title_text = large_font.render("Game Over", True, WHITE)
    score_text = font.render(f"Your Score: {score}", True, WHITE)
    restart_text = font.render("Press SPACE to Restart", True, WHITE)
    menu_text = font.render("Press M to go to Menu", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 3))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
    pygame.display.flip()

def get_player_name(score: int):
    """Get the player's name for the leaderboard."""
    input_box = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill(BLACK)
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.display.flip()

    return text

# Game loop
def game_loop():
    """Main game loop."""
    # Initialize game objects
    spaceship = Spaceship()
    bullets: List[Bullet] = []
    asteroids: List[Asteroid] = []
    special_items: List[SpecialItem] = []
    score = 0
    lives = 3

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if spaceship.has_powerup:
                        # Shoot triple bullets
                        bullets.append(Bullet(spaceship.rect.centerx - 20, spaceship.rect.top, is_triple=True))
                        bullets.append(Bullet(spaceship.rect.centerx, spaceship.rect.top, is_triple=True))
                        bullets.append(Bullet(spaceship.rect.centerx + 20, spaceship.rect.top, is_triple=True))
                    else:
                        # Shoot single bullet
                        bullets.append(Bullet(spaceship.rect.centerx, spaceship.rect.top))

        # Key states
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            spaceship.move(-SPACESHIP_SPEED, 0)
        if keys[pygame.K_RIGHT]:
            spaceship.move(SPACESHIP_SPEED, 0)
        if keys[pygame.K_UP]:
            spaceship.move(0, -SPACESHIP_SPEED)
        if keys[pygame.K_DOWN]:
            spaceship.move(0, SPACESHIP_SPEED)

        # Update game objects
        for bullet in bullets:
            bullet.update()
        for asteroid in asteroids:
            asteroid.update()
        for special_item in special_items:
            special_item.update()

        # Spawn asteroids
        if random.randint(1, ASTEROID_SPAWN_RATE) == 1:
            asteroids.append(Asteroid())

        # Spawn special items
        if random.randint(1, ASTEROID_SPAWN_RATE * 10) == 1:  # Less frequent than asteroids
            special_items.append(SpecialItem())

        # Remove off-screen bullets, asteroids, and special items
        bullets = [bullet for bullet in bullets if bullet.rect.bottom > 0]
        asteroids = [asteroid for asteroid in asteroids if asteroid.rect.top < SCREEN_HEIGHT]
        special_items = [special_item for special_item in special_items if special_item.rect.top < SCREEN_HEIGHT]

        # Collision detection (bullet vs asteroid)
        for bullet in bullets[:]:
            for asteroid in asteroids[:]:
                if bullet.rect.colliderect(asteroid.rect):
                    bullets.remove(bullet)
                    asteroid.shatter()
                    score += 1
                    break

        # Collision detection (spaceship vs asteroid)
        for asteroid in asteroids[:]:
            if not spaceship.is_immune and spaceship.rect.colliderect(asteroid.rect):
                lives -= 1
                spaceship.start_immunity()
                asteroid.shatter()
                if lives <= 0:
                    player_name = get_player_name(score)
                    if player_name:
                        add_score_to_leaderboard(player_name, score)
                    return "game_over"

        # Collision detection (spaceship vs special item)
        for special_item in special_items[:]:
            if spaceship.rect.colliderect(special_item.rect):
                spaceship.start_powerup()
                special_items.remove(special_item)

        # Collision detection (asteroid vs asteroid)
        for i in range(len(asteroids)):
            for j in range(i + 1, len(asteroids)):
                if asteroids[i].rect.colliderect(asteroids[j].rect):
                    asteroids[i].shatter()
                    asteroids[j].shatter()

        # Remove shattered asteroids after 0.25 seconds
        asteroids = [asteroid for asteroid in asteroids if not asteroid.should_disappear()]

        # Update immunity and powerup states
        spaceship.update_immunity()
        spaceship.update_powerup()

        # Draw everything
        screen.fill(BLACK)
        spaceship.draw()
        for bullet in bullets:
            bullet.draw()
        for asteroid in asteroids:
            asteroid.draw()
        for special_item in special_items:
            special_item.draw()

        # Draw HUD (score, lives, and powerup status)
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        powerup_text = font.render(f"Powerup: {'Active' if spaceship.has_powerup else 'Inactive'}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        screen.blit(powerup_text, (10, 90))

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

# Main menu loop
def main_menu():
    """Main menu loop."""
    while True:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "start_game"
                elif event.key == pygame.K_l:
                    return "leaderboard"

# Leaderboard loop
def leaderboard_loop():
    """Leaderboard loop."""
    while True:
        draw_leaderboard()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    return "menu"

# Game over loop
def game_over_loop(score: int):
    """Game over loop."""
    while True:
        draw_game_over(score)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "start_game"
                elif event.key == pygame.K_m:
                    return "menu"

# Main game flow
def main():
    """Main game flow."""
    current_state = "menu"
    score = 0

    while True:
        if current_state == "menu":
            current_state = main_menu()
        elif current_state == "start_game":
            current_state = game_loop()
        elif current_state == "leaderboard":
            current_state = leaderboard_loop()
        elif current_state == "game_over":
            current_state = game_over_loop(score)
        elif current_state == "quit":
            break

# Run the game
if __name__ == "__main__":
    main()
    pygame.quit()
