import contextlib
import glob
import wave


def file_statistics(glob_pattern):
    # file_statistics(r"path\to\wav\*.wav")
    def get_file_len(wav_path):
        with contextlib.closing(wave.open(wav_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            wav_length = frames / float(rate)
            # print(f"wave length: {wav_length} seconds")
            return wav_length

    full_length = 0
    wav_file_count = 0
    for file in glob.iglob(glob_pattern):
        full_length += get_file_len(file)
        wav_file_count += 1

    print(f"wav full length: {full_length / 60 / 60} hours, total files: {wav_file_count}")
