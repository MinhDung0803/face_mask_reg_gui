from pydub import AudioSegment
from pydub.playback import play
import threading


def play_audio(file):
    print("[INFO]-- Playing sound alarm threading is running")
    sound = AudioSegment.from_file(file)
    # play the file
    play(sound)


def play_audio_by_threading(file):
    t = threading.Thread(target = play_audio, args = [file])
    t.start()