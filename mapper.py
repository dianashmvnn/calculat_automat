"""
Mapping from cellular automaton states to MIDI events.
Fixed to ensure pitch is within 0..127.
"""

import numpy as np


class DirectMapper:
    """
    Direct mapping: each column of the grid corresponds to a pitch (within a scale).
    """
    def __init__(self, history, base_pitch=60, scale_intervals=None, step_duration=0.5):
        self.history = history
        self.base_pitch = base_pitch
        if scale_intervals is None:
            scale_intervals = [0, 2, 4, 5, 7, 9, 11]  # C major
        self.scale_intervals = scale_intervals
        self.step_duration = step_duration
        self.is_2d = len(history.shape) == 3

    def _pitch_from_column(self, col, total_cols):
        # Map column index to a pitch within the scale
        scale_degree = col % len(self.scale_intervals)
        octave_shift = (col // len(self.scale_intervals)) * 12
        pitch = self.base_pitch + self.scale_intervals[scale_degree] + octave_shift
        # CLIP to MIDI range 0..127
        return max(0, min(127, pitch))

    def generate_events(self):
        events = []  # each event: (time_sec, type, pitch, velocity)
        if self.is_2d:
            steps, height, width = self.history.shape
            for step in range(steps):
                t = step * self.step_duration
                state_2d = self.history[step]
                for row in range(height):
                    for col in range(width):
                        if state_2d[row, col] == 1:
                            pitch = self._pitch_from_column(col, width)
                            events.append((t, 'note_on', pitch, 80))
                            events.append((t + self.step_duration, 'note_off', pitch, 0))
        else:
            steps, width = self.history.shape
            for step in range(steps):
                t = step * self.step_duration
                row = self.history[step]
                for col, active in enumerate(row):
                    if active == 1:
                        pitch = self._pitch_from_column(col, width)
                        events.append((t, 'note_on', pitch, 80))
                        events.append((t + self.step_duration, 'note_off', pitch, 0))
        return events


class IntervalMapper:
    """
    Interval mapping: consecutive active cells generate intervals.
    """
    def __init__(self, history, base_pitch=60, scale_intervals=None, step_duration=0.5):
        self.history = history
        self.base_pitch = base_pitch
        if scale_intervals is None:
            scale_intervals = [0, 2, 4, 7, 9]  # pentatonic
        self.scale_intervals = scale_intervals
        self.step_duration = step_duration
        self.is_2d = len(history.shape) == 3

    def _closest_pitch_in_scale(self, pitch):
        # Find nearest pitch in the scale
        if not self.scale_intervals:
            return max(0, min(127, pitch))
        base_mod = self.base_pitch % 12
        scale_mods = [(self.base_pitch + d) % 12 for d in self.scale_intervals]
        mod = pitch % 12
        # Find the scale note with minimal circular distance
        best_diff = 12
        best_scale_note = pitch
        for s in scale_mods:
            diff = (mod - s) % 12
            if diff > 6:
                diff = 12 - diff
            if diff < best_diff:
                best_diff = diff
                best_scale_note = (pitch // 12) * 12 + s
                if best_scale_note < pitch - 6:
                    best_scale_note += 12
                elif best_scale_note > pitch + 6:
                    best_scale_note -= 12
        return max(0, min(127, best_scale_note))

    def generate_events(self):
        events = []
        if self.is_2d:
            steps, height, width = self.history.shape
            last_pitch = self.base_pitch
            for step in range(steps):
                t = step * self.step_duration
                cells = []
                for row in range(height):
                    for col in range(width):
                        if self.history[step, row, col] == 1:
                            cells.append((row, col))
                if cells:
                    row, col = cells[0]
                    interval = (col % 7) - 3  # -3..3
                    new_pitch = last_pitch + interval
                    new_pitch = max(0, min(127, new_pitch))
                    new_pitch = self._closest_pitch_in_scale(new_pitch)
                    events.append((t, 'note_on', new_pitch, 80))
                    events.append((t + self.step_duration, 'note_off', new_pitch, 0))
                    last_pitch = new_pitch
        else:
            steps, width = self.history.shape
            last_pitch = self.base_pitch
            for step in range(steps):
                t = step * self.step_duration
                active_cols = [col for col, val in enumerate(self.history[step]) if val == 1]
                if active_cols:
                    col = active_cols[0]
                    interval = (col % 7) - 3
                    new_pitch = last_pitch + interval
                    new_pitch = max(0, min(127, new_pitch))
                    new_pitch = self._closest_pitch_in_scale(new_pitch)
                    events.append((t, 'note_on', new_pitch, 80))
                    events.append((t + self.step_duration, 'note_off', new_pitch, 0))
                    last_pitch = new_pitch
        return events


class TonnetzMapper:
    """
    Experimental mapping based on Tonnetz.
    Fixed to avoid deprecated np.sum usage and ensure pitch range.
    """
    def __init__(self, history, base_pitch=60, step_duration=0.5):
        self.history = history
        self.base_pitch = base_pitch
        self.step_duration = step_duration
        self.is_2d = len(history.shape) == 3

    def generate_events(self):
        events = []
        if self.is_2d:
            steps, height, width = self.history.shape
            for step in range(steps):
                t = step * self.step_duration
                # Count active cells in 2x2 blocks
                block_sum = 0
                # Avoid deprecated warning by explicitly converting to array if needed
                for i in range(0, height, 2):
                    for j in range(0, width, 2):
                        block = self.history[step, i:min(i+2,height), j:min(j+2,width)]
                        block_sum += np.sum(block)  # block is ndarray, safe
                if block_sum > 10:
                    pitches = [self.base_pitch, self.base_pitch+4, self.base_pitch+7]
                elif block_sum > 5:
                    pitches = [self.base_pitch, self.base_pitch+3, self.base_pitch+7]
                else:
                    pitches = [self.base_pitch]
                for p in pitches:
                    p_clipped = max(0, min(127, p))
                    events.append((t, 'note_on', p_clipped, 70))
                    events.append((t + self.step_duration, 'note_off', p_clipped, 0))
        else:
            steps, width = self.history.shape
            for step in range(steps):
                t = step * self.step_duration
                # Use sliding window of size 3
                triplets = []
                for i in range(width-2):
                    triplets.append(tuple(self.history[step, i:i+3]))
                if triplets:
                    pattern = triplets[step % len(triplets)]
                    sum_bits = sum(pattern)  # built-in sum, not np.sum
                    if sum_bits == 3:
                        pitches = [self.base_pitch, self.base_pitch+4, self.base_pitch+7]
                    elif sum_bits == 2:
                        pitches = [self.base_pitch, self.base_pitch+3, self.base_pitch+7]
                    else:
                        pitches = [self.base_pitch]
                    for p in pitches:
                        p_clipped = max(0, min(127, p))
                        events.append((t, 'note_on', p_clipped, 70))
                        events.append((t + self.step_duration, 'note_off', p_clipped, 0))
        return events