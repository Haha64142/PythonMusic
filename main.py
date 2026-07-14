import numpy as np
from track_funcs import NotePostEffects, ADSR
from scipy.io.wavfile import write
from notes import Notes, NoteEvent
from track import Track


def signal(track: Track, note: NoteEvent):
    return track.call_func("wave", note)


sample_rate = 48000
track = Track(sample_rate)
track.set_default_funcs(ADSR)
# track.opts["fade_time"] = 0.01
# track.opts["fade_in_time"] = 0.01
# track.opts["fade_out_time"] = 0.49
# track.set_func("note_post_effects", NotePostEffects.none)
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
