import math
import numpy as np
import pygame
from matplotlib import pyplot as plt, cm

GRID_WIDTH = 200
GRID_HEIGHT = 200
WALL_COLOR = (0, 0, 0)
BG_COLOR = (255, 255, 255)  # White
CELL_SIZE = 5

# Tablica kierunków
directions = [
    [0, 0], [1, 0], [1, 0], [0, 1], [0, 1],
    [1, 1], [1, 1], [1, 1], [1, 1]
]

d = {
    "n": 3,  # północ (north)
    "s": 4,  # południe (south)
    "e": 1,  # wschód (east)
    "w": 2,  # zachód (west)
    "ne": 5, # północny-wschód (northeast)
    "nw": 6, # północny-zachód (northwest)
    "se": 8, # południowy-wschód (southeast)
    "sw": 7, # południowy-zachód (southwest)
    "c": 0   # centralny kierunek (center)
}

# Tablica wag
weights = [4 / 9, 1 / 9, 1 / 9, 1 / 9, 1 / 9, 1 / 36, 1 / 36, 1 / 36, 1 / 36]


def initialize(height, width):
    lattice = np.zeros((height, width, 3, 9))  # 3 sets of functions, 9 directions each
    concentration = np.zeros((height, width))  # Separate array for concentration
    velocity = np.zeros((height, width, 2))  # osobna tablica dla velocity - dwuwymiarowa

    left_bound = (width // 5)
    print("left_bound", left_bound)

    # inicjalizacja wartości makroskopowych
    # Warunki początkowe:
    # gęstość ρ = 1.0 w jednej części i ρ = 0.95-0.99 w innej;
    # prędkość w całym obszarze u = 0.0.
    concentration[:, :left_bound] = 1.0
    concentration[:, left_bound:] = 0.95
    velocity[:, :, ] = 0.0

    # Obliczanie funkcji równowagowej
    for i in range(len(directions)):
        direction = directions[i]  # Kierunek
        weight = weights[i]  # Waga

        # Iloczyn skalarny direction * velocity dla całej siatki
        dir_velocity = velocity[:, :, 0] * direction[0] + velocity[:, :, 1] * direction[1]

        # Funkcja równowagowa według wzoru
        eq_function = (
                weight * concentration *
                (1 + 3 * dir_velocity + 4.5 * dir_velocity ** 2 - 1.5 * np.sum(velocity ** 2, axis=2))
        )

        # Przypisanie funkcji równowagowej
        lattice[:, :, 1, i] = eq_function

    # obliczenie wartości funkcji wyjściowej jako przypisanie wartości funkcji równowagowej
    # wynika to z uproszczenia wzoru poprzez zastosowanie theta=1
    lattice[:, :, 2, :] = lattice[:, :, 1, :]

    return lattice, concentration, velocity


def create_walls(height, width):
    """
    Create a wall grid. 1 represents a wall, 0 represents free space.
    """
    # Initialize grid with zeros
    walls = np.zeros((height, width), dtype=int)

    # Add internal vertical wall as before
    walls[0:2 * (height // 5), width // 5] = 1
    walls[(3 * (height // 5)):height, width // 5] = 1

    # Add walls around the boundary
    # walls[0, :] = 1  # Top boundary
    # walls[-1, :] = 1  # Bottom boundary
    # walls[:, 0] = 1  # Left boundary
    # walls[:, -1] = 1  # Right boundary

    return walls


# wymaga wartości w funkcji input, dlatego przed wywołaniem kolziji trzeba wywołać streaming
def collide(lattice, velocity):
    new_lattice = np.copy(lattice)

    # Obliczenie wartości funkcji makroskopowych
    concentration = np.sum(lattice[:, :, 0, :], axis=2)
    print("=== KROK 1: Gestosc ===")
    print(f"Min: {np.min(concentration):.6f}, Max: {np.max(concentration):.6f}, Średnia: {np.mean(concentration):.6f}")

    velocity[:, :, 0] = (
            new_lattice[:, :, 0, 1] + new_lattice[:, :, 0, 5] + new_lattice[:, :, 0, 8]
            - new_lattice[:, :, 0, 2] - new_lattice[:, :, 0, 6] - new_lattice[:, :, 0, 7]
    )
    velocity[:, :, 1] = (
            new_lattice[:, :, 0, 3] + new_lattice[:, :, 0, 5] + new_lattice[:, :, 0, 6]
            - new_lattice[:, :, 0, 4] - new_lattice[:, :, 0, 7] - new_lattice[:, :, 0, 8]
    )
    # print("=== KROK 2: Prędkość ===")
    # print(
    #     f"Velocity X - Min: {np.min(velocity[:, :, 0]):.6f}, Max: {np.max(velocity[:, :, 0]):.6f}, Średnia: {np.mean(velocity[:, :, 0]):.6f}")
    # print(
    #     f"Velocity Y - Min: {np.min(velocity[:, :, 1]):.6f}, Max: {np.max(velocity[:, :, 1]):.6f}, Średnia: {np.mean(velocity[:, :, 1]):.6f}")

    # Obliczanie funkcji równowagowej
    for i in range(len(directions)):
        direction = directions[i]  # Kierunek
        weight = weights[i]  # Waga

        # Iloczyn skalarny direction * velocity dla całej siatki
        dir_velocity = velocity[:, :, 0] * direction[0] + velocity[:, :, 1] * direction[1]

        # Funkcja równowagowa według wzoru
        eq_function = (
                weight * concentration *
                (1 + 3 * dir_velocity + 4.5 * dir_velocity ** 2 - 1.5 * np.sum(velocity ** 2, axis=2))
        )
        lattice[:, :, 1, i] = eq_function

        # # Debug dla każdej funkcji równowagowej
        # if i == 0:  # Drukujemy tylko dla pierwszego kierunku jako przykład
        #     print(f"=== KROK 3: Funkcja równowagowa dla kierunku {i} ===")
        #     print(
        #         f"Min: {np.min(eq_function):.6f}, Max: {np.max(eq_function):.6f}, Średnia: {np.mean(eq_function):.6f}")

    # Relaksacja
    theta = 1.2
    lattice[:, :, 2, :] = lattice[:, :, 0, :] + (1 / theta) * (lattice[:, :, 1, :] - lattice[:, :, 0, :])
    # print("=== KROK 4: Zaktualizowane wartości funkcji output===")
    # print(
    #     f"Min: {np.min(lattice[:, :, 2, :]):.6f}, Max: {np.max(lattice[:, :, 2, :]):.6f}, Średnia: {np.mean(lattice[:, :, 2, :]):.6f}")

    # Zwracamy dane
    return lattice, concentration, velocity


def streaming(lattice, walls):
    height, width = GRID_HEIGHT, GRID_WIDTH
    new_lattice = np.zeros((height, width, 3, 9))  # 3 sets of functions, 9 directions each
    for h in range(height):
        for w in range(width):
            if walls[h, w] == 1:
                continue
            # przypisanie wartości x_skladowej funkcji outlet z komórki do wartosci x_skladowej funkcji inlet aktualnej komórki
            # n
            if h < height - 1 and walls[h + 1, w] == 0:  # przypadek bez odbicia
                new_lattice[h, w, 0, d["n"]] = lattice[h + 1, w, 2, d["n"]]
            else:
                new_lattice[h, w, 0, d["n"]] = lattice[h, w, 2,d["s"]]  # przypadek z odbiciem

            # e
            if w > 0 and walls[h, w - 1] == 0:
                new_lattice[h, w, 0, d["e"]] = lattice[h, w - 1, 2,d["e"]]
            else:
                new_lattice[h, w, 0, d["e"]] = lattice[h, w, 2,d["w"]]

            # s
            if h > 0 and walls[h - 1, w] == 0:
                new_lattice[h, w, 0, d["s"]] = lattice[h - 1, w, 2, d["s"]]
            else:
                new_lattice[h, w, 0,d["s"]] = lattice[h, w, 2, d["n"]]

            # w
            if w < width - 1 and walls[h, w + 1] == 0:
                new_lattice[h, w, 0, d["w"]] = lattice[h, w + 1, 2, d["w"]]
            else:
                new_lattice[h, w, 0, d["w"]] = lattice[h, w, 2,d["e"]]

            # ne
            if h < height - 1 and w >0 and walls[h + 1, w] == 0 and walls[h, w - 1] == 0:  # przypadek bez odbicia
                new_lattice[h, w, 0, d["ne"]] = lattice[h + 1, w-1, 2, d["ne"]]
            else:
                new_lattice[h, w, 0, d["ne"]] = lattice[h, w, 2,d["sw"]]  # przypadek z odbiciem

            # se
            if h >0 and w >0 and walls[h -1, w] == 0 and walls[h, w -1] == 0:  # przypadek bez odbicia
                new_lattice[h, w, 0, d["se"]] = lattice[h - 1, w-1, 2, d["se"]]
            else:
                new_lattice[h, w, 0, d["se"]] = lattice[h, w, 2,d["nw"]]  # przypadek z odbiciem

            # sw
            if h >0 and w < width - 1 and walls[h -1, w] == 0 and walls[h, w +1] == 0:  # przypadek bez odbicia
                new_lattice[h, w, 0, d["sw"]] = lattice[h - 1, w+1, 2, d["sw"]]
            else:
                new_lattice[h, w, 0, d["sw"]] = lattice[h, w, 2,d["ne"]]  # przypadek z odbiciem

            # nw
            if h < height - 1 and w < width - 1 and walls[h +1, w] == 0 and walls[h, w +1] == 0:  # przypadek bez odbicia
                new_lattice[h, w, 0, d["nw"]] = lattice[h + 1, w+1, 2, d["nw"]]
            else:
                new_lattice[h, w, 0, d["nw"]] = lattice[h, w, 2,d["se"]]  # przypadek z odbici

            new_lattice[h,w,0,d["c"]] = lattice[h, w, 2,d["c"]]

    return new_lattice


def draw_grid(screen, walls, velocity):
    """
    Draw the grid onto the screen, optimized for performance.
    - Velocity is visualized as a gradient.
    - Walls are drawn separately with a fixed color.
    """

    rows, cols = velocity.shape[:2]  # Get grid dimensions

    # Calculate speed (magnitude of velocity vector) for each cell
    speed = np.sqrt(velocity[:, :, 0]**2 + velocity[:, :, 1]**2)

    # Normalize speed to [0, 1] for consistent gradient scaling
    norm_speed = (speed - np.min(speed)) / (np.max(speed) - np.min(speed) + 1e-8)

    # Choose a colormap for speed visualization
    cmap = plt.get_cmap('plasma')

    # Map normalized speed to colors (precompute for performance)
    speed_colors = (cmap(norm_speed.flatten())[:, :3] * 255).astype(int)

    # Draw each cell
    for row in range(rows):
        for col in range(cols):
            if walls[row, col]:  # Draw wall
                color = WALL_COLOR
            else:
                # Get color based only on velocity
                speed_idx = row * cols + col
                color = speed_colors[speed_idx]

            pygame.draw.rect(screen, color,
                             (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_grid_concentration(screen, walls, concentration):
    """
    Draw the grid onto the screen, optimized for performance.
    - Cells are colored based solely on their concentration value.
    - Walls are drawn separately with a fixed color.
    """

    rows, cols = concentration.shape  # Get grid dimensions

    # Normalize concentration to [0, 1] for consistent gradient scaling
    norm_concentration = (concentration - np.min(concentration)) / (np.max(concentration) - np.min(concentration) + 1e-8)

    # Choose a colormap for concentration visualization
    cmap = plt.get_cmap('viridis')

    # Map normalized concentration to colors (precompute for performance)
    concentration_colors = (cmap(norm_concentration.flatten())[:, :3] * 255).astype(int)

    # Draw each cell
    for row in range(rows):
        for col in range(cols):
            if walls[row, col]:  # Draw wall
                color = WALL_COLOR
            else:
                # Get color based on concentration
                conc_idx = row * cols + col
                color = concentration_colors[conc_idx]

            pygame.draw.rect(screen, color,
                             (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def concentration_to_color(concentration):
    min_conc = np.min(concentration)
    max_conc = np.max(concentration)

    # Sprawdź, czy różnica maks-min nie wynosi 0, aby uniknąć dzielenia przez zero
    if max_conc - min_conc == 0:
        norm_conc = np.zeros_like(concentration)  # Jeśli różnica wynosi 0, ustaw wszystkie wartości na 0
    else:
        norm_conc = (concentration - min_conc) / (max_conc - min_conc)

    colormap = cm.plasma(norm_conc)  # Używamy colormap 'plasma'
    return (colormap[:, :, :3] * 255).astype(np.uint8)
# Funkcja wizualizacji

def visualize(concentration, walls):
    color_grid = concentration_to_color(concentration)
    for h in range(GRID_HEIGHT):
        for w in range(GRID_WIDTH):
            if walls[h, w] == 1:
                color_grid[h, w] = [0, 0, 0]  # Kolor ścian na czarno
    return color_grid

# Główna pętla symulacji


def main():
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    pygame.display.set_caption("LBM")
    clock = pygame.time.Clock()

    # Initialize the grid
    lattice, concentration, velocity = initialize(GRID_HEIGHT, GRID_WIDTH)

    walls = create_walls(GRID_HEIGHT, GRID_WIDTH)

    running = True
    paused = True  # Variable to track pause state

    i = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # Toggle pause when the spacebar is pressed
                if event.key == pygame.K_SPACE:
                    paused = not paused

        # Run one iteration if not paused
        if not paused:
            lattice = streaming(lattice, walls)
            lattice, concentration, velocity = collide(lattice, velocity)
            #print(f"predkosc x w wezle 50,20: {velocity[50,20,0]}")

        # Draw the current state
        screen.fill(BG_COLOR)
        draw_grid(screen, walls,  velocity)
        #draw_grid_concentration(screen, walls, concentration)

        # color_grid = visualize(concentration, walls)
        # for h in range(GRID_HEIGHT):
        #     for w in range(GRID_WIDTH):
        #         pygame.draw.rect(screen, color_grid[h, w], (w * CELL_SIZE, h * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        pygame.display.flip()
        i=i+1

    pygame.quit()


if __name__ == "__main__":
    main()