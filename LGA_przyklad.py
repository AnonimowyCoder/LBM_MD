import math
import numpy as np
import pygame
from matplotlib import pyplot as plt

GRID_WIDTH = 50
GRID_HEIGHT = 50
WALL_COLOR = (0, 0, 0)
BG_COLOR = (255, 255, 255)  # White
CELL_SIZE = 9

# Tablica kierunków
directions = [
    [0, 0], [1, 0], [1, 0], [0, 1], [0, 1],
    [1, 1], [1, 1], [1, 1], [1, 1]
]

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
    velocity[:, :, :] = 0.0

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
    walls[0, :] = 1  # Top boundary
    walls[-1, :] = 1  # Bottom boundary
    walls[:, 0] = 1  # Left boundary
    walls[:, -1] = 1  # Right boundary

    return walls


# wymaga wartości w funkcji input, dlatego przed wywołaniem kolziji trzeba wywołać streaming
def collide(lattice, velocity):
    new_lattice = np.copy(lattice)

    # obliczenie wartości funkcji makroskopowych
    concentration = np.sum(lattice[:, :, 0, :], axis=2)
    velocity[:, :, 0] = new_lattice[:, :, 0, 1] + new_lattice[:, :, 0, 5] + new_lattice[:, :, 0, 8] - new_lattice[:, :,
                                                                                                      0,
                                                                                                      2] - new_lattice[
                                                                                                           :, :, 0,
                                                                                                           6] - new_lattice[
                                                                                                                :, :, 0,
                                                                                                                7]
    velocity[:, :, 1] = new_lattice[:, :, 0, 3] + new_lattice[:, :, 0, 5] + new_lattice[:, :, 0, 6] - new_lattice[:, :,
                                                                                                      0,
                                                                                                      4] - new_lattice[
                                                                                                           :, :, 0,
                                                                                                           7] - new_lattice[
                                                                                                                :, :, 0,
                                                                                                                8]

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
    lattice[:, :, 2, :] = lattice[:, :, 1, :]

    # zwracamy concentration, bo jest potrzebne do wizualizacji - to jest parametr który nas interesuje
    return new_lattice, concentration, velocity


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
                new_lattice[h, w, 0, 0] = lattice[h + 1, w, 2, 0]
            else:
                new_lattice[h, w, 0, 0] = lattice[h, w, 2, 2]  # przypadek z odbiciem

            # e
            if w > 0 and walls[h, w - 1] == 0:
                new_lattice[h, w, 0, 1] = lattice[h, w - 1, 2, 1]
            else:
                new_lattice[h, w, 0, 1] = lattice[h, w, 2, 3]

            # s
            if h > 0 and walls[h - 1, w] == 0:
                new_lattice[h, w, 0, 2] = lattice[h - 1, w, 2, 2]
            else:
                new_lattice[h, w, 0, 2] = lattice[h, w, 2, 0]

            # w
            if w < width - 1 and walls[h, w + 1] == 0:
                new_lattice[h, w, 0, 3] = lattice[h, w + 1, 2, 3]
            else:
                new_lattice[h, w, 0, 3] = lattice[h, w, 2, 1]

    return new_lattice


def draw_grid(screen, walls, concentration):
    """
    Draw the grid onto the screen, optimized for performance.
    - Cells are colored based on their concentration value.
    - Walls are drawn separately with a fixed color.
    """

    rows, cols = GRID_HEIGHT, GRID_WIDTH

    # Draw walls
    wall_indices = np.argwhere(walls == 1)  # Get positions of walls
    for row, col in wall_indices:
        pygame.draw.rect(screen, WALL_COLOR,
                         (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Normalize concentration to [0, 1] for colormap mapping
    # norm_concentration = (concentration - np.min(concentration)) / (np.max(concentration) - np.min(concentration))

    # Choose a colormap from Matplotlib (you can try others like 'plasma', 'inferno', 'cividis')
    cmap = plt.get_cmap('viridis')

    # Precompute colors for performance
    colors = (cmap(concentration.flatten())[:, :3] * 255).astype(int)  # RGB scaled to [0, 255]

    # Draw each cell
    for row in range(rows):
        for col in range(cols):
            if walls[row, col]:  # Draw wall
                color = WALL_COLOR
            else:  # Draw concentration cell
                idx = row * cols + col  # Flattened index to match color array
                color = colors[idx]

            pygame.draw.rect(screen, color,
                             (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))


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

        # Draw the current state
        screen.fill(BG_COLOR)
        draw_grid(screen, walls, concentration)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
