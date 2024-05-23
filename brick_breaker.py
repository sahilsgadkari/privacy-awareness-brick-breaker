import asyncio
import pygame
import random
import time

pygame.init()

# Constants
WIDTH, HEIGHT = 900, 900
FRAME_WIDTH = 5  # Frame width adjusted
FRAME_GAP = 10  # Gap between frame and bricks
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
FONT_SIZE = 16
BRICK_FONT_SIZE = 10
FPS = 30
BRICK_HEIGHT = 35  # Increased height for better visibility
ADD_BRICK_INTERVAL = 20
BRICK_ROWS = 5
BRICK_COLS = 10
H_GAP = 10
V_GAP = 10  # Vertical gap constant
BRICK_WIDTH = (WIDTH - (BRICK_COLS - 1) * H_GAP - 2 * (FRAME_WIDTH + FRAME_GAP)) // BRICK_COLS
PADDLE_PADDING = 50  # Padding between paddle and bottom of the screen
MESSAGE_PADDING = 70  # Padding between message and paddle
SCORE_PADDING = 20  # Padding between score/lives and bottom of the screen

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
pygame.display.set_caption("Privacy Awareness Block Breaker")
font = pygame.font.Font('freesansbold.ttf', FONT_SIZE)
brick_font = pygame.font.Font('freesansbold.ttf', BRICK_FONT_SIZE)
clock = pygame.time.Clock()

# Improved Striker class
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
        # Draw rounded rectangle for the paddle
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)

    def update(self, xFac):
        self.posx += self.speed * xFac
        self.posx = max(FRAME_WIDTH + FRAME_GAP, min(self.posx, WIDTH - self.width - FRAME_WIDTH - FRAME_GAP))
        self.rect = pygame.Rect(self.posx, self.posy, self.width, self.height)

# Block class
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
        self.posy += (BRICK_HEIGHT + V_GAP)  # Move down by brick height and vertical gap
        self.rect = pygame.Rect(self.posx, self.posy, self.width, self.height)

    def hit(self):
        self.health -= 100

# Ball class
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
        self.xFac = offset  # Set xFac to offset
        if self.xFac > 1:
            self.xFac = 1
        elif self.xFac < -1:
            self.xFac = -1

    def hit_brick(self):
        self.yFac *= -1

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
            # 30:70 ratio for green:white
            color = GREEN if random.random() < 0.3 else WHITE
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
        # 30:70 ratio for green:white
        color = GREEN if random.random() < 0.3 else WHITE
        x_pos = col * (width + h_gap) + FRAME_WIDTH + FRAME_GAP
        y_pos = FRAME_WIDTH + FRAME_GAP  # New bricks start at the top
        new_bricks.append(Block(x_pos, y_pos, width, height, color, label, message))
    bricks.extend(new_bricks)

def display_message(message):
    words = message.split(' ')
    lines = []
    current_line = words[0]
    for word in words[1:]:
        if font.size(current_line + ' ' + word)[0] < WIDTH - 40:  # Adjust width to fit within the game window
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
    screen.fill(BLACK)
    start_text = font.render("Press any key to start", True, WHITE)
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 - start_text.get_height() // 2))
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                waiting = False

async def main():
    running = True
    lives = 3
    score = 0
    striker = Striker(WIDTH // 2 - 50, HEIGHT - PADDLE_PADDING, 100, 20, 10, WHITE)  # Adjusted position of paddle
    strikerXFac = 0
    ball = Ball(WIDTH // 2, HEIGHT // 2, 7, 3, WHITE)  # Update the ball speed here to 3
    bricks = create_bricks(BRICK_ROWS, BRICK_COLS, BRICK_WIDTH, BRICK_HEIGHT, H_GAP, V_GAP)
    last_add_time = time.time()
    current_message = ""

    show_start_screen()  # Show start screen before starting the game

    while running:
        screen.fill(BLACK)  # Fill the screen with black to avoid overlapping colors

        # Draw the frame
        pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, FRAME_WIDTH))  # Top frame
        pygame.draw.rect(screen, WHITE, (0, 0, FRAME_WIDTH, HEIGHT))  # Left frame
        pygame.draw.rect(screen, WHITE, (WIDTH - FRAME_WIDTH, 0, FRAME_WIDTH, HEIGHT))  # Right frame
        pygame.draw.rect(screen, WHITE, (0, HEIGHT - FRAME_WIDTH, WIDTH, FRAME_WIDTH))  # Bottom frame

        # Draw the score and lives display
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(score_text, (FRAME_WIDTH + 10, HEIGHT - SCORE_PADDING - FRAME_WIDTH))  # Adjusted position of score
        screen.blit(lives_text, (WIDTH - lives_text.get_width() - FRAME_WIDTH - 10, HEIGHT - SCORE_PADDING - FRAME_WIDTH))  # Adjusted position of lives

        if not bricks:
            bricks = create_bricks(BRICK_ROWS, BRICK_COLS, BRICK_WIDTH, BRICK_HEIGHT, H_GAP, V_GAP)

        if lives <= 0:
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    strikerXFac = -1
                if event.key == pygame.K_RIGHT:
                    strikerXFac = 1
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    strikerXFac = 0

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
                    # Increase ball speed after every 50 points
                    if score % 50 == 0:
                        ball.speed += 1
                        if ball.speed % 5 == 0:  # Check if ball speed is a multiple of 5
                            striker.speed += 1  # Increase paddle speed as well

        striker.update(strikerXFac)
        if ball.update():
            lives -= 1
            ball.reset()  # Ensure the ball resets but keeps the same speed

        if time.time() - last_add_time > ADD_BRICK_INTERVAL:
            add_new_bricks(bricks, BRICK_COLS, BRICK_WIDTH, BRICK_HEIGHT, H_GAP, V_GAP)  # Add V_GAP here
            last_add_time = time.time()

        striker.display()
        ball.display()
        for brick in bricks:
            brick.display()

        # Display the current message
        if current_message:
            display_message(current_message)

        pygame.display.update()
        await asyncio.sleep(0)  # Ensuring non-blocking call
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
