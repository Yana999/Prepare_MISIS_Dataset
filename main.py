# importing libraries
from __future__ import unicode_literals

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import speech_recognition as sr
import yt_dlp
from pydub import AudioSegment
from pydub.silence import split_on_silence
from tqdm import tqdm

CHUNKS_FOLDER = Path(r'./Audio_chunks')
TRANSCRIPTS_FOLDER = Path(r'./Transcripts')

CHUNKS_FOLDER.mkdir(exist_ok=True)
TRANSCRIPTS_FOLDER.mkdir(exist_ok=True)

# a function that splits the audio file into chunks
# and applies speech recognition
def silence_based_conversion(path):

    audio_subfolder = CHUNKS_FOLDER / path.name
    transcripts_subfolder = TRANSCRIPTS_FOLDER / path.name

    audio_subfolder.mkdir(exist_ok=True)
    transcripts_subfolder.mkdir(exist_ok=True)
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


    # process each chunk
    pbar = tqdm(chunks[1:], colour='green', unit='chunk', ncols=80, desc=path.name)
    for i, chunk in enumerate(pbar):
        # Create 0.5 seconds silence chunk
        chunk_silent = AudioSegment.silent(duration=10)

        # add 0.5 sec silence to beginning and
        # end of audio chunk. This is done so that
        # it doesn't seem abruptly sliced.
        audio_chunk = chunk_silent + chunk + chunk_silent

        # export audio chunk and save it in the current directory.
        chunk_file = audio_subfolder / f"chunk_{i}.wav"
        # specify the bitrate to be 192 k
        audio_chunk.export(chunk_file, bitrate='192k', format="wav")

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
                with (transcripts_subfolder / f'recognized_{i}.txt').open('w+', encoding='utf-8') as f:
                    f.write(rec)
                # catch any errors.
            except Exception:
                pass
            # except sr.UnknownValueError:
            #     pbar.write(f"{i}: Could not understand audio")
            # except sr.RequestError:
            #     pbar.write(f"{i}: Could not request results. check your internet connection")

if __name__ == '__main__':

    ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': './audio/YT_video_%(autonumber)d.%(ext)s',
    'quiet': True,
    'concurrent_fragment_downloads': 3,
    'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        with open(r'./youtube.txt', encoding='utf-8') as f:
            ydl.download(f.read().splitlines())


    audio_folder = Path(r"./audio")
    with ProcessPoolExecutor(max_workers=3) as executor:
        executor.map(silence_based_conversion, audio_folder.iterdir())
