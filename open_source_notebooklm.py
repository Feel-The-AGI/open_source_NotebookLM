from pypdf import PdfReader
from pydantic import BaseModel, ValidationError
from typing import List, Literal, Tuple, Optional
import subprocess
import ffmpeg
from cartesia import Cartesia

# Define Dialogue Schema with Pydantic
class LineItem(BaseModel):
    """A single line in the script."""
    speaker: Literal["Host (Jane)", "Guest"]
    text: str

class Script(BaseModel):
    """The script between the host and guest."""
    scratchpad: str
    name_of_guest: str
    script: List[LineItem]

# System Prompt for Script Generation
SYSTEM_PROMPT = """
You are a world-class podcast producer tasked with transforming the provided input text into an engaging and informative podcast script. The input may be unstructured or messy, sourced from PDFs or web pages. Your goal is to extract the most interesting and insightful content for a compelling podcast discussion.

# Steps to Follow:
...
"""

# Download PDF and Extract Contents
def get_PDF_text(file : str):
    text = ''
    try:
        with Path(file).open("rb") as f:
            reader = PdfReader(f)
            text = "\n\n".join([page.extract_text() for page in reader.pages])
    except Exception as e:
        raise f"Error reading the PDF file: {str(e)}"
    if len(text) > 400000:
        raise "The PDF is too long. Please upload a PDF with fewer than ~131072 tokens."
    return text

text = get_PDF_text('MoA.pdf')

# Generate Podcast Script using JSON Mode
from together import Together

client_together = Together(api_key="TOGETHER_API_KEY")

def call_llm(system_prompt: str, text: str, dialogue_format):
    """Call the LLM with the given prompt and dialogue format."""
    response = client_together.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        response_format={
            "type": "json_object",
            "schema": dialogue_format.model_json_schema(),
        },
    )
    return response

def generate_script(system_prompt: str, input_text: str, output_model):
    """Get the script from the LLM."""
    try:
        response = call_llm(system_prompt, input_text, output_model)
        dialogue = output_model.model_validate_json(
            response.choices[0].message.content
        )
    except ValidationError as e:
        error_message = f"Failed to parse dialogue JSON: {e}"
        system_prompt_with_error = f"{system_prompt}\n\nPlease return a VALID JSON object. This was the earlier error: {error_message}"
        response = call_llm(system_prompt_with_error, input_text, output_model)
        dialogue = output_model.model_validate_json(
            response.choices[0].message.content
        )
    return dialogue

script = generate_script(SYSTEM_PROMPT, text, Script)

# Generate Podcast Using TTS
client_cartesia = Cartesia(api_key="CARTESIA_API_KEY")

host_id = "694f9389-aac1-45b6-b726-9d9369183238" # Jane - host voice
guest_id = "a0e99841-438c-4a64-b679-ae501e7d6091" # Guest voice
model_id = "sonic-english" # The Sonic Cartesia model for English TTS

output_format = {
    "container": "raw",
    "encoding": "pcm_f32le",
    "sample_rate": 44100,
}

# Set up a WebSocket connection.
ws = client_cartesia.tts.websocket()

# Open a file to write the raw PCM audio bytes to.
f = open("podcast.pcm", "wb")

# Generate and stream audio.
for line in script.dialogue:
    if line.speaker == "Guest":
        voice_id = guest_id
    else:
        voice_id = host_id

    for output in ws.send(
        model_id=model_id,
        transcript='-' + line.text,
        voice_id=voice_id,
        stream=True,
        output_format=output_format,
    ):
        buffer = output["audio"]
        f.write(buffer)

# Close the connection to release resources
ws.close()
f.close()

# Convert the raw PCM bytes to a WAV file.
ffmpeg.input("podcast.pcm", format="f32le").output("podcast.wav").run()

# Play the file
subprocess.run(["ffplay", "-autoexit", "-nodisp", "podcast.wav"])