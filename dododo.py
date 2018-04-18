from wave import open
from struct import Struct
from math import floor
from math import sin, pi

frame_rate = 11025

def encode(x):
    """Encode float x between -1 and 1 as two bytes.
    (See https://docs.python.org/3/library/struct.html)
    """
    i = int(16384 * x)
    return Struct('h').pack(i)

harm_number = 1
def play(sampler, name='song.wav', seconds=2):
    """Write the output of a sampler function as a wav file.
    (See https://docs.python.org/3/library/wave.html)
    """
    out = open(name, 'wb')
    out.setnchannels(1)
    out.setsampwidth(2)
    out.setframerate(frame_rate)
    t = 0
    while t < seconds * frame_rate:
        sample = sampler(t)/harm_number
        out.writeframes(encode(sample))
        t = t + 1
    out.close()

# triangle wave
def tri(frequency, amplitude=1):
    """A continuous triangle wave."""
    period = frame_rate // frequency
    def sampler(t):
        tri_wave = (2 / period) * (0.5 * period - abs(t % (period) - 0.5 * period)) - 0.5
        return amplitude * tri_wave

    return sampler
# square wave
def squ(frequency, amplitude =1):
    period = frame_rate// frequency
    def sampler(t):
        squ_wave = 2 * floor(t / (period)) - floor((2 * t) / (period)) + 0.5
        return amplitude * squ_wave
    return sampler
# sine wave
def sine(frequency, amplitude = 1):
    period = frame_rate// frequency
    def sampler(t):
        sine_wave = sin(2*pi*t/period)
        return amplitude * sine_wave
    return sampler


def note(f, start, end, fade=.01):
    """Play f for a fixed duration."""
    def sampler(t):
        seconds = t / frame_rate
        if seconds < start:
            return 0
        elif seconds > end:
            return 0
        elif seconds < start + fade:
            return (seconds - start) / fade * f(t)
        elif seconds > end - fade:
            return (end - seconds) / fade * f(t)
        else:
            return f(t)
    return sampler

# play several music lines together
def both(*arg):
    global harm_number
    harm_number = len(arg)
    def add_all(t):
        result = arg[0](t)
        for i in range(1,len(arg)):
            result += arg[i](t)
        return result
    return add_all

# the frequency of each note
do,ri,mi,fa,so,la,xi = 261.63,293.66 ,329.63, 349.23,392.00,440.00,493.88
do2, ri2, fa2,so2,la2 = 277.18,311.13,369.99,415.30,466.16

# for space and half interval
space = 0
decrease = 0.1

# to get the length of whole music
song_total_len = 0
# generate one wave line based on music notes
def note_line(notes, wave_form = tri, wave_amplitude = 1,note_len =1 / 4, note_inter =1 / 4 ):
    z = note_inter
    song = note(wave_form(notes[0],wave_amplitude), z , z + note_len)
    song_len = len(notes) * (note_len + note_inter)

    for i in range(0,len(notes)):
        if notes[i] == 0:
            song = both(song, note(tri(1), z, z + note_len))
            z = z + note_inter
            continue
        elif notes[i] < 1:
            z = z - 0.5*note_inter
            continue
        song = both(song, note(wave_form(notes[i],wave_amplitude), z, z + note_len))
        z = z + note_inter
    global song_total_len
    if song_len > song_total_len:
        song_total_len = song_len
    return song

# change octave of whole wave line
def octave_set(notes_list, octave):
    return [i * octave for i in notes_list]


"""
do ri mi fa so la xi || do ri mi fa so la xi
"""
# mario test
mario = [mi,decrease,mi,mi,do,decrease,mi,so,space,0.5*so]

harm1 = note_line(mario,wave_form=tri,wave_amplitude=1,note_len=1/8,note_inter=1/4)
harm2 = note_line(octave_set(mario,0.5),wave_form=tri,wave_amplitude=0.5,note_len=1/8,note_inter=1/4)
play(both(harm1,harm2), name='mario.wav', seconds=song_total_len)






