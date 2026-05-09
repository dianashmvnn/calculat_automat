"""
Plotting script for generated metrics.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_note_distribution(midi_file, output_png="note_dist.png"):
    import pretty_midi
    pm = pretty_midi.PrettyMIDI(midi_file)
    pitches = []
    for inst in pm.instruments:
        pitches.extend([n.pitch for n in inst.notes])
    plt.figure(figsize=(10,4))
    plt.hist(pitches, bins=range(128), alpha=0.7, color='steelblue')
    plt.xlabel('MIDI pitch')
    plt.ylabel('Frequency')
    plt.title('Note distribution')
    plt.savefig(output_png)
    plt.close()


def plot_entropy_evolution(csv_file, output_png="entropy_evolution.png"):
    df = pd.read_csv(csv_file)
    # Group by rule and mapping
    grouped = df.groupby(['rule', 'mapping_type'])['entropy'].mean().reset_index()
    plt.figure(figsize=(8,5))
    sns.barplot(data=grouped, x='rule', y='entropy', hue='mapping_type')
    plt.xlabel('CA Rule')
    plt.ylabel('Shannon Entropy (bits)')
    plt.title('Entropy by Rule and Mapping')
    plt.legend(title='Mapping')
    plt.savefig(output_png)
    plt.close()


def plot_zipf_comparison(csv_file, output_png="zipf_comparison.png"):
    df = pd.read_csv(csv_file)
    plt.figure(figsize=(8,5))
    sns.boxplot(data=df, x='ca_type', y='zipf_alpha', hue='mapping_type')
    plt.xlabel('CA Type')
    plt.ylabel('Zipf exponent α')
    plt.axhline(y=1.0, linestyle='--', color='red', label='Ideal (speech/music)')
    plt.legend()
    plt.title('Zipf exponent by CA type and mapping')
    plt.savefig(output_png)
    plt.close()


if __name__ == "__main__":
    # Example: plot from results.csv
    plot_entropy_evolution("results.csv", "entropy_evolution.png")
    plot_zipf_comparison("results.csv", "zipf_comparison.png")
    # Also plot distribution of a specific MIDI file (e.g., first generated)
    import glob
    midi_files = glob.glob("output/*.mid")
    if midi_files:
        plot_note_distribution(midi_files[0], "note_dist.png")