from transformers import AutoProcessor
from transformers import SeamlessM4TModel
import torchaudio, torch

model = SeamlessM4TModel.from_pretrained("facebook/hf-seamless-m4t-large")
device = "cuda:0" if torch.cuda.is_available() else "cpu"
model = model.to(device)
processor = AutoProcessor.from_pretrained("facebook/hf-seamless-m4t-large")


# Load the audio file
sample_rate=16000
audio_sample, audio_sampling_rate = torchaudio.load("gossos.mp3")

# Check if the audio's sampling rate is different from the model's sampling rate and resample if necessary
if audio_sampling_rate != model.config.sampling_rate:
    audio_sample = torchaudio.functional.resample(audio_sample, 
                                                  orig_freq=audio_sampling_rate, 
                                                  new_freq=model.config.sampling_rate)

# Process the audio inputs using the specified processor, device, and sampling rate
audio_inputs = processor(audios=audio_sample, return_tensors="pt", sampling_rate=sample_rate).to(device)

# Generate text from the processed audio inputs, targeting French as the output language and disabling speech generation
output_tokens = model.generate(**audio_inputs, tgt_lang="cat", generate_speech=False)

# Decode the output tokens to obtain the translated text from the audio
translated_text_from_audio = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)

# Print the translated text obtained from the audio
print(f"Translated Text: {translated_text_from_audio}")
