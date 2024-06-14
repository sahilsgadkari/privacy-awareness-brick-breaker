import asyncio
import pygame
import random
import time
import sys

# Initialize pygame and Pygbag
pygame.init()

# Constants
WIDTH, HEIGHT = 1400, 900
FRAME_WIDTH = 5
FRAME_GAP = 10
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
FONT_SIZE = 16
BRICK_FONT_SIZE = 10
FPS = 60
BRICK_HEIGHT = 35
ADD_BRICK_INTERVAL = 20
BRICK_ROWS = 5
BRICK_COLS = 12
H_GAP = 10
V_GAP = 10
BRICK_WIDTH = (WIDTH - (BRICK_COLS - 1) * H_GAP - 2 * (FRAME_WIDTH + FRAME_GAP)) // BRICK_COLS
PADDLE_PADDING = 50
MESSAGE_PADDING = 70
SCORE_PADDING = 20

# Privacy messages
PRIVACY_ASPECTS = [
    ("Controller", "Organization deciding how and why personal data should be processed."),
    ("Encryption", "Always encrypt sensitive data to keep it secure."),
    ("Cookies", "Manage cookies to control how your information is tracked online."),
    ("Two-Factor", "Enable two-factor authentication for an added layer of security."),
    ("Passwords", "Use strong, unique passwords for each account to enhance security."),
    ("Phishing", "Avoid phishing scams by not clicking on suspicious links or emails."),
    ("VPN", "Use a VPN to secure your internet connection and protect your privacy."),
    ("DPIA", "Assessment to identify and mitigate risks associated with data processing activities."),
    ("Access Ctrl", "Only authorized individuals should access or modify sensitive information, protecting data from unauthorized use and breaches."),
    ("Data Sharing", "Be cautious about sharing personal information with external third parties."),
    ("Data Breach", "Incident where personal data is accessed or disclosed without authorization."),
    ("PII", "Personally Identifiable Information (PII) - Information that can identify a person, like names and addresses."),
    ("Sensitive PII", "Sensitive PII - PII revealing racial or ethnic origin, political opinions, religious or philosophical beliefs, trade union membership, genetic data, biometric data, health data."),
    ("LFT", "Lawfulness, Fairness, and Transparency - Data must be processed legally, fairly, and transparently."),
    ("Purpose Lmt", "Purpose Limitation - Data should be collected for specified, explicit purposes and not used for incompatible purposes."),
    ("Data Mini", "Data Minimization - Only the necessary data for the specified purpose should be collected."),
    ("Accuracy", "Data should be accurate and kept up to date."),
    ("Storage Lmt", "Storage Limitation - Data should be kept only as long as necessary for the purpose."),
    ("Int & Conf", "Integrity and Confidentiality - Data must be processed securely to prevent unauthorized access & to ensure integrity."),
    ("Accountability", "Organizations & its employees should ensure compliance with applicable data protection / privacy laws.")
]

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Privacy Awareness Brick Breaker")
font = pygame.font.Font('freesansbold.ttf', FONT_SIZE)
brick_font = pygame.font.Font('freesansbold.ttf', BRICK_FONT_SIZE)
clock = pygame.time.Clock()

# Load images
try:
    background_img = pygame.image.load('/images/background.png')
    start_button_img = pygame.image.load('/images/start_button.png')
    exit_button_img = pygame.image.load('/images/exit_button.png')
    return_button_img = pygame.image.load('/images/return_button.png')
except pygame.error as e:
    print(f"Error loading images: {e}")
    sys.exit(1)

# Game classes
class Striker:
    def __init__(self, posx, posy, width, height, speed, color):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color
        self.rect = pygame.Rect(self.posx, self.posy, self.width, self.height)

    def display(self):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_LEFT]:
            self.posx -= self.speed
        if keys_pressed[pygame.K_RIGHT]:
            self.posx += self.speed
        self.posx = max(FRAME_WIDTH + FRAME_GAP, min(self.posx, WIDTH - self.width - FRAME_WIDTH - FRAME_GAP))
        self.rect.x = self.posx

class Block:
    def __init__(self, posx, posy, width, height, color, label, message):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.color = color
        self.label = label
        self.message = message
        self.rect = pygame.Rect(self.posx, self.posy, self.width, self.height)
        self.health = 100

    def display(self):
        if self.health > 0:
            pygame.draw.rect(screen, self.color, self.rect)
            text = brick_font.render(self.label, True, BLACK)
            text_rect = text.get_rect(center=(self.rect.x + self.width // 2, self.rect.y + self.height // 2))
            screen.blit(text, text_rect)

    def move_down(self):
        self.posy += (BRICK_HEIGHT + V_GAP)
        self.rect.y = self.posy

    def hit(self):
        self.health -= 100

class Ball:
    def __init__(self, posx, posy, radius, speed, color):
        self.posx = posx
        self.posy = posy
        self.radius = radius
        self.speed = speed
        self.color = color
        self.xFac, self.yFac = 1, -1

    def display(self):
        pygame.draw.circle(screen, self.color, (self.posx, self.posy), self.radius)

    def update(self):
        self.posx += self.xFac * self.speed
        self.posy += self.yFac * self.speed
        if self.posx <= FRAME_WIDTH + FRAME_GAP + self.radius or self.posx >= WIDTH - FRAME_WIDTH - FRAME_GAP - self.radius:
            self.xFac *= -1
        if self.posy <= FRAME_WIDTH + FRAME_GAP + self.radius:
            self.yFac *= -1
        if self.posy >= HEIGHT - FRAME_WIDTH - FRAME_GAP - self.radius:
            return True
        return False

    def reset(self):
        self.posx, self.posy = WIDTH // 2, HEIGHT // 2
        self.xFac, self.yFac = 1, -1

    def hit_paddle(self, paddle):
        self.yFac *= -1
        offset = (self.posx - paddle.posx) / (paddle.width / 2) - 1
        self.xFac = offset
        if self.xFac > 1:
            self.xFac = 1
        elif self.xFac < -1:
            self.xFac = -1

    def hit_brick(self):
        self.yFac *= -1

# Helper functions
def collision_checker(rect, ball):
    ball_rect = pygame.Rect(ball.posx - ball.radius, ball.posy - ball.radius, ball.radius * 2, ball.radius * 2)
    return rect.colliderect(ball_rect)

def create_bricks(rows, cols, width, height, h_gap, v_gap):
    bricks = []
    random.shuffle(PRIVACY_ASPECTS)
    for row in range(rows):
        for col in range(cols):
            aspect_index = (row * cols + col) % len(PRIVACY_ASPECTS)
            label, message = PRIVACY_ASPECTS[aspect_index]
            color = GREEN if random.random() < 0.4 else WHITE
            x_pos = col * (width + h_gap) + FRAME_WIDTH + FRAME_GAP
            y_pos = row * (height + v_gap) + FRAME_WIDTH + FRAME_GAP
            bricks.append(Block(x_pos, y_pos, width, height, color, label, message))
    return bricks

def add_new_bricks(bricks, cols, width, height, h_gap, v_gap):
    for brick in bricks:
        brick.move_down()
    new_bricks = []
    random.shuffle(PRIVACY_ASPECTS)
    for col in range(cols):
        aspect_index = col % len(PRIVACY_ASPECTS)
        label, message = PRIVACY_ASPECTS[aspect_index]
        color = GREEN if random.random() < 0.4 else WHITE
        x_pos = col * (width + h_gap) + FRAME_WIDTH + FRAME_GAP
        y_pos = FRAME_WIDTH + FRAME_GAP  # New bricks start at the top
        new_bricks.append(Block(x_pos, y_pos, width, height, color, label, message))
    bricks.extend(new_bricks)  # Add the new bricks to the existing list

def display_message(message):
    words = message.split(' ')
    lines = []
    current_line = words[0]
    for word in words[1:]:
        if font.size(current_line + ' ' + word)[0] < WIDTH - 40:
            current_line += ' ' + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)

    y_offset = HEIGHT - PADDLE_PADDING - MESSAGE_PADDING - len(lines) * FONT_SIZE
    for line in lines:
        message_text = font.render(line, True, WHITE)
        screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, y_offset))
        y_offset += FONT_SIZE + 5  # Line spacing

