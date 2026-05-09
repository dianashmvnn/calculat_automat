"""
Formal evaluation metrics: entropy, Zipf's law, repetitiveness.
"""

import numpy as np
from collections import Counter
import pretty_midi
from scipy import stats


class Evaluator:
    def __init__(self, midi_file):
        self.midi_data = pretty_midi.PrettyMIDI(midi_file)
        self.notes = self._extract_notes()
        self.pitches = [n.pitch for n in self.notes]

    def _extract_notes(self):
        notes = []
        for inst in self.midi_data.instruments:
            notes.extend(inst.notes)
        return notes

    def pitch_entropy(self):
        """Shannon entropy based on pitch classes (0-11)."""
        pitch_classes = [p % 12 for p in self.pitches]
        if not pitch_classes:
            return 0.0
        counts = Counter(pitch_classes)
        total = len(pitch_classes)
        probs = [c / total for c in counts.values()]
        # ИСПРАВЛЕНО: используем встроенную sum() вместо np.sum()
        entropy = -sum(p * np.log2(p) for p in probs)
        return entropy

    def zipf_exponent(self):
        """Fit power law to rank-frequency distribution of pitches."""
        if not self.pitches:
            return 0.0
        counts = Counter(self.pitches)
        sorted_counts = sorted(counts.values(), reverse=True)
        ranks = np.arange(1, len(sorted_counts) + 1)
        log_ranks = np.log(ranks)
        log_freqs = np.log(sorted_counts)
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_ranks, log_freqs)
        alpha = -slope
        return alpha

    def repetitiveness(self, max_lag=8):
        """Average autocorrelation of pitch sequence for lags 1..max_lag."""
        if len(self.pitches) < 2:
            return 0.0
        pitches = np.array(self.pitches)
        pitches = pitches - np.mean(pitches)
        autocorr = np.correlate(pitches, pitches, mode='full')
        autocorr = autocorr[len(autocorr) // 2:]  # positive lags
        autocorr = autocorr / autocorr[0]  # normalize
        lags = np.arange(1, min(max_lag, len(autocorr) - 1) + 1)
        if len(lags) == 0:
            return 0.0
        return np.mean(autocorr[lags])

    def evaluate_all(self):
        return {
            'entropy': self.pitch_entropy(),
            'zipf_alpha': self.zipf_exponent(),
            'repetitiveness': self.repetitiveness()
        }