import numpy as np
import math
from notes import NoteEvent, NoteTimes
from numpy.typing import NDArray
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from track import Track, TrackData, NoteData


class ADSR:
    @staticmethod
    def adsr_curve(times: NoteData, curvature: float) -> NoteData:
        if curvature == 0:
            return times

        return (np.exp2(curvature * times) - 1) / (math.exp2(curvature) - 1)

    @staticmethod
    def inverse_adsr_curve(value: float, curvature: float) -> float:
        if curvature == 0:
            return value

        return math.log2(1 + value * (math.exp2(curvature) - 1)) / curvature


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
