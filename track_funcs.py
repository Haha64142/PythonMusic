import numpy as np
import math
from notes import NoteEvent, NoteTimes
from numpy.typing import NDArray
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from track import Track, TrackData, NoteData


class ADSR:
    @staticmethod
    def base_curve(_track: Track, times: NoteData, curvature: float) -> NoteData:
        if curvature == 0:
            return times

        curvature = -curvature
        return (np.exp2(curvature * times) - 1) / (math.exp2(curvature) - 1)

    @staticmethod
    def inverse_base_curve(_track: Track, value: float, curvature: float) -> float:
        if curvature == 0:
            return value

        curvature = -curvature
        return math.log2(1 + value * (math.exp2(curvature) - 1)) / curvature

    @staticmethod
    def adsr_curve(
        track: Track,
        sample_rate: int,
        note_on_time: float,
        adr: tuple[float, float, float],
        adsr_shapes: tuple[float, float, float, float],
    ) -> tuple[float, NoteData]:
        a, d, base_r = adr
        a_curve, d_curve, s_volume, r_curve = adsr_shapes

        note_on_frames = int(note_on_time * sample_rate)
        a_frames = min(int(a * sample_rate), note_on_frames)
        d_frames = min(int(d * sample_rate), note_on_frames - a_frames)

        note_on_volumes = np.ones(note_on_frames) * s_volume
        time_lookup = np.arange(max(a_frames, d_frames)) / sample_rate

        note_on_volumes[0:a_frames] = track.call_func(
            "base_curve", time_lookup[0:a_frames] / a, a_curve
        )
        note_on_volumes[a_frames : a_frames + d_frames] = 1 - track.call_func(
            "base_curve", time_lookup[0:d_frames] / d, d_curve
        ) * (1 - s_volume)

        prev_volume = 0 if note_on_volumes.size == 0 else note_on_volumes[-1]
        r_offset = track.call_func("inverse_base_curve", 1 - prev_volume, r_curve)
        r = base_r * (1 - r_offset)
        r_frames = int(r * sample_rate)

        time_lookup = np.arange(r_frames) / sample_rate
        release_volumes = 1 - track.call_func(
            "base_curve", time_lookup / base_r + r_offset, r_curve
        )

        return (r, np.concat((note_on_volumes, release_volumes)))

    @staticmethod
    def gen_adsr_note(track: Track, note: NoteEvent) -> NoteEvent:
        a: float = note.opts.get("a", track.opts.get("a", 0.01))
        d: float = note.opts.get("d", track.opts.get("d", 0.5))
        base_r: float = note.opts.get("r", track.opts.get("r", 0.1))

        a_curve: float = note.opts.get("a_curve", track.opts.get("a_curve", 8))
        d_curve: float = note.opts.get("d_curve", track.opts.get("d_curve", 6))
        s_volume: float = note.opts.get("s_volume", track.opts.get("s_volume", 0.3))
        r_curve: float = note.opts.get("r_curve", track.opts.get("r_curve", 6))

        adsr_out: tuple[float, NoteData] = track.call_func(
            "adsr_curve",
            track.sample_rate,
            note.stop - note.start,
            (a, d, base_r),
            (a_curve, d_curve, s_volume, r_curve),
        )
        r = adsr_out[0]
        adsr_volumes = adsr_out[1]
        note.stop = note.stop + r
        note.opts["adsr_volumes"] = adsr_volumes
        return note

    @staticmethod
    def setup(track: Track) -> TrackData:
        max_time = track.track_time
        for i in range(len(track._notes)):
            note: NoteEvent = track.call_func("gen_adsr_note", track._notes[i])
            max_time = max(note.stop, max_time)
            track._notes[i] = note

        sample_rate = track.sample_rate
        frames = int(sample_rate * max_time)
        return np.zeros(frames, np.float64)

    @staticmethod
    def note_post_effects(
        _track: Track, note_data: NoteData, _note_times: NoteTimes, note: NoteEvent
    ) -> NoteData:
        adsr_volumes = note.opts.get("adsr_volumes")
        if adsr_volumes is None or len(note_data) != len(adsr_volumes):
            return note_data
        return note_data * adsr_volumes


class Waveforms:
    @staticmethod
    def sin(_track: Track, note_times: NoteTimes, note: NoteEvent) -> NoteData:
        signal = np.sin(2 * math.pi * note.freq * note_times.times)
        return signal


