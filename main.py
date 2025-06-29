import pygame
import random
import heapq

# Config
GRID_SIZE = 20
CELL_SIZE = 30
WIDTH = HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 10

# Colors
BG_COLOR = (30, 30, 30)
GRID_COLOR = (50, 50, 50)
BLUE = (66, 135, 245)
GREEN = (46, 204, 113)
RED = (231, 76, 60)
WHITE = (255, 255, 255)

DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("✨ Autonomous Snake Battle ✨")
font = pygame.font.SysFont("arial", 28, bold=True)
clock = pygame.time.Clock()

class Snake:
    def __init__(self, color, start_pos):
        self.body = [start_pos]
        self.color = color
        self.grow = False
        self.alive = True
        self.score = 0

    def move(self, new_head):
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
        self.body.insert(0, new_head)

    def head(self):
        return self.body[0]

    def get_positions(self):
        return set(self.body)

def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

def draw_snake(snake):
    for i, segment in enumerate(snake.body):
        rect = pygame.Rect(segment[0]*CELL_SIZE+2, segment[1]*CELL_SIZE+2, CELL_SIZE-4, CELL_SIZE-4)
        pygame.draw.rect(screen, snake.color, rect, border_radius=8 if i == 0 else 5)

def draw_food(food_pos):
    center = (food_pos[0]*CELL_SIZE + CELL_SIZE//2, food_pos[1]*CELL_SIZE + CELL_SIZE//2)
    pygame.draw.circle(screen, RED, center, CELL_SIZE//3)

def draw_score(snake1, snake2):
    text1 = font.render(f"BLUE: {snake1.score}", True, BLUE)
    text2 = font.render(f"GREEN: {snake2.score}", True, GREEN)
    screen.blit(text1, (20, 10))
    screen.blit(text2, (WIDTH - 180, 10))

def in_bounds(pos):
    x, y = pos
    return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(start, goal, obstacles):
    open_set = [(0 + heuristic(start, goal), 0, start)]
    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, cost, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for dx, dy in DIRS:
            neighbor = (current[0] + dx, current[1] + dy)
            if in_bounds(neighbor) and neighbor not in obstacles:
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, tentative_g, neighbor))

    return []

def get_next_move(snake, food, other_snake):
    block = snake.get_positions().union(other_snake.get_positions())
    path = a_star(snake.head(), food, block)
    return path[0] if path else snake.head()

def random_free_position(snake1, snake2):
    taken = snake1.get_positions().union(snake2.get_positions())
    all_cells = {(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)}
    free = list(all_cells - taken)
    return random.choice(free) if free else None

# Init
snake1 = Snake(BLUE, (5, 5))
snake2 = Snake(GREEN, (15, 15))
food = random_free_position(snake1, snake2)

# Game loop
running = True
while running:
    clock.tick(FPS)
    screen.fill(BG_COLOR)
    draw_grid()
    draw_snake(snake1)
    draw_snake(snake2)
    draw_food(food)
    draw_score(snake1, snake2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if snake1.alive:
        move1 = get_next_move(snake1, food, snake2)
        if move1 == food:
            snake1.grow = True
            snake1.score += 1
            food = random_free_position(snake1, snake2)
        snake1.move(move1)

    if snake2.alive:
        move2 = get_next_move(snake2, food, snake1)
        if move2 == food:
            snake2.grow = True
            snake2.score += 1
            food = random_free_position(snake1, snake2)
        snake2.move(move2)

    for snake in [snake1, snake2]:
        head = snake.head()
        if (not in_bounds(head) or
            snake.body.count(head) > 1 or
            (head in snake2.body if snake == snake1 else head in snake1.body)):
            snake.alive = False

    if not snake1.alive and not snake2.alive:
        running = False

    pygame.display.flip()

pygame.quit()

