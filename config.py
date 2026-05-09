"""
Configuration and parameter loading for experiments.
"""

import json
import random
import numpy as np


class Config:
    def __init__(self, config_dict: dict = None):
        if config_dict is None:
            config_dict = {}
        self.ca_type = config_dict.get('ca_type', '1D')          # '1D' or '2D'
        self.rule = config_dict.get('rule', 90)                 # 0-255 for 1D
        self.width = config_dict.get('width', 64)               # grid width for 1D, N for 2D
        self.height = config_dict.get('height', 64)             # for 2D only
        self.init_type = config_dict.get('init_type', 'random') # 'random', 'single', 'periodic'
        self.density = config_dict.get('density', 0.5)          # initial active probability
        self.steps = config_dict.get('steps', 100)              # number of CA steps/generations
        self.mapping_type = config_dict.get('mapping_type', 'direct') # 'direct', 'interval', 'tonnetz'
        self.base_pitch = config_dict.get('base_pitch', 60)     # MIDI note (C4)
        self.scale_intervals = config_dict.get('scale_intervals', [0, 2, 4, 5, 7, 9, 11]) # C major
        self.step_duration = config_dict.get('step_duration', 0.5) # seconds per CA step
        self.tempo = config_dict.get('tempo', 120)              # BPM (overrides step_duration if given)
        self.instrument = config_dict.get('instrument', 0)      # GM program number (0 = Acoustic Grand)
        self.output_file = config_dict.get('output_file', 'output.mid')
        self.seed = config_dict.get('seed', 42)

    def validate(self):
        if self.ca_type == '1D':
            assert 0 <= self.rule <= 255, "Rule must be between 0 and 255"
            assert self.width > 0, "Width must be positive"
        elif self.ca_type == '2D':
            assert self.width > 0 and self.height > 0, "Width and height must be positive"
        assert self.steps > 0, "Steps must be positive"
        assert self.mapping_type in ['direct', 'interval', 'tonnetz'], "Unknown mapping type"
        assert 0 <= self.base_pitch <= 127, "Base pitch out of MIDI range"
        if self.tempo:
            assert 20 <= self.tempo <= 300, "Tempo out of reasonable range"

    def to_dict(self):
        return {
            'ca_type': self.ca_type,
            'rule': self.rule,
            'width': self.width,
            'height': self.height,
            'init_type': self.init_type,
            'density': self.density,
            'steps': self.steps,
            'mapping_type': self.mapping_type,
            'base_pitch': self.base_pitch,
            'scale_intervals': self.scale_intervals,
            'step_duration': self.step_duration,
            'tempo': self.tempo,
            'instrument': self.instrument,
            'output_file': self.output_file,
            'seed': self.seed
        }

    @classmethod
    def from_json(cls, json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
        return cls(data)

    def set_seed(self):
        random.seed(self.seed)
        np.random.seed(self.seed)