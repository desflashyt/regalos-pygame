


import math
import random
import pygame

# ---------- AJUSTES ----------
WIDTH, HEIGHT = 540, 960        
FPS = 60
NUM_FLOWERS = 9                 
GROW_FRAMES = 80                
BLOOM_FRAMES = 70               
FALLING_PETALS = True           

# ---------- MENSAJE ----------
MESSAGE = "Happy Anniversary\nMy Love"

FONT_NAMES = "georgia,segoescript,arial"
TEXT_COLOR = (255, 232, 238)

# Colores de las flores
FLOWER_COLORS = [
    (235, 70, 110),     
    (255, 150, 180),    
    (240, 240, 250),    
    (255, 190, 80),     
    (170, 110, 230),    
    (230, 50, 60),      
]

CX = WIDTH // 2
BASE_Y = 690                    
STEM_COLOR = (40, 150, 75)
LEAF_COLOR = (55, 175, 90)


# ---------- UTILIDADES ----------
def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def lighter(c, k):
    return tuple(int(v + (255 - v) * k) for v in c)


def darker(c, k):
    return tuple(int(v * (1 - k)) for v in c)


def petal_points(cx, cy, ang, length, width):
    """Polígono con forma de pétalo/hoja que sale de (cx, cy) hacia 'ang'."""
    ca, sa = math.cos(ang), math.sin(ang)
    left, right = [], []
    for i in range(9):
        t = i / 8
        d = length * t
        w = width * math.sin(math.pi * t) ** 0.8
        left.append((cx + ca * d - sa * w, cy + sa * d + ca * w))
        right.append((cx + ca * d + sa * w, cy + sa * d - ca * w))
    return left + right[::-1]


class Flower:
    def __init__(self, angle_deg, length, color, delay):
        a = math.radians(angle_deg)
        self.p0 = (CX + random.uniform(-6, 6), BASE_Y)
        top = (self.p0[0] + math.sin(a) * length, BASE_Y - math.cos(a) * length)
        dx, dy = top[0] - self.p0[0], top[1] - self.p0[1]
        self.p1 = (self.p0[0] + dx * 0.1, self.p0[1] + dy * 0.65)
        self.p2 = top
        self.color = color
        self.delay = delay
        self.radius = random.uniform(34, 44)
        self.phase = random.uniform(0, math.tau)
        self.sway_amp = random.uniform(3, 7)
        self.rot = random.uniform(0, math.tau)
        self.leaves = [(0.35, -1), (0.55, 1)]
        self.tip = None
        self.g = 0.0

    def curve_point(self, t, frame):
        u = 1 - t
        x = u * u * self.p0[0] + 2 * u * t * self.p1[0] + t * t * self.p2[0]
        y = u * u * self.p0[1] + 2 * u * t * self.p1[1] + t * t * self.p2[1]
        sway = self.sway_amp * math.sin(frame * 0.03 + self.phase)
        return x + sway * t * t, y

    def draw_stem(self, screen, frame):
        g = ease((frame - self.delay) / GROW_FRAMES)
        self.g = g
        if g <= 0:
            self.tip = None
            return
        n = 40
        pts = [self.curve_point(g * i / n, frame) for i in range(n + 1)]
        pygame.draw.lines(screen, STEM_COLOR, False, pts, 4)
        self.tip = pts[-1]

        for t_leaf, side in self.leaves:
            if g > t_leaf:
                lg = ease((g - t_leaf) / 0.3)
                lx, ly = self.curve_point(t_leaf, frame)
                ang = -math.pi / 2 + side * 0.9
                poly = petal_points(lx, ly, ang, 48 * lg, 15 * lg)
                pygame.draw.polygon(screen, LEAF_COLOR, poly)
                pygame.draw.polygon(screen, darker(LEAF_COLOR, 0.3), poly, 1)

    def draw_head(self, screen, frame):
        if self.tip is None:
            return
        cx, cy = self.tip
        b = ease((frame - self.delay - GROW_FRAMES) / BLOOM_FRAMES)
        if b <= 0:
            pygame.draw.circle(screen, (60, 170, 85), (int(cx), int(cy)), 5)
            return

        R = self.radius * b
        spin = self.rot + frame * 0.004
        outline = darker(self.color, 0.35)
        inner_color = lighter(self.color, 0.35)

        for k in range(8):  
            ang = spin + k * math.tau / 8
            poly = petal_points(cx, cy, ang, R, R * 0.42)
            pygame.draw.polygon(screen, self.color, poly)
            pygame.draw.polygon(screen, outline, poly, 1)
        for k in range(6):  
            ang = spin + math.tau / 16 + k * math.tau / 6
            poly = petal_points(cx, cy, ang, R * 0.65, R * 0.28)
            pygame.draw.polygon(screen, inner_color, poly)
        pygame.draw.circle(screen, (255, 205, 70), (int(cx), int(cy)), max(2, int(R * 0.2)))
        pygame.draw.circle(screen, (210, 140, 30), (int(cx), int(cy)), max(2, int(R * 0.2)), 2)


def make_wrapper():
    """Papel de regalo con lazo, dibujado una sola vez."""
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    paper = (245, 222, 214)
    pygame.draw.polygon(surf, paper, [(CX - 110, 640), (CX + 110, 640), (CX + 26, 840), (CX - 26, 840)])
    pygame.draw.polygon(surf, (225, 190, 190), [(CX - 110, 640), (CX, 720), (CX - 26, 840)])
    pygame.draw.polygon(surf, (225, 190, 190), [(CX + 110, 640), (CX, 720), (CX + 26, 840)])
    pygame.draw.polygon(surf, (255, 242, 236), [(CX - 110, 640), (CX + 110, 640), (CX, 720)])
    ribbon = (200, 40, 80)
    for ang in (math.pi + 0.35, -0.35):
        poly = petal_points(CX, 722, ang, 56, 22)
        pygame.draw.polygon(surf, ribbon, poly)
        pygame.draw.polygon(surf, darker(ribbon, 0.3), poly, 2)
    pygame.draw.circle(surf, darker(ribbon, 0.15), (CX, 722), 10)
    return surf.convert_alpha()


def build_message(text):
    lines = text.split("\n")
    size = 64
    while size > 20:
        font = pygame.font.SysFont(FONT_NAMES, size)
        if max(font.size(line)[0] for line in lines) <= WIDTH - 70:
            break
        size -= 2
    line_h = int(font.get_linesize() * 1.1)
    surf = pygame.Surface((WIDTH, line_h * len(lines)), pygame.SRCALPHA)
    for i, line in enumerate(lines):
        img = font.render(line, True, TEXT_COLOR)
        surf.blit(img, img.get_rect(midtop=(WIDTH // 2, i * line_h)))
    return surf.convert_alpha()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Blooming Bouquet")
    clock = pygame.time.Clock()

    # Fondo degradado
    background = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        k = 1 - y / HEIGHT
        pygame.draw.line(background, (int(8 + 24 * k), int(4 + 8 * k), int(14 + 32 * k)),
                         (0, y), (WIDTH, y))

    # Crear las flores
    angles = [-38 + 76 * i / (NUM_FLOWERS - 1) for i in range(NUM_FLOWERS)]
    order = sorted(range(NUM_FLOWERS), key=lambda i: abs(angles[i]))
    flowers = []
    for rank, i in enumerate(order):
        a = angles[i]
        length = 430 - 120 * abs(a) / 38 + random.uniform(-15, 15)
        color = FLOWER_COLORS[rank % len(FLOWER_COLORS)]
        flowers.append(Flower(a, length, color, 30 + rank * 18))

    bloom_done = max(f.delay for f in flowers) + GROW_FRAMES + BLOOM_FRAMES
    text_start = bloom_done + 10

    wrapper = make_wrapper()
    message = build_message(MESSAGE)

    # Luciérnagas / polen flotando
    fireflies = [[random.uniform(0, WIDTH), random.uniform(0, HEIGHT),
                  random.uniform(0, math.tau), random.uniform(0.2, 0.7)] for _ in range(45)]
    falling = []

    frame = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                running = False

        frame += 1
        screen.blit(background, (0, 0))

        for f in fireflies:
            f[1] -= f[3]
            if f[1] < -5:
                f[1] = HEIGHT + 5
                f[0] = random.uniform(0, WIDTH)
            v = 0.5 + 0.5 * math.sin(frame * 0.05 + f[2])
            col = (int(255 * v), int(220 * v), int(120 * v))
            pygame.draw.circle(screen, col, (int(f[0] + math.sin(frame * 0.02 + f[2]) * 10), int(f[1])), 2)

        # Tallos y hojas
        for fl in flowers:
            fl.draw_stem(screen, frame)

        # Papel de regalo 
        wrapper.set_alpha(int(255 * min(1.0, frame / 40)))
        screen.blit(wrapper, (0, 0))

        # Cabezas de las flores 
        for fl in sorted(flowers, key=lambda f: -f.delay):
            fl.draw_head(screen, frame)

        # Pétalos que caen
        if FALLING_PETALS and frame > bloom_done and frame % 6 == 0:
            fl = random.choice(flowers)
            if fl.tip:
                falling.append([fl.tip[0], fl.tip[1], random.uniform(-0.4, 0.4),
                                random.uniform(0.8, 1.6), random.uniform(0, math.tau),
                                lighter(fl.color, 0.1), random.uniform(-0.05, 0.05)])
        for p in falling[:]:
            p[1] += p[3]
            p[0] += p[2] + math.sin(frame * 0.04 + p[4]) * 0.6
            p[4] += p[6]
            if p[1] > HEIGHT + 20:
                falling.remove(p)
                continue
            pygame.draw.polygon(screen, p[5], petal_points(p[0], p[1], p[4], 13, 6))

        # Mensaje
        if frame > text_start:
            message.set_alpha(min(255, (frame - text_start) * 4))
            screen.blit(message, message.get_rect(center=(CX, 130)))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
