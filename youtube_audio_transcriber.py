import os
import threading
import time
import json
import whisper
from pathlib import Path


def create_transcription_file(transcribed_text, filename, transcription_output_folder):

    name_without_extension = Path(filename).stem        # Remove the extension (.m4a)

    with open(f'{transcription_output_folder}\\{name_without_extension}.txt', 'w', encoding="utf-8") as file:
        file.write(transcribed_text)


def paragraphize_text(input_string):

    # Convert the input string to a list of characters for easier manipulation
    chars = list(input_string)
    space_count = 0

    # Iterate over the characters and replace every 100th space with a newline
    for i in range(len(chars)):
        if chars[i] == ' ':
            space_count += 1
            if space_count % 100 == 0:
                chars[i] = '\n\n'

    # Join the list back into a string
    result_string = ''.join(chars)
    return result_string


def transcribe_audio(input_audio_file: str):

    print(f'Running audio conversion for: {os.path.basename(input_audio_file)}')

    model = whisper.load_model('base')
    result = model.transcribe(input_audio_file, fp16=False)
    transcribed_text = result['text']

    final_text = paragraphize_text(transcribed_text)

    return final_text


def transcribe_and_output_text(audio_file_folder, audio_file, transcription_output_folder):

    transcribed_text = transcribe_audio(os.path.join(audio_file_folder, audio_file))
    # After doing the transcription, make the .txt file with the text transcription.
    create_transcription_file(transcribed_text, audio_file, transcription_output_folder)


def transcribe_and_output_text_thread(audio_file_folder, audio_file, transcription_output_folder):

    my_thread = threading.Thread(target=transcribe_and_output_text, args=(audio_file_folder, audio_file, transcription_output_folder))
    my_thread.start()


def read_settings_file():

    with open("settings.json", "r") as f:
        settings_json = json.load(f)

    return settings_json


def main():

    settings_json = read_settings_file()

    audio_file_folder = settings_json['input_audio']
    transcription_output_folder = settings_json['output_transcriptions']
    log_file = settings_json['log_file']

    # Cycle through the folder of audio files
    for audio_file in os.listdir(audio_file_folder):

        start_time = time.time()  # Start timing

        transcribe_and_output_text(audio_file_folder, audio_file, transcription_output_folder)

        end_time = time.time()  # End timing
        elapsed_time = end_time - start_time  # Calculate elapsed time

        # Convert seconds to mm:ss format
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)

        processing_message = f"Time for processing '{audio_file}': {minutes:02}:{seconds:02}"

        print(processing_message)
        print()

        with open(log_file, "a") as file:
            file.write(processing_message + "\n")


if __name__ == '__main__':

    main()