def show_start_screen():
    screen.blit(background_img, (0, 0))
    start_button_rect = start_button_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    exit_button_rect = exit_button_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    screen.blit(start_button_img, start_button_rect)
    screen.blit(exit_button_img, exit_button_rect)
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_button_rect.collidepoint(mouse_pos):
                    waiting = False
                if exit_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

async def main():
    running = True
    global lives, score  # Make lives and score global to be modified in handle_restart
    lives = 3
    score = 0
    high_score = 0
    striker = Striker(WIDTH // 2 - 50, HEIGHT - PADDLE_PADDING, 100, 20, 10, WHITE)
    strikerXFac = 0
    ball = Ball(WIDTH // 2, HEIGHT // 2, 7, 3, WHITE)
    bricks = create_bricks(BRICK_ROWS, BRICK_COLS, BRICK_WIDTH, BRICK_HEIGHT, H_GAP, V_GAP)
    last_add_time = time.time()
    current_message = ""

    show_start_screen()

    while running:
        screen.fill(BLACK)
        # Draw the frame
        pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, FRAME_WIDTH))
        pygame.draw.rect(screen, WHITE, (0, 0, FRAME_WIDTH, HEIGHT))
        pygame.draw.rect(screen, WHITE, (WIDTH - FRAME_WIDTH, 0, FRAME_WIDTH, HEIGHT))
        pygame.draw.rect(screen, WHITE, (0, HEIGHT - FRAME_WIDTH, WIDTH, FRAME_WIDTH))

        # Display scores and lives
        score_text = font.render(f"Score: {score}", True, WHITE)
        high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(score_text, (10, HEIGHT - SCORE_PADDING - FRAME_WIDTH))
        screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT - SCORE_PADDING - FRAME_WIDTH))
        screen.blit(lives_text, (WIDTH - lives_text.get_width() - FRAME_WIDTH - 10, HEIGHT - SCORE_PADDING - FRAME_WIDTH))

        if not bricks:
            bricks = create_bricks(BRICK_ROWS, BRICK_COLS, BRICK_WIDTH, BRICK_HEIGHT, H_GAP, V_GAP)

        if lives <= 0:
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Exit the game loop when the user closes the window
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_button_rect.collidepoint(mouse_pos):
                    waiting = False
                if exit_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        keys_pressed = pygame.key.get_pressed()
        striker.update(keys_pressed)

        if collision_checker(striker.rect, ball):
            ball.hit_paddle(striker)
        for brick in bricks:
            if collision_checker(brick.rect, ball):
                ball.hit_brick()
                brick.hit()
                if brick.health <= 0:
                    current_message = brick.message
                    bricks.remove(brick)
                    score += 5
                    if score % 50 == 0:
                        ball.speed += 1
                        if ball.speed % 5 == 0:
                            striker.speed += 1

        if ball.update():
            lives -= 1
            if lives <= 0:
                running = False
            ball.reset()

        if time.time() - last_add_time > ADD_BRICK_INTERVAL:
            add_new_bricks(bricks, BRICK_COLS, BRICK_WIDTH, BRICK_HEIGHT, H_GAP, V_GAP)
            last_add_time = time.time()

        striker.display()
        ball.display()
        for brick in bricks:
            brick.display()

        if current_message:
            display_message(current_message)

        pygame.display.update()
        await asyncio.sleep(0)
        clock.tick(FPS)

    if score > high_score:
        high_score = score

    lives = 3
    score = 0

    show_game_over_screen()
    await handle_restart()

def show_game_over_screen():
    screen.fill(BLACK)
    game_over_text = font.render("Game Over! Click to restart", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
    return_button_rect = return_button_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    screen.blit(return_button_img, return_button_rect)
    pygame.display.update()

async def handle_restart():
    global lives, score
    lives = 3
    score = 0
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        await asyncio.sleep(0)
    await main()  # Call main asynchronously

if __name__ == "__main__":
    asyncio.run(main())
