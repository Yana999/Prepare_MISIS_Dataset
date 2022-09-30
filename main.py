# importing libraries
import os

import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence


# a function that splits the audio file into chunks
# and applies speech recognition
def silence_based_conversion(path=r"C:\Users\Dns\voice\rec1.2.wav"):
    # open the audio file stored in
    # the local system as a wav file.
    song = AudioSegment.from_wav(path)
    # open a file where we will concatenate
    # and store the recognized text
    fh = open("recognized.txt", "w+")
    # split track where silence is 0.5 seconds
    # or more and get chunks
    chunks = split_on_silence(song,
                          # must be silent for at least 0.5 seconds
                          # or 500 ms. adjust this value based on user
                          # requirement. if the speaker stays silent for
                          # longer, increase this value. else, decrease it.
                          min_silence_len=700,
                          # consider it silent if quieter than -16 dBFS
                          # adjust this per requirement
                          silence_thresh=- 20
                          )
    # create a directory to store the audio chunks.
    try:
        os.mkdir('audio_chunks')
    except (FileExistsError):
        pass
    # move into the directory to
    # store the audio files.
    os.chdir('audio_chunks')
    # process each chunk
    for i, chunk in enumerate(chunks):
        # Create 0.5 seconds silence chunk
        chunk_silent = AudioSegment.silent(duration=10)
        # add 0.5 sec silence to beginning and
        # end of audio chunk. This is done so that
        # it doesn't seem abruptly sliced.
        audio_chunk = chunk_silent + chunk + chunk_silent
        # export audio chunk and save it in
        # the current directory.
        print(f"saving chunk{i}.wav")
        # specify the bitrate to be 192 k
        audio_chunk.export(f"./chunk {i}.wav", bitrate='192k', format="wav")
        # the name of the newly created chunk
        filename = f'chunk {i}.wav'
        print(f"Processing chunk {i}")
        # get the name of the newly created chunk
        # in the AUDIO_FILE variable for later use.
        # create a speech recognition object
        r = sr.Recognizer()
        # recognize the chunk
        with sr.AudioFile(filename) as source:
            # remove this if it is not working
            # correctly.
            r.dynamic_energy_threshold = True
            r.adjust_for_ambient_noise(source)
            audio = r.record(source)
            try:
                # try converting it to text
                rec = r.recognize_google(audio, language="ru-RU")
                # write the output to the file.
                with open(f'../recognized/recognized {i}.txt', 'w+') as f:
                    f.write(rec)
                # catch any errors.
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print("Could not request results. check your internet connection")
            i += 1
        os.chdir('..')

if __name__ == '__main__':
    print('Enter the audio file path')
    # path = input()
    silence_based_conversion()
