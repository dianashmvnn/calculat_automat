"""
Cellular Automata Engines: 1D Elementary CA and 2D Game of Life.
"""

import numpy as np


class ElementaryCA:
    """1D elementary cellular automaton (Wolfram rules)."""
    def __init__(self, rule: int, width: int, init_type: str = 'random', density: float = 0.5):
        self.rule = rule
        self.width = width
        self.init_type = init_type
        self.density = density
        self.state = self._init_state()
        # Build rule table: index 0..7 (binary triplet) -> new bit
        self.rule_bits = [(rule >> i) & 1 for i in range(8)]

    def _init_state(self):
        if self.init_type == 'random':
            return np.random.choice([0, 1], size=self.width, p=[1 - self.density, self.density])
        elif self.init_type == 'single':
            state = np.zeros(self.width, dtype=int)
            state[self.width // 2] = 1
            return state
        elif self.init_type == 'periodic':
            return np.array([1 if i % 2 == 0 else 0 for i in range(self.width)])
        else:  # default random
            return np.random.choice([0, 1], size=self.width, p=[0.5, 0.5])

    def next(self):
        new = np.zeros_like(self.state)
        for i in range(self.width):
            left = self.state[(i - 1) % self.width]
            center = self.state[i]
            right = self.state[(i + 1) % self.width]
            pattern = (left << 2) | (center << 1) | right
            new[i] = self.rule_bits[7 - pattern]
        self.state = new
        return self.state

    def evolve(self, steps: int):
        """Return a 2D array of shape (steps+1, width)."""
        history = [self.state.copy()]
        for _ in range(steps):
            self.next()
            history.append(self.state.copy())
        return np.array(history)


class GameOfLife:
    """Conway's Game of Life (2D)."""
    def __init__(self, width: int, height: int, init_type: str = 'random', density: float = 0.5):
        self.width = width
        self.height = height
        self.init_type = init_type
        self.density = density
        self.state = self._init_state()

    def _init_state(self):
        if self.init_type == 'random':
            return np.random.choice([0, 1], size=(self.height, self.width),
                                    p=[1 - self.density, self.density])
        elif self.init_type == 'glider':
            state = np.zeros((self.height, self.width), dtype=int)
            # place a glider near center
            cx, cy = self.width // 2, self.height // 2
            glider = np.array([[0, 1, 0],
                               [0, 0, 1],
                               [1, 1, 1]])
            state[cy-1:cy+2, cx-1:cx+2] = glider
            return state
        else:
            return np.random.choice([0, 1], size=(self.height, self.width), p=[0.9, 0.1])

    def next(self):
        new_state = np.zeros_like(self.state)
        for i in range(self.height):
            for j in range(self.width):
                # count live neighbors with toroidal boundary
                neighbors = (
                    self.state[(i-1) % self.height, (j-1) % self.width] +
                    self.state[(i-1) % self.height, j] +
                    self.state[(i-1) % self.height, (j+1) % self.width] +
                    self.state[i, (j-1) % self.width] +
                    self.state[i, (j+1) % self.width] +
                    self.state[(i+1) % self.height, (j-1) % self.width] +
                    self.state[(i+1) % self.height, j] +
                    self.state[(i+1) % self.height, (j+1) % self.width]
                )
                if self.state[i, j] == 1:
                    new_state[i, j] = 1 if neighbors in (2, 3) else 0
                else:
                    new_state[i, j] = 1 if neighbors == 3 else 0
        self.state = new_state
        return self.state

    def evolve(self, steps: int):
        """Return a list of states (each is 2D array)."""
        history = [self.state.copy()]
        for _ in range(steps):
            self.next()
            history.append(self.state.copy())
        return np.array(history)