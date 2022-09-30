# importing libraries
from pathlib import Path

import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from tqdm import tqdm


CHUNKS_FOLDER = Path(r'./Audio_chunks')
TRANSCRIPTS_FOLDER = Path(r'./Transcripts')

# a function that splits the audio file into chunks
# and applies speech recognition
def silence_based_conversion(path):
    # open the audio file stored in
    # the local system as a wav file.
    song = AudioSegment.from_wav(path)
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
                          silence_thresh=-20
                          )
    # create a directory to store the audio chunks.
    CHUNKS_FOLDER.mkdir(exist_ok=True)

    # process each chunk
    pbar = tqdm(chunks[1:], colour='green', unit='chunk', ncols=80)
    for i, chunk in enumerate(pbar):
        # Create 0.5 seconds silence chunk
        chunk_silent = AudioSegment.silent(duration=10)

        # add 0.5 sec silence to beginning and
        # end of audio chunk. This is done so that
        # it doesn't seem abruptly sliced.
        audio_chunk = chunk_silent + chunk + chunk_silent

        # export audio chunk and save it in the current directory.
        pbar.set_description_str('Saving')
        chunk_file = CHUNKS_FOLDER / f"chunk_{i}.wav"
        # specify the bitrate to be 192 k
        audio_chunk.export(chunk_file, bitrate='192k', format="wav")
        pbar.set_description_str('Processing')

        # create a speech recognition object
        r = sr.Recognizer()
        # recognize the chunk
        with sr.AudioFile(str(chunk_file)) as source:
            # remove this if it is not working correctly.
            r.adjust_for_ambient_noise(source)
            audio = r.record(source)
            try:
                # try converting it to text
                rec = r.recognize_google(audio, language="ru-RU")
                # write the output to the file.
                TRANSCRIPTS_FOLDER.mkdir(exist_ok=True)
                with (TRANSCRIPTS_FOLDER / f'recognized_{i}.txt').open('w+', encoding='utf-8') as f:
                    f.write(rec)
                # catch any errors.
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError:
                print("Could not request results. check your internet connection")

if __name__ == '__main__':
    source_audio = Path(r"./audio/rec1.2.wav").resolve()
    print(f'Audio file path: {source_audio}')
    silence_based_conversion(source_audio)
