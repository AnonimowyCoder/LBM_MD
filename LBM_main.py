# import math
# import numpy as np
# import pygame
#
# GRID_WIDTH = 50
# GRID_HEIGHT = 50
# WALL_COLOR = (255, 0, 255)
# BG_COLOR = (255, 255, 255)  # White
# CELL_SIZE = 10
# THETA = 1
# BOUND = 5
#
#
# def initialize(height, width):
#     lattice = np.zeros((height, width, 3, 4))  # 3 sets of functions, 4 directions each
#     concentration = np.zeros((height, width))  # Separate array for concentration
#
#     left_bound = (width // BOUND) - 1
#     print("left_bound", left_bound)
#
#     # Set concentration for the specified region
#     for h in range(height):
#         for w in range(left_bound):
#             concentration[h, w] = 1.0
#             print(f"Concentration at ({h}, {w}): {concentration[h, w]}")
#
#     # obliczenie rozkładu równowagowego
#     weight = 0.25
#     print(f"\nCalculating equilibrium distribution with weight = {weight}:")
#     for h in range(height):
#         for w in range(width):
#             lattice[h, w, 1, :] = concentration[h, w] * weight
#             print(f"New lattice equilibrium value at ({h},{w}): {lattice[h, w, 1, :]}")
#
#     # obliczenie wartości funkcji wyjściowej jako przypisanie wartości funkcji równowagowej
#     # wynika to z uproszczenia wzoru poprzez zastosowanie theta=1
#     print(f"\nCalculating final lattice values with THETA = {THETA}:")
#     for h in range(height):
#         for w in range(width):
#             lattice[h, w, 2, :] = lattice[h, w, 0, :] + (1 / THETA) * (
#                     lattice[h, w, 1, :] - lattice[h, w, 0, :])
#             print(f"New lattice final value at ({h},{w}): {lattice[h, w, 2, :]}")
#
#     return lattice, concentration
#
#
#
# def create_walls(height, width):
#     """
#     Create a wall grid. 1 represents a wall, 0 represents free space.
#     """
#     walls = np.zeros((height, width), dtype=int)
#
#     walls[0:(math.floor(BOUND*(2/5))) * (height // BOUND), width // BOUND] = 1
#     walls[(math.floor(BOUND*(3/5)) * (height // BOUND)):height, width // BOUND] = 1
#
#     return walls
#
#
# # wymaga wartości w funkcji input, dlatego przed wywołaniem kolziji trzeba wywołać streaming
# def collide(lattice):
#     height, width = GRID_HEIGHT, GRID_WIDTH
#     new_lattice = np.copy(lattice)
#
#     # Initialize the concentration array
#     concentration = np.zeros((height, width))
#
#     # obliczenie stężenie jako suma funkcji wejściowych z kierunków
#     for h in range(height):
#         for w in range(width):
#             concentration[h, w] = np.sum(lattice[h, w, 0, :])
#
#     # obliczenie rozkładu równowagowego
#     weight = 0.25
#     for h in range(height):
#         for w in range(width):
#             new_lattice[h, w, 1, :] = concentration[h, w] * weight
#
#     # obliczenie wartości funkcji wyjściowej jako przypisanie wartości funkcji równowagowej
#     # wynika to z uproszczenia wzoru poprzez zastosowanie theta=1
#     for h in range(height):
#         for w in range(width):
#             new_lattice[h, w, 2, :] = new_lattice[h, w, 0, :] + (1 / THETA) * (
#                     new_lattice[h, w, 1, :] - new_lattice[h, w, 0, :])
#
#     # zwracamy concentration, bo jest potrzebne do wizualizacji - to jest parametr który nas interesuje
#     return new_lattice, concentration
#
# def collide_debug(lattice):
#     height, width = GRID_HEIGHT, GRID_WIDTH
#     new_lattice = np.copy(lattice)
#
#     # Initialize the concentration array
#     concentration = np.zeros((height, width))
#
#     # obliczenie stężenie jako suma funkcji wejściowych z kierunków
#     print("Calculating concentration:")
#     for h in range(height):
#         for w in range(width):
#             concentration[h, w] = np.sum(lattice[h, w, 0, :])
#             print(f"Concentration at ({h},{w}): {concentration[h, w]}")
#
#     # obliczenie rozkładu równowagowego
#     weight = 0.25
#     print(f"\nCalculating equilibrium distribution with weight = {weight}:")
#     for h in range(height):
#         for w in range(width):
#             new_lattice[h, w, 1, :] = concentration[h, w] * weight
#             print(f"New lattice equilibrium value at ({h},{w}): {new_lattice[h, w, 1, :]}")
#
#     # obliczenie wartości funkcji wyjściowej jako przypisanie wartości funkcji równowagowej
#     # wynika to z uproszczenia wzoru poprzez zastosowanie theta=1
#     print(f"\nCalculating final lattice values with THETA = {THETA}:")
#     for h in range(height):
#         for w in range(width):
#             new_lattice[h, w, 2, :] = new_lattice[h, w, 0, :] + (1 / THETA) * (
#                     new_lattice[h, w, 1, :] - new_lattice[h, w, 0, :])
#             print(f"New lattice final value at ({h},{w}): {new_lattice[h, w, 2, :]}")
#
#     # zwracamy concentration, bo jest potrzebne do wizualizacji - to jest parametr który nas interesuje
#     return new_lattice, concentration
#
# # konwencja kierunków:
# #                                           n = 0, e = 1, s = 2, w = 3
# def streaming(lattice, walls):
#     height, width = GRID_HEIGHT, GRID_WIDTH
#     new_lattice = np.zeros((height, width, 3, 4))  # 3 sets of functions, 4 directions each
#     for h in range(height):
#         for w in range(width):
#             if walls[h, w] == 1:
#                 continue
#             # przypisanie wartości x_skladowej funkcji outlet z komórki do wartosci x_skladowej funkcji inlet aktualnej komórki
#             # n
#             if h < height - 1 and walls[h + 1, w] == 0:  # przypadek bez odbicia
#                 new_lattice[h, w, 0, 0] = lattice[h + 1, w, 2, 0]
#             else:
#                 new_lattice[h, w, 0, 0] = lattice[h, w, 2, 2]  # przypadek z odbiciem
#
#             # e
#             if w > 0 and walls[h, w - 1] == 0:
#                 new_lattice[h, w, 0, 1] = lattice[h, w - 1, 2, 1]
#             else:
#                 #print("jest w warunku odbicia od lewej ściany")
#                 new_lattice[h, w, 0, 1] = lattice[h, w, 2, 3]
#
#             # s
#             if h > 0 and walls[h - 1, w] == 0:
#                 new_lattice[h, w, 0, 2] = lattice[h - 1, w, 2, 2]
#             else:
#                 new_lattice[h, w, 0, 2] = lattice[h, w, 2, 0]
#
#             # w
#             if w < width - 1 and walls[h, w + 1] == 0:
#                 new_lattice[h, w, 0, 3] = lattice[h, w + 1, 2, 3]
#             else:
#                 #print("jest w warunku odbicia od prawej ściany")
#                 new_lattice[h, w, 0, 3] = lattice[h, w, 2, 1]
#
#     return new_lattice
#
# def streaming_debug(lattice, walls):
#     height, width = GRID_HEIGHT, GRID_WIDTH
#     new_lattice = np.zeros((height, width, 3, 4))  # 3 sets of functions, 4 directions each
#
#     for h in range(height):
#         for w in range(width):
#             print(f"Processing cell ({h}, {w})")
#             if walls[h, w] == 1:
#                 print("sciana!!!!!!!!!!!!!!!!!")
#                 continue
#
#             # N (North) direction
#             if h < height - 1 and walls[h + 1, w] == 0:  # No wall, free space
#                 print(f"  Moving from South to North: lattice[{h + 1}, {w}, 2, 0], val = {lattice[h + 1, w, 2, 0]} -> new_lattice[{h}, {w}, 0, 0], val = {new_lattice[h, w, 0, 0]}")
#                 new_lattice[h, w, 0, 0] = lattice[h + 1, w, 2, 0]
#             else:
#                 print(f"  Wall or out of bounds at North, reflecting: lattice[{h}, {w}, 2, 2], val = {lattice[h, w, 2, 2]} -> new_lattice[{h}, {w}, 0, 0], val = {new_lattice[h, w, 0, 0]}")
#                 new_lattice[h, w, 0, 0] = lattice[h, w, 2, 2]  # Reflection
#
#             # E (East) direction
#             if w > 0 and walls[h, w - 1] == 0:  # No wall, free space
#                 print(f"  Moving from West to East: lattice[{h}, {w - 1}, 2, 1], val = {lattice[h, w - 1, 2, 1]} -> new_lattice[{h}, {w}, 0, 1], val = {new_lattice[h, w, 0, 1]}")
#                 new_lattice[h, w, 0, 1] = lattice[h, w - 1, 2, 1]
#             else:
#                 print(f"  Wall or out of bounds at East, reflecting: lattice[{h}, {w}, 2, 3], val = {lattice[h, w, 2, 3]} -> new_lattice[{h}, {w}, 0, 1], val = {new_lattice[h, w, 0, 1]}")
#                 new_lattice[h, w, 0, 1] = lattice[h, w, 2, 3]  # Reflection
#
#             # S (South) direction
#             if h > 0 and walls[h - 1, w] == 0:  # No wall, free space
#                 print(f"  Moving from North to South: lattice[{h - 1}, {w}, 0, 2], val = {lattice[h - 1, w, 0, 2]} -> new_lattice[{h}, {w}, 0, 2], val = {new_lattice[h, w, 0, 2]}")
#                 new_lattice[h, w, 0, 2] = lattice[h - 1, w, 2, 2]
#             else:
#                 print(f"  Wall or out of bounds at South, reflecting: lattice[{h}, {w}, 2, 0], val = {lattice[h, w, 2, 0]} -> new_lattice[{h}, {w}, 0, 2], val = {new_lattice[h, w, 0, 2]}")
#                 new_lattice[h, w, 0, 2] = lattice[h, w, 2, 0]  # Reflection
#
#             # W (West) direction
#             if w < width - 1 and walls[h, w + 1] == 0:  # No wall, free space
#                 print(f"  Moving from East to West: lattice[{h}, {w + 1}, 0, 3], val = {lattice[h, w + 1, 0, 3]} -> new_lattice[{h}, {w}, 0, 3], val = {new_lattice[h, w, 0, 3]}")
#                 new_lattice[h, w, 0, 3] = lattice[h, w + 1, 2, 3]
#             else:
#                 print(f"  Wall or out of bounds at West, reflecting: lattice[{h}, {w}, 2, 1], val = {lattice[h, w, 2, 1]} -> new_lattice[{h}, {w}, 0, 3], val = {new_lattice[h, w, 0, 3]}")
#                 new_lattice[h, w, 0, 3] = lattice[h, w, 2, 1]  # Reflection
#
#     return new_lattice
#
# def draw_grid(screen, walls, concentration):
#     """
#     Draw the grid onto the screen, optimized for performance.
#     - Cells are colored based on their concentration value.
#     - Walls are drawn separately with a fixed color.
#     """
#
#     rows, cols = GRID_HEIGHT, GRID_WIDTH
#
#     # Draw walls
#     wall_indices = np.argwhere(walls == 1)  # Get positions of walls
#     for row, col in wall_indices:
#         pygame.draw.rect(screen, WALL_COLOR,
#                          (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
#
#     # Draw concentration cells
#     for row in range(rows):
#         for col in range(cols):
#             conc = concentration[row, col]  # Get the concentration for this cell
#
#             # Map concentration to a grayscale intensity (0 to 255)
#             intensity = 255 - int(conc * 255)  # Scale concentration to 0-255 range for intensity
#             color = (intensity, intensity, intensity)  # Grayscale color
#
#             # Draw the rectangle with the color corresponding to concentration
#             if walls[row, col] == 0:
#                 pygame.draw.rect(screen, color,
#                                  (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
#
#
# def main():
#     pygame.init()
#     screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
#     pygame.display.set_caption("LBM")
#     clock = pygame.time.Clock()
#
#     # Initialize the grid
#     lattice, concentration = initialize(GRID_HEIGHT, GRID_WIDTH)
#
#     walls = create_walls(GRID_HEIGHT, GRID_WIDTH)
#
#     running = True
#
#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#             # Update the simulation
#
#         lattice = streaming(lattice, walls)
#         lattice, concentration = collide(lattice)
#
#         # Draw the current state
#         screen.fill(BG_COLOR)
#         draw_grid(screen, walls, concentration)
#         pygame.display.flip()
#
#         #clock.tick(1)
#
#     pygame.quit()
#
#
# if __name__ == "__main__":
#     main()
