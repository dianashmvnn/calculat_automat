"""
Build MIDI file from events.
"""

import mido
import pretty_midi


def build_midi_file(events, tempo=120, instrument=0, output_file="output.mid"):
    """
    events: list of (time_sec, type, pitch, velocity)
    type: 'note_on' or 'note_off'
    """
    # Create a PrettyMIDI object
    mid = pretty_midi.PrettyMIDI(initial_tempo=tempo)
    # Create an instrument track
    instrument_track = pretty_midi.Instrument(program=instrument)
    # Convert time in seconds to ticks using mido for simplicity? 
    # PrettyMIDI expects absolute times in seconds.
    # We'll just use seconds.
    # Group note_on/note_off pairs to create Note objects
    notes = {}
    for time_sec, typ, pitch, velocity in events:
        if typ == 'note_on':
            if pitch not in notes:
                notes[pitch] = []
            notes[pitch].append(('on', time_sec, velocity))
        elif typ == 'note_off':
            if pitch in notes and notes[pitch]:
                # pair with last unpaired note_on
                on_events = [ev for ev in notes[pitch] if ev[0] == 'on']
                if on_events:
                    on_time, vel = on_events[-1][1], on_events[-1][2]
                    notes[pitch].remove(('on', on_time, vel))
                    note = pretty_midi.Note(
                        velocity=vel,
                        pitch=pitch,
                        start=on_time,
                        end=time_sec
                    )
                    instrument_track.notes.append(note)
    # Add any orphaned note_on (closing at end of last event)
    max_time = max([t for t,_,_,_ in events]) if events else 0.0
    for pitch, ev_list in notes.items():
        for ev in ev_list:
            if ev[0] == 'on':
                note = pretty_midi.Note(
                    velocity=ev[2],
                    pitch=pitch,
                    start=ev[1],
                    end=max_time + 0.5
                )
                instrument_track.notes.append(note)
    mid.instruments.append(instrument_track)
    mid.write(output_file)
    return output_file