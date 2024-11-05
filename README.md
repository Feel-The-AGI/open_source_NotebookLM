# PDF to Podcast

This script takes a PDF file as input and generates an audio podcast from its contents. It uses a large language model (LLM) to create a script for a conversation between a host and a guest, and then uses a text-to-speech (TTS) service to convert the script into an audio file.

## Requirements

- Python 3.10 or later
- The following Python packages:
  - `pypdf`
  - `pydantic`
  - `together-ai`
  - `cartesia`
  - `ffmpeg-python`
  - `subprocess`

You'll also need to provide your own API keys for the `Together AI` and `Cartesia` services.

## Usage

1. Download the PDF file you want to use as input and place it in the same directory as the script.
2. Replace `"TOGETHER_API_KEY"` and `"CARTESIA_API_KEY"` in the script with your own API keys.
3. Run the script using `python path/to/script.py`.
4. The script will generate a `podcast.wav` file in the same directory, which you can then listen to or distribute as a podcast.

## How it works

1. The script uses the `pypdf` library to extract the text content from the PDF file.
2. It then defines a Pydantic schema for the podcast script, which includes the host, guest, and their lines of dialogue.
3. The script calls the `Together AI` API to generate the podcast script using a large language model (LLM) and the provided system prompt.
4. The generated script is then used to create the audio podcast using the `Cartesia` TTS service, which generates the audio for each line of dialogue.
5. The raw PCM audio data is written to a file, which is then converted to a WAV file using `ffmpeg-python`.
6. Finally, the script plays the generated podcast audio file using `subprocess`.

## Customization

You can customize the script in the following ways:

- Modify the system prompt used to generate the podcast script.
- Adjust the voice IDs for the host and guest in the TTS section.
- Change the output audio format or sample rate.
- Add additional processing or post-processing steps for the generated audio.

## License

This script is licensed under the [MIT License](LICENSE).
