
import pygame as pg
from typing import Dict, Optional
import numpy as np


class SoundManager:

    def __init__(self):
        pg.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

        self.sounds: Dict[str, pg.mixer.Sound] = {}
        self.music_enabled = True
        self.sfx_enabled = True

        self.music_volume = 0.3
        self.sfx_volume = 0.5

        self._create_sounds()

    def _create_sounds(self):
        self.sounds['shoot'] = self._create_shoot_sound()

        self.sounds['explosion_large'] = self._create_explosion_sound(duration=0.4, freq_start=120)
        self.sounds['explosion_medium'] = self._create_explosion_sound(duration=0.3, freq_start=100)
        self.sounds['explosion_small'] = self._create_explosion_sound(duration=0.2, freq_start=80)

        self.sounds['ship_explode'] = self._create_explosion_sound(duration=0.6, freq_start=150)

        self.sounds['thrust'] = self._create_thrust_sound()

        self.sounds['hyperspace'] = self._create_hyperspace_sound()

        self.sounds['ufo_large'] = self._create_ufo_sound(freq=80)
        self.sounds['ufo_small'] = self._create_ufo_sound(freq=120)

        self.sounds['ufo_shoot'] = self._create_ufo_shoot_sound()

        self.sounds['extra_life'] = self._create_extra_life_sound()

        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)

    def _create_shoot_sound(self) -> pg.mixer.Sound:
        sample_rate = 22050
        duration = 0.1
        frequency = 440

        samples = self._generate_pulse(sample_rate, duration, frequency, decay=0.3)
        sound = pg.mixer.Sound(buffer=samples)
        return sound

    def _create_explosion_sound(self, duration: float, freq_start: int) -> pg.mixer.Sound:
        sample_rate = 22050
        samples = self._generate_noise_explosion(sample_rate, duration, freq_start)
        sound = pg.mixer.Sound(buffer=samples)
        return sound

    def _create_thrust_sound(self) -> pg.mixer.Sound:
        sample_rate = 22050
        duration = 0.3
        samples = self._generate_thrust_noise(sample_rate, duration)
        sound = pg.mixer.Sound(buffer=samples)
        return sound

    def _create_hyperspace_sound(self) -> pg.mixer.Sound:
        sample_rate = 22050
        duration = 0.5
        samples = self._generate_frequency_sweep(sample_rate, duration, 1200, 200)
        sound = pg.mixer.Sound(buffer=samples)
        return sound

    def _create_ufo_sound(self, freq: int) -> pg.mixer.Sound:
        sample_rate = 22050
        duration = 0.6
        samples = self._generate_ufo_beep(sample_rate, duration, freq)
        sound = pg.mixer.Sound(buffer=samples)
        return sound

    def _create_ufo_shoot_sound(self) -> pg.mixer.Sound:
        sample_rate = 22050
        duration = 0.12
        frequency = 320

        samples = self._generate_pulse(sample_rate, duration, frequency, decay=0.4)
        sound = pg.mixer.Sound(buffer=samples)
        return sound

    def _create_extra_life_sound(self) -> pg.mixer.Sound:
        sample_rate = 22050
        duration = 0.5
        samples = self._generate_extra_life_melody(sample_rate, duration)
        sound = pg.mixer.Sound(buffer=samples)
        return sound

    def _generate_pulse(self, sample_rate: int, duration: float,
                       frequency: float, decay: float) -> bytes:
        num_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)

        wave = np.sin(2 * np.pi * frequency * t)

        envelope = np.exp(-decay * t / duration * 10)

        wave = wave * envelope

        wave = (wave * 32767).astype(np.int16)

        stereo = np.empty((num_samples, 2), dtype=np.int16)
        stereo[:, 0] = wave
        stereo[:, 1] = wave

        return stereo.tobytes()

    def _generate_noise_explosion(self, sample_rate: int, duration: float,
                                   freq_start: int) -> bytes:
        import numpy as np

        num_samples = int(sample_rate * duration)

        noise = np.random.uniform(-1, 1, num_samples)

        t = np.linspace(0, 1, num_samples, False)
        envelope = np.exp(-5 * t)

        wave = noise * envelope

        wave = (wave * 32767).astype(np.int16)

        stereo = np.empty((num_samples, 2), dtype=np.int16)
        stereo[:, 0] = wave
        stereo[:, 1] = wave

        return stereo.tobytes()

    def _generate_thrust_noise(self, sample_rate: int, duration: float) -> bytes:
        import numpy as np

        num_samples = int(sample_rate * duration)

        noise = np.random.uniform(-0.3, 0.3, num_samples)

        wave = (noise * 32767).astype(np.int16)

        stereo = np.empty((num_samples, 2), dtype=np.int16)
        stereo[:, 0] = wave
        stereo[:, 1] = wave

        return stereo.tobytes()

    def _generate_frequency_sweep(self, sample_rate: int, duration: float,
                                   freq_start: float, freq_end: float) -> bytes:
        import numpy as np

        num_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)

        freq = np.linspace(freq_start, freq_end, num_samples)
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate

        wave = np.sin(phase)

        envelope = np.exp(-2 * t / duration)
        wave = wave * envelope

        wave = (wave * 32767).astype(np.int16)

        stereo = np.empty((num_samples, 2), dtype=np.int16)
        stereo[:, 0] = wave
        stereo[:, 1] = wave

        return stereo.tobytes()

    def _generate_ufo_beep(self, sample_rate: int, duration: float,
                           base_freq: int) -> bytes:
        import numpy as np

        num_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)

        freq1 = base_freq
        freq2 = base_freq * 1.25

        switch_rate = 8
        switch = (np.sin(2 * np.pi * switch_rate * t) > 0).astype(float)

        wave1 = np.sin(2 * np.pi * freq1 * t)
        wave2 = np.sin(2 * np.pi * freq2 * t)

        wave = wave1 * (1 - switch) + wave2 * switch

        wave = (wave * 0.4 * 32767).astype(np.int16)

        stereo = np.empty((num_samples, 2), dtype=np.int16)
        stereo[:, 0] = wave
        stereo[:, 1] = wave

        return stereo.tobytes()

    def _generate_extra_life_melody(self, sample_rate: int, duration: float) -> bytes:
        import numpy as np

        notes = [523, 659, 784, 1047]
        note_duration = duration / len(notes)

        wave_total = np.array([], dtype=np.int16)

        for freq in notes:
            num_samples = int(sample_rate * note_duration)
            t = np.linspace(0, note_duration, num_samples, False)

            wave = np.sin(2 * np.pi * freq * t)

            envelope = np.exp(-3 * t / note_duration)
            wave = wave * envelope

            wave = (wave * 32767).astype(np.int16)
            wave_total = np.concatenate([wave_total, wave])

        stereo = np.empty((len(wave_total), 2), dtype=np.int16)
        stereo[:, 0] = wave_total
        stereo[:, 1] = wave_total

        return stereo.tobytes()

    def play(self, sound_name: str, loops: int = 0):
        if not self.sfx_enabled:
            return

        if sound_name in self.sounds:
            self.sounds[sound_name].play(loops=loops)

    def stop(self, sound_name: str):
        if sound_name in self.sounds:
            self.sounds[sound_name].stop()

    def stop_all(self):
        pg.mixer.stop()

    def set_sfx_volume(self, volume: float):
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)

    def set_music_volume(self, volume: float):
        self.music_volume = max(0.0, min(1.0, volume))
        pg.mixer.music.set_volume(self.music_volume)

    def toggle_sfx(self):
        self.sfx_enabled = not self.sfx_enabled

    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            pg.mixer.music.unpause()
        else:
            pg.mixer.music.pause()


_sound_manager: Optional[SoundManager] = None


def get_sound_manager() -> SoundManager:
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager


def init_sound() -> SoundManager:
    return get_sound_manager()
