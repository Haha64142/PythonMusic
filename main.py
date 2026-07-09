import numpy as np
from track_funcs import PostEffects
from scipy.io.wavfile import write
from notes import Notes, NoteEvent
from track import Track


# sample_rate = 48000
# amplitude = 32767
# duration = 7
# fade_t = 0.005
# fade_samples = int(fade_t * sample_rate)
#
# t = np.arange(int(sample_rate * duration)) / sample_rate
# signal = np.zeros_like(t)
#
# # (note, start, stop)
# notes = [
#     (Notes.C4, 0, 3),  # c chord
#     (Notes.E4, 0.5, 3),
#     (Notes.G4, 1, 3),
#     (Notes.D4, 3, 5),  # d chord
#     (Notes.F4, 3, 5),
#     (Notes.A4, 3, 5),
#     (Notes.C4, 4, 7),  # c chord
#     (Notes.E4, 4, 7),
#     (Notes.G4, 4, 7),
# ]
#
# for freq, start, stop in notes:
#     start_frame = int(start * sample_rate)
#     stop_frame = int(stop * sample_rate)
#
#     note_t = np.arange(stop_frame - start_frame) / sample_rate
#     fade = np.ones(len(note_t))
#     fade[:fade_samples] = np.linspace(0, 1, fade_samples)
#     fade[-fade_samples:] = np.linspace(1, 0, fade_samples)
#
#     signal[start_frame:stop_frame] += np.sin(2 * np.pi * freq * note_t) * fade
#
# # Prevent clipping
# signal /= max(np.max(np.abs(signal)), 3)
#
# write("sound.wav", sample_rate, (signal * amplitude * 0.4).astype(np.int16))


def signal(track: Track, note: NoteEvent):
    return track.call_func("wave", note)


sample_rate = 48000
track = Track(sample_rate)
# track.opts["fade_time"] = 0.01
# track.opts["fade_in_time"] = 0.01
# track.opts["fade_out_time"] = 0.49
# track.set_func("post_effects", PostEffects.none)
# track.set_func("signal", signal)

# track.add_note(Notes.C4, 0, 15)
# track.add_note(Notes.E4, 0, 15)
# track.add_note(Notes.G4, 0, 15)
# track.add_note(Notes.C5, 0, 15)
# track.add_note(Notes.E5, 0, 15)
# track.add_note(Notes.G5, 0, 15)
# track.add_note(Notes.C3, 0, 15)
# track.add_note(Notes.E3, 0, 15)
# track.add_note(Notes.G3, 0, 15)

# for i in range(108):
#     track.add_note(Notes.C0 * (2 ** (i / 12)), 0.5 * i, 0.5 * i + 0.5)

track.add_note(Notes.C4, 0.0, 0.5)
track.add_note(Notes.D4, 0.5, 1.0)
track.add_note(Notes.E4, 1.0, 1.5)
track.add_note(Notes.F4, 1.5, 2.0)
track.add_note(Notes.G4, 2.0, 2.5)
track.add_note(Notes.A4, 2.5, 3.0)
track.add_note(Notes.B4, 3.0, 3.5)
track.add_note(Notes.C5, 3.5, 4.0)
track.add_note(Notes.C5, 4.0, 4.5)
track.add_note(Notes.B4, 4.5, 5.0)
track.add_note(Notes.A4, 5.0, 5.5)
track.add_note(Notes.G4, 5.5, 6.0)
track.add_note(Notes.F4, 6.0, 6.5)
track.add_note(Notes.E4, 6.5, 7.0)
track.add_note(Notes.D4, 7.0, 7.5)
track.add_note(Notes.C4, 7.5, 9.0)

# track.add_note(Notes.C3, 0, 1)
# track.add_note(Notes.C4, 1, 2)
# track.add_note(Notes.C5, 2, 3)

# for i in range(1200):
#     track.add_note(Notes.C4 * (2 ** (i / 1200)), i / 200, (i + 1) / 200)

# eighth = 0.25
# track.add_note(Notes.Ab5, 0 * eighth, 1 * eighth)
# track.add_note(Notes.E5, 1 * eighth, 2 * eighth)
# track.add_note(Notes.Ab5, 2 * eighth, 3 * eighth)
# track.add_note(Notes.Bb5, 3 * eighth, 4 * eighth)
# track.add_note(Notes.C6, 4 * eighth, 5 * eighth)
# track.add_note(Notes.Bb5, 5 * eighth, 6 * eighth)
# track.add_note(Notes.Ab5, 6 * eighth, 7 * eighth)
# track.add_note(Notes.E5, 7 * eighth, 8 * eighth)
# track.add_note(Notes.Eb5, 8 * eighth, 16 * eighth)

# track.add_note(0836.85, 0, 1, 1)
# track.add_note(1673.68, 0, 1, 1)
# track.add_note(2515.78, 0, 1, 1)
# track.add_note(2689.47, 0, 1, 1)
# track.add_note(3352.63, 0, 1, 1)

# track.add_note(0668.16, 0, 1, 1)
# track.add_note(1340.89, 0, 1, 1)
# track.add_note(2695.46, 0, 1, 1)

# track.add_note(1066.66, 0, 1, 1)
# track.add_note(2141.63, 0, 1, 1)
# track.add_note(3208.31, 0, 1, 1)
# track.add_note(4283.34, 0, 1, 1)

generated_track = track.generate_track()
# print(type(generated_track), generated_track.dtype)
write("sound.wav", sample_rate, generated_track)
