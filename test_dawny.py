import math
import numpy as np
import pygame
from matplotlib import pyplot as plt

GRID_WIDTH = 100
GRID_HEIGHT = 100
WALL_COLOR = (0, 0, 0)
BG_COLOR = (255, 255, 255)  # White
CELL_SIZE = 9

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

    left_bound = (width // 5)
    print("left_bound", left_bound)

    # inicjalizacja wartości makroskopowych
    concentration[:, :left_bound] = 1.0

    for i in range(9):
        weight = 1/9  # Waga
        lattice[:,:,1,i] = concentration[:,:]*weight

    lattice[:,:,2,:] = lattice[:,:,1,:]

    return lattice, concentration


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
def collide(lattice):
    new_lattice = np.copy(lattice)

    concentration = np.sum(lattice[:,:,0,:], axis=2)

    # # obliczenie rozkladu rownowagowego
    # for i in range(len(weights)):
    #     weight = weights[i]  # Waga
    #     lattice[:,:,1,i] = concentration[:,:]*weight

    for i in range(9):
        weight = 1/9  # Waga
        lattice[:,:,1,i] = concentration[:,:]*weight

    lattice[:,:,2,:] = lattice[:,:,1,:]


    # Zwracamy dane
    return new_lattice, concentration


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


def main():
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    pygame.display.set_caption("LBM")
    clock = pygame.time.Clock()

    # Initialize the grid
    lattice, concentration= initialize(GRID_HEIGHT, GRID_WIDTH)

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
            lattice, concentration = collide(lattice)

        # Draw the current state
        screen.fill(BG_COLOR)
        # draw_grid(screen, walls,  velocity)
        draw_grid_concentration(screen, walls, concentration)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()