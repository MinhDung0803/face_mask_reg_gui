from pydub import AudioSegment
from pydub.playback import play
import threading


def play_audio(file):
    sound = AudioSegment.from_file(file)
    # play the file
    play(sound)


def play_audio_by_threading(file):
    t = threading.Thread(target = play_audio, args = [file])
    t.start()