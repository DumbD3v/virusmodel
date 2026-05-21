import pygame
import random
import math

pygame.init()

# scherm pygame
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pandemic Simulator")

font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 40)
clock = pygame.time.Clock()

# kleuren
WHITE = (255,255,255)
BLACK = (30,30,30)
GREEN = (0,255,0)
RED = (255,0,0)
BLUE = (0,120,255)
GRAY = (120,120,120)

# variabelen
settings = {
    "population": "120",
    "start_infected": "5",
    "infection_chance": "0.25",
    "infection_radius": "10",
    "death_chance": "0.001",
    "recovery_time": "400",
    "lockdown": "0.0",
    "vaccination": "0.0",
    "speed": "1.5"
}

keys = list(settings.keys())
active_index = 0

menu = True
people = []

# mensen
class Person:
    def __init__(self, infected=False, immune=False):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)

        self.dx = random.choice([-1,-0.5,0.5,1])
        self.dy = random.choice([-1,-0.5,0.5,1])

        self.status = "healthy"
        if infected:
            self.status = "infected"
        elif immune:
            self.status = "recovered"

        self.time = 0

    def move(self):
        if self.status == "dead":
            return

        speed = float(settings["speed"]) * (1 - float(settings["lockdown"]))

        self.x += self.dx * speed
        self.y += self.dy * speed

        if self.x < 0 or self.x > WIDTH:
            self.dx *= -1
        if self.y < 0 or self.y > HEIGHT:
            self.dy *= -1

    def update(self):
        if self.status == "infected":
            self.time += 1

            # sterfte terwijl je geinfecteerd bent 
            if random.random() < float(settings["death_chance"]):
                self.status = "dead"
                return

            if self.time > int(settings["recovery_time"]):
                self.status = "recovered"

    def draw(self):
        if self.status == "healthy":
            color = GREEN
        elif self.status == "infected":
            color = RED
        elif self.status == "recovered":
            color = BLUE
        else:
            color = GRAY

        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 5)

# mensheid of pupolatie, of hoe je het wilt noemen
def create_population():
    global people
    people = []

    pop = int(settings["population"])
    start_inf = int(settings["start_infected"])
    vacc = float(settings["vaccination"])

    for i in range(pop):
        infected = i < start_inf
        immune = random.random() < vacc
        people.append(Person(infected, immune))

# knoppen
start_btn = pygame.Rect(420, 600, 200, 50)
restart_btn = pygame.Rect(420, 600, 200, 50)

# loop
running = True

while running:
    screen.fill(BLACK)
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # menu
        if menu:
            if event.type == pygame.KEYDOWN:

                key = keys[active_index]

                if event.key == pygame.K_BACKSPACE:
                    settings[key] = settings[key][:-1]

                elif event.key == pygame.K_TAB:
                    active_index = (active_index + 1) % len(keys)

                else:
                    settings[key] += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:

                if start_btn.collidepoint(event.pos):
                    create_population()
                    menu = False

        # simualtie/modelleren
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:

                # restart knop
                if restart_btn.collidepoint(event.pos):
                    menu = True
                    people = []

    # menu
    if menu:

        title = big_font.render("Pandemic Simulator Setup", True, WHITE)
        screen.blit(title, (260, 30))

        y = 120

        for i, key in enumerate(keys):
            color = GREEN if i == active_index else WHITE
            txt = font.render(f"{key}: {settings[key]}", True, color)
            screen.blit(txt, (300, y))
            y += 45

        screen.blit(font.render("TAB = switch | TYPE = edit", True, WHITE), (300, 80))

        pygame.draw.rect(screen, GREEN, start_btn)
        screen.blit(font.render("START", True, BLACK), (500, 615))

    # simulatie/modelleren
    else:

        for p in people:
            p.move()
            p.update()

        # mensen infecteren
        for a in people:
            if a.status != "infected":
                continue

            for b in people:
                if b.status != "healthy":
                    continue

                dist = math.hypot(a.x - b.x, a.y - b.y)

                if dist < float(settings["infection_radius"]):
                    if random.random() < float(settings["infection_chance"]):
                        b.status = "infected"

        for p in people:
            p.draw()

        
        h = sum(1 for p in people if p.status == "healthy")
        i = sum(1 for p in people if p.status == "infected")
        r = sum(1 for p in people if p.status == "recovered")
        d = sum(1 for p in people if p.status == "dead")

        stats = font.render(f"H:{h} I:{i} R:{r} D:{d}", True, WHITE)
        screen.blit(stats, (20,20))

        # restart knop
        pygame.draw.rect(screen, (200,50,50), restart_btn)
        screen.blit(font.render("RESTART", True, WHITE), (465, 615))

    pygame.display.update()

pygame.quit()