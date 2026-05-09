"""
Batch experiment runner.
"""

import os
import csv
import numpy as np
from config import Config
from ca_engine import ElementaryCA, GameOfLife
from mapper import DirectMapper, IntervalMapper, TonnetzMapper
from midi_builder import build_midi_file
from evaluator import Evaluator


def run_experiment(config, output_dir="output"):
    """Run a single experiment given a Config object."""
    os.makedirs(output_dir, exist_ok=True)
    config.set_seed()

    # Generate CA history
    if config.ca_type == '1D':
        ca = ElementaryCA(rule=config.rule, width=config.width,
                          init_type=config.init_type, density=config.density)
        history = ca.evolve(config.steps)
    else:  # 2D
        ca = GameOfLife(width=config.width, height=config.height,
                        init_type=config.init_type, density=config.density)
        history = ca.evolve(config.steps)

    # Map to events
    if config.mapping_type == 'direct':
        mapper = DirectMapper(history, base_pitch=config.base_pitch,
                              scale_intervals=config.scale_intervals,
                              step_duration=config.step_duration)
    elif config.mapping_type == 'interval':
        mapper = IntervalMapper(history, base_pitch=config.base_pitch,
                                scale_intervals=config.scale_intervals,
                                step_duration=config.step_duration)
    elif config.mapping_type == 'tonnetz':
        mapper = TonnetzMapper(history, base_pitch=config.base_pitch,
                               step_duration=config.step_duration)
    else:
        raise ValueError(f"Unknown mapping type: {config.mapping_type}")

    events = mapper.generate_events()
    # Determine output file name
    fname = f"{config.ca_type}_r{config.rule}_m{config.mapping_type}_s{config.steps}.mid"
    out_path = os.path.join(output_dir, fname)
    build_midi_file(events, tempo=config.tempo, instrument=config.instrument,
                    output_file=out_path)

    # Evaluate
    evaluator = Evaluator(out_path)
    metrics = evaluator.evaluate_all()
    metrics['file'] = fname
    metrics.update(config.to_dict())
    return metrics


def run_batch(configs, output_dir="output", results_csv="results.csv"):
    """Run multiple experiments defined by a list of Config dicts."""
    all_metrics = []
    for idx, cfg_dict in enumerate(configs):
        print(f"Running experiment {idx+1}/{len(configs)}: {cfg_dict}")
        cfg = Config(cfg_dict)
        try:
            metrics = run_experiment(cfg, output_dir)
            all_metrics.append(metrics)
        except Exception as e:
            print(f"Error in experiment {idx+1}: {e}")
            continue
    # Save results to CSV
    if all_metrics:
        keys = all_metrics[0].keys()
        with open(results_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_metrics)
        print(f"Results saved to {results_csv}")
    return all_metrics


if __name__ == "__main__":
    # Example batch: vary rule and mapping type
    base_config = {
        'ca_type': '1D',
        'width': 64,
        'steps': 32,
        'init_type': 'random',
        'density': 0.5,
        'tempo': 120,
        'instrument': 0,
        'base_pitch': 60,
        'scale_intervals': [0, 2, 4, 5, 7, 9, 11],
        'step_duration': 0.5,
        'seed': 42
    }
    experiments = []
    for rule in [30, 90, 110, 150, 184]:
        for mapping in ['direct', 'interval']:
            cfg = base_config.copy()
            cfg['rule'] = rule
            cfg['mapping_type'] = mapping
            experiments.append(cfg)
    # Add Game of Life examples
    experiments.append({
        'ca_type': '2D',
        'width': 32,
        'height': 32,
        'steps': 50,
        'init_type': 'random',
        'density': 0.3,
        'mapping_type': 'direct',
        'tempo': 120,
        'base_pitch': 60,
        'step_duration': 0.5,
        'seed': 42
    })
    run_batch(experiments, output_dir="output", results_csv="results.csv")