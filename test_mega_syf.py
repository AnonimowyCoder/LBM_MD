import numpy as np
import pygame
from matplotlib import pyplot as plt, cm

GRID_WIDTH = 100
GRID_HEIGHT = 100
WALL_COLOR = (0, 0, 0)
BG_COLOR = (255, 255, 255)  # White
CELL_SIZE = 9


def initialize(height, width):
    lattice = np.zeros((height, width, 3, 4))  # 3 sets of functions, 4 directions each
    concentration = np.zeros((height, width))  # Separate array for concentration

    left_bound = (width // 5)
    print("left_bound", left_bound)

    # inicjalizacja wartości makroskopowych
    concentration[:, :left_bound] = 1.0
    concentration[:, left_bound:] = 0.1

    weight = 0.25  # Waga
    lattice[:,:,1,:] = concentration[:,:,np.newaxis]*weight

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

    weight = 0.25  # Waga
    lattice[:,:,1,] = concentration[:,:,np.newaxis]*weight

    lattice[:,:,2,:] = lattice[:,:,1,:]


    # Zwracamy dane
    return lattice, concentration


def streaming(lattice, walls):
    height, width = GRID_HEIGHT, GRID_WIDTH
    new_lattice = np.zeros((height, width, 3, 4))  # 3 sets of functions, 9 directions each
    for h in range(height):
        for w in range(width):
            if walls[h, w] == 1:
                continue
            # przypisanie wartości x_skladowej funkcji outlet z komórki do wartosci x_skladowej funkcji inlet aktualnej komórki
            # n
            if h < height - 1 and walls[h + 1, w] == 0:  # przypadek bez odbicia
                new_lattice[h, w, 0, 0] = lattice[h + 1, w, 2, 0]
                print(f"new_lattice [{h,w,0,0}] = {lattice[h+1,w,2,0]}")

            else:
                new_lattice[h, w, 0, 0] = lattice[h, w, 2,2]  # przypadek z odbiciem

            # e
            if w > 0 and walls[h, w - 1] == 0:
                new_lattice[h, w, 0, 1] = lattice[h, w - 1, 2,1]
            else:
                new_lattice[h, w, 0, 1] = lattice[h, w, 2,3]

            # s
            if h > 0 and walls[h - 1, w] == 0:
                new_lattice[h, w, 0, 2] = lattice[h - 1, w, 2, 2]
            else:
                new_lattice[h, w, 0,2] = lattice[h, w, 2, 0]

            # w
            if w < width - 1 and walls[h, w + 1] == 0:
                new_lattice[h, w, 0, 3] = lattice[h, w + 1, 2, 3]
            else:
                new_lattice[h, w, 0, 3] = lattice[h, w, 2,1]


    return new_lattice


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
    pygame.display.set_caption("LBM Visualization")
    clock = pygame.time.Clock()

    lattice, concentration = initialize(GRID_HEIGHT, GRID_WIDTH)
    walls = create_walls(GRID_HEIGHT, GRID_WIDTH)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Symulacja LBM
        lattice = streaming(lattice, walls)
        lattice, concentration = collide(lattice)

        # Wizualizacja
        color_grid = visualize(concentration, walls)

        for h in range(GRID_HEIGHT):
            for w in range(GRID_WIDTH):
                pygame.draw.rect(screen, color_grid[h, w], (w * CELL_SIZE, h * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
