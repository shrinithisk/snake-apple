import pygame, random, os

# ───────────── 1. INITIALISE ─────────────
pygame.init()
dis_width, dis_height = 720, 480
dis = pygame.display.set_mode((dis_width, dis_height))
pygame.display.set_caption("Snake Game – Visual Upgrade + High Score")
clock = pygame.time.Clock()

# colours
WHITE = (255, 255, 255)
RED   = (213,  50,  80)
BROWN = (139,  69,  19)
GREEN = ( 34, 139,  34)
BLACK = (  0,   0,   0)

snake_block = 20
snake_speed = 8

# assets
bg_img    = pygame.image.load("background.jpg")
bg_img    = pygame.transform.scale(bg_img, (dis_width, dis_height))
apple_img = pygame.image.load("apple.png")
apple_img = pygame.transform.scale(apple_img, (snake_block, snake_block))

# fonts
score_font = pygame.font.SysFont("arial", 28, bold=True)
big_font   = pygame.font.SysFont("arial", 50, bold=True)

# ───────────── 2. HIGH SCORE PERSISTENCE ─────────────
HS_FILE = "highscore.txt"
def load_highscore() -> int:
    if os.path.exists(HS_FILE):
        try:
            return int(open(HS_FILE).read().strip())
        except ValueError:
            pass
    return 0

def save_highscore(hs: int):
    with open(HS_FILE, "w") as f:
        f.write(str(hs))

high_score = load_highscore()

# ───────────── 3. HELPERS ─────────────
def draw_score(score: int):
    """Draw current score badge and return its rect."""
    text = score_font.render(f"Score: {score}", True, WHITE)
    r = text.get_rect(topleft=(12, 10))
    pygame.draw.rect(dis, BLACK, (r.x-8, r.y-6, r.w+16, r.h+12), border_radius=10)
    dis.blit(text, r)
    return pygame.Rect(r.x-8, r.y-6, r.w+16, r.h+12)

def draw_snake(snake_list):
    for idx, (x, y) in enumerate(snake_list):
        if idx == len(snake_list) - 1:  # head
            pygame.draw.rect(dis, GREEN, (x, y, snake_block, snake_block))
            eye_r = max(2, snake_block // 7)
            off   = snake_block // 4
            pygame.draw.circle(dis, BLACK, (x + off, y + off), eye_r)
            pygame.draw.circle(dis, BLACK, (x + snake_block - off, y + off), eye_r)
        elif idx == len(snake_list) - 2:  # newest block
            pygame.draw.rect(dis, GREEN, (x, y, snake_block, snake_block))
        else:  # older body
            pygame.draw.rect(dis, BROWN, (x, y, snake_block, snake_block))
            mid_y = y + snake_block // 2
            pygame.draw.line(dis, GREEN, (x, mid_y), (x+snake_block, mid_y), 3)

def spawn_food(forbidden_rect):
    while True:
        fx = random.randrange(0, dis_width  - snake_block, snake_block)
        fy = random.randrange(0, dis_height - snake_block, snake_block)
        if not pygame.Rect(fx, fy, snake_block, snake_block).colliderect(forbidden_rect):
            return fx, fy

def rules_screen():
    dis.blit(bg_img, (0,0))
    title = big_font.render("SNAKE  GAME", True, GREEN)
    dis.blit(title, title.get_rect(center=(dis_width/2, dis_height*0.22)))

    rules = [
        "RULES:",
        "• Use Arrow Keys to move the snake",
        "• Eat apples to grow and score points",
        "• Don't hit walls or your own body",
        "• Apple never hides under the score badge",
        "",
        "Press  S  to start  |  Q  to quit"
    ]
    for i, line in enumerate(rules):
        txt = score_font.render(line, True, WHITE)
        dis.blit(txt, txt.get_rect(center=(dis_width/2, dis_height*0.40 + i*32)))
    pygame.display.update()

    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); quit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q:
                    pygame.quit(); quit()
                elif e.key == pygame.K_s:
                    waiting = False

def game_over_screen(score, new_high):
    dis.blit(bg_img, (0,0))
    dis.blit(big_font.render("GAME  OVER", True, RED),
             big_font.render("GAME  OVER", True, RED).get_rect(center=(dis_width/2, dis_height*0.28)))

    scr_txt = score_font.render(f"Your Score: {score}", True, WHITE)
    dis.blit(scr_txt, scr_txt.get_rect(center=(dis_width/2, dis_height*0.45)))

    hs_txt = score_font.render(f"High Score: {high_score}", True, WHITE)
    dis.blit(hs_txt, hs_txt.get_rect(center=(dis_width/2, dis_height*0.55)))

    if new_high:
        yay = score_font.render("Yay! NEW HIGH SCORE!", True, GREEN)
        dis.blit(yay, yay.get_rect(center=(dis_width/2, dis_height*0.63)))

    info = score_font.render("Press  C  to play again  |  Q  to quit", True, WHITE)
    dis.blit(info, info.get_rect(center=(dis_width/2, dis_height*0.75)))
    pygame.display.update()

# ───────────── 4. MAIN GAME LOOP ─────────────
def snake_game():
    global high_score
    x = dis_width // 2
    y = dis_height // 2
    dx = dy = 0
    snake = []
    length = 1

    # first draw to get score badge size
    dis.blit(bg_img, (0,0))
    badge_rect = draw_score(0)
    pygame.display.flip()

    foodx, foody = spawn_food(badge_rect)

    running, dead = True, False
    while running:
        while dead:
            new_high = length-1 > high_score
            if new_high:
                high_score = length-1
                save_highscore(high_score)
            game_over_screen(length-1, new_high)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False; dead = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_q:
                        running = False; dead = False
                    elif e.key == pygame.K_c:
                        snake_game()
                        return

        # input
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if   e.key == pygame.K_LEFT:  dx, dy = -snake_block, 0
                elif e.key == pygame.K_RIGHT: dx, dy =  snake_block, 0
                elif e.key == pygame.K_UP:    dx, dy = 0, -snake_block
                elif e.key == pygame.K_DOWN:  dx, dy = 0,  snake_block

        # move
        x += dx;  y += dy
        if x < 0 or x >= dis_width or y < 0 or y >= dis_height:
            dead = True

        dis.blit(bg_img, (0,0))
        dis.blit(apple_img, (foodx, foody))

        head = [x, y]
        snake.append(head)
        if len(snake) > length:
            snake.pop(0)
        if head in snake[:-1]:
            dead = True

        draw_snake(snake)
        badge_rect = draw_score(length-1)
        pygame.display.update()

        # eat apple?
        if x == foodx and y == foody:
            length += 1
            foodx, foody = spawn_food(badge_rect)

        clock.tick(snake_speed)

    pygame.quit()

# ───────────── 5. RUN ─────────────
if __name__ == "__main__":
    rules_screen()
    snake_game()