class NotePreEffects:
    @staticmethod
    def none(_track: Track, note: NoteEvent) -> NoteEvent:
        return note


class NotePostEffects:
    @staticmethod
    def none(
        _track: Track,
        note_data: NoteData,
        _note_times: NoteTimes,
        _note: NoteEvent,
    ) -> NoteData:
        return note_data

    @staticmethod
    def fade(
        track: Track,
        note_data: NoteData,
        note_times: NoteTimes,
        note: NoteEvent,
    ) -> NoteData:
        sample_rate = note_times.sample_rate

        fade_time: float = note.opts.get("fade_time", track.opts.get("fade_time", 0.01))
        fade_in_time: float = note.opts.get(
            "fade_in_time", track.opts.get("fade_in_time", fade_time)
        )
        fade_out_time: float = note.opts.get(
            "fade_out_time", track.opts.get("fade_out_time", fade_time)
        )

        note_frames = note_times.total_frames

        fade_in_frames = int(fade_in_time * sample_rate)
        fade_out_frames = int(fade_out_time * sample_rate)

        fade_volumes: NoteData = np.ones(note_frames)

        fade_in_volumes: NoteData = np.linspace(0.0, 1.0, fade_in_frames)
        fade_out_volumes: NoteData = np.linspace(1.0, 0.0, fade_out_frames)

        fade_scale = min(note_frames / (fade_in_frames + fade_out_frames), 1)
        fade_volumes[: int(fade_in_frames * fade_scale)] = fade_in_volumes[
            : int(fade_in_frames * fade_scale)
        ]
        fade_volumes[-int(fade_out_frames * fade_scale) :] = fade_out_volumes[
            -int(fade_out_frames * fade_scale) :
        ]

        return note_data * fade_volumes

    adsr = vars(ADSR)["note_post_effects"]


class TrackPostEffects:
    @staticmethod
    def master_volume(track: Track, track_data: TrackData) -> TrackData:
        return track_data * track.opts.get("master_volume", 0.2)

    @staticmethod
    def clip_volume(track: Track, track_data: TrackData) -> TrackData:
        clip_volume: float = track.opts.get("clip_volume", 0.8)
        peak: float = np.max(np.abs(track_data))
        if peak <= clip_volume:
            return track_data

        return track_data * clip_volume / peak


class Defaults:
    @staticmethod
    def setup(track: Track) -> TrackData:
        track_size = track.get_track_size()
        track_data: TrackData = np.zeros(track_size, np.float64)
        return track_data

    @staticmethod
    def note_times(track: Track, note: NoteEvent) -> NoteTimes:
        sample_rate = track.sample_rate
        start_frame = int(note.start * sample_rate)
        stop_frame = int(note.stop * sample_rate)
        note_times: NoteData = np.arange(stop_frame - start_frame) / sample_rate
        return NoteTimes(sample_rate, start_frame, note_times)

    note_post_effects = vars(NotePostEffects)["none"]
    wave = vars(Waveforms)["sin"]

    @staticmethod
    def signal(track: Track, note_times: NoteData, note: NoteEvent) -> NoteData:
        note_data: NoteData = track.call_func("wave", note_times, note) * note.volume
        note_data: NoteData = track.call_func(
            "note_post_effects", note_data, note_times, note
        )
        return note_data

    note_pre_effects = vars(NotePreEffects)["none"]

    @staticmethod
    def main_logic(track: Track, track_data: TrackData) -> TrackData:
        track_data = track_data
        for note in track._notes:
            note = track.call_func("note_pre_effects", note)
            note_times: NoteTimes = track.call_func("note_times", note)
            track_data[note_times.start_frame : note_times.stop_frame] = (
                track.call_func("signal", note_times, note)
            )
        return track_data

    master_volume = vars(TrackPostEffects)["master_volume"]
    clip_volume = vars(TrackPostEffects)["clip_volume"]

    @staticmethod
    def track_post_effects(track: Track, track_data: TrackData) -> TrackData:
        track_data = track.call_func("master_volume", track_data)
        track_data = track.call_func("clip_volume", track_data)
        return track_data

    @staticmethod
    def generate(track: Track) -> TrackData:
        track_data = track.call_func("setup")

        track_data = track.call_func("main_logic", track_data)

        track_data = track.call_func("track_post_effects", track_data)

        return track_data
