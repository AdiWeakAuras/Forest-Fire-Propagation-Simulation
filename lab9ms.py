import pygame
import random
import matplotlib.pyplot as plt
import numpy as np

# --- 1. SETTINGS & EMPIRICAL PARAMETERS ---
GRID_SIZE = 60
CELL_SIZE = 10
P_BASE = 0.28         # Researched Base Probability
WIND_MODIFIER = 1.45   # Researched North Wind Factor
BURN_TICKS = 6        # Researched Duration (NWCG)

# State Constants
EMPTY, TREE, BURNING, ASH = 0, 1, 2, 3
COLORS = {
    EMPTY: (0, 0, 0),        # Black
    TREE: (34, 139, 34),     # Forest Green
    BURNING: (255, 69, 0),   # Red-Orange
    ASH: (105, 105, 105)     # Dim Gray
}

class WildfireModel:
    def __init__(self, density, has_firebreak=False):
        # Initialize grid based on density
        self.grid = np.random.choice([TREE, EMPTY], size=(GRID_SIZE, GRID_SIZE), p=[density, 1-density])
        self.age = np.zeros((GRID_SIZE, GRID_SIZE))
        self.history = []
        
        if has_firebreak:
            # Resource 2 Application: Man-made fuel removal (Firebreak)
            self.grid[:, GRID_SIZE//2] = EMPTY

        # Ignite the bottom row to start the simulation
        self.grid[GRID_SIZE-1, :] = np.where(self.grid[GRID_SIZE-1, :] == TREE, BURNING, EMPTY)

    def update(self):
        new_grid = self.grid.copy()
        current_active_fire = 0
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c] == BURNING:
                    current_active_fire += 1
                    self.age[r][c] += 1
                    
                    # If burn time exceeded, turn to ash
                    if self.age[r][c] >= BURN_TICKS:
                        new_grid[r][c] = ASH
                        continue
                    
                    # Spread to neighbors
                    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and self.grid[nr][nc] == TREE:
                            prob = P_BASE
                            # Resource 1 Application: Wind pushes fire North (upwards)
                            if dr == -1: prob *= WIND_MODIFIER 
                            
                            if random.random() < prob:
                                new_grid[nr][nc] = BURNING
        
        self.grid = new_grid
        self.history.append(current_active_fire)
        return current_active_fire

def run_experiment(name, density, firebreak):
    pygame.init()
    screen = pygame.display.set_mode((GRID_SIZE*CELL_SIZE, GRID_SIZE*CELL_SIZE))
    pygame.display.set_caption(f"Lab 9: {name} Scenario")
    
    sim = WildfireModel(density, firebreak)
    clock = pygame.time.Clock()
    
    running = True
    while running and (len(sim.history) < 2 or sim.history[-1] > 0):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            
        sim.update()
        screen.fill((0,0,0))
        
        # Draw Grid
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if sim.grid[r][c] != EMPTY:
                    pygame.draw.rect(screen, COLORS[sim.grid[r][c]], 
                                     (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1))
        
        pygame.display.flip()
        clock.tick(20) # Speed of simulation
        
        if len(sim.history) > 150: break # Safety cutoff

    pygame.quit()
    return sim.history

# --- RUNNING THE COMPARISON ---
print("Running Scenario A: Natural Forest...")
stats_natural = run_experiment("Natural", 0.80, False)

print("Running Scenario B: Managed Forest (Firebreaks)...")
stats_managed = run_experiment("Managed", 0.80, True)

# --- VISUAL PRESENTATION 2: DATA PLOT ---
plt.figure(figsize=(10, 6))
plt.plot(stats_natural, label="Scenario A: Natural Spread", color='red', linewidth=2)
plt.plot(stats_managed, label="Scenario B: Firebreak Managed", color='blue', linestyle='--')
plt.title("Comparison of Fire Intensity Over Time")
plt.xlabel("Simulation Ticks")
plt.ylabel("Number of Cells Currently Burning")
plt.legend()
plt.grid(True)
plt.show()