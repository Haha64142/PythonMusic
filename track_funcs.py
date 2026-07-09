import numpy as np
import math
from notes import NoteEvent
from numpy.typing import NDArray
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from track import Track


def curve(times: NDArray[np.float64], curvature: float) -> NDArray[np.float64]:
    if curvature == 0:
        return times

    return (np.exp2(curvature * times) - 1) / (math.exp2(curvature) - 1)


def inverse_curve(value: float, curvature: float) -> float:
    if curvature == 0:
        return value

    return math.log2(1 + value * (math.exp2(curvature) - 1)) / curvature


class Waveforms:
    @staticmethod
    def sin(track: Track, note: NoteEvent) -> NDArray[np.float64]:
        sample_rate = track.sample_rate
        start_frame = int(note.start * sample_rate)
        stop_frame = int(note.stop * sample_rate)

        note_time = np.arange(stop_frame - start_frame) / sample_rate
        signal = np.sin(2 * math.pi * note.freq * note_time)
        return signal


class PostEffects:
    @staticmethod
    def none(
        _track: Track, note_data: NDArray[np.float64], _note: NoteEvent
    ) -> NDArray[np.float64]:
        return note_data

    @staticmethod
    def fade(
        track: Track, note_data: NDArray[np.float64], note: NoteEvent
    ) -> NDArray[np.float64]:
        sample_rate = track.sample_rate

        fade_time = note.opts.get("fade_time", track.opts.get("fade_time", 0.01))
        fade_in_time = note.opts.get(
            "fade_in_time", track.opts.get("fade_in_time", fade_time)
        )
        fade_out_time = note.opts.get(
            "fade_out_time", track.opts.get("fade_out_time", fade_time)
        )

        start_frame = int(note.start * sample_rate)
        stop_frame = int(note.stop * sample_rate)

        note_frames = int(stop_frame - start_frame)

        fade_in_frames = int(fade_in_time * sample_rate)
        fade_out_frames = int(fade_out_time * sample_rate)

        fade_volumes = np.ones(note_frames)

        fade_in_volumes = np.linspace(0.0, 1.0, fade_in_frames)
        fade_out_volumes = np.linspace(1.0, 0.0, fade_out_frames)

        fade_scale = min(note_frames / (fade_in_frames + fade_out_frames), 1)
        fade_volumes[: int(fade_in_frames * fade_scale)] = fade_in_volumes[
            : int(fade_in_frames * fade_scale)
        ]
        fade_volumes[-int(fade_out_frames * fade_scale) :] = fade_out_volumes[
            -int(fade_out_frames * fade_scale) :
        ]

        return note_data * fade_volumes


class Defaults:
    @staticmethod
    def generate(track: Track) -> NDArray[np.float64]:
        track_data = track.call_func("setup")

        track_data = track.call_func("main_logic", track_data)

        track_data = track.call_func("finalize", track_data)

        return track_data

    @staticmethod
    def setup(track: Track) -> NDArray[np.float64]:
        track_size = track.get_track_size()
        track_data = np.zeros(track_size, np.float64)
        return track_data

    @staticmethod
    def main_logic(
        track: Track, track_data: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        sample_rate = track.sample_rate
        track_data = track_data
        for note in track._notes:
            start_frame = int(note.start * sample_rate)
            stop_frame = int(note.stop * sample_rate)
            track_data[start_frame:stop_frame] = track.call_func("signal", note)
        return track_data

    @staticmethod
    def signal(track: Track, note: NoteEvent) -> NDArray[np.float64]:
        note_data = track.call_func("wave", note) * note.volume
        note_data = track.call_func("post_effects", note_data, note)
        return note_data

    @staticmethod
    def finalize(_track: Track, track_data: NDArray[np.float64]) -> NDArray[np.float64]:
        track_data = track_data * 0.2
        peak = np.max(np.abs(track_data))
        if peak > 0.8:
            track_data *= 0.8 / peak
        return track_data

    post_effects = staticmethod(PostEffects.fade)
    wave = staticmethod(Waveforms.sin)
