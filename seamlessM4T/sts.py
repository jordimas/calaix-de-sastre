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


# Resample the audio if the sampling rate is different from the model's sampling rate
if audio_sampling_rate != model.config.sampling_rate:
    audio_sample = torchaudio.functional.resample(audio_sample,
                                                  orig_freq=audio_sampling_rate,
                                                  new_freq=model.config.sampling_rate)

# Process the audio inputs
audio_inputs = processor(audios=audio_sample, 
                         return_tensors="pt",
                         sampling_rate=sample_rate).to(device)

# Generate speech from the processed audio inputs
audio_array_from_audio = model.generate(**audio_inputs, tgt_lang="spa")[0].cpu().numpy().squeeze()

# Displaying the generated audio using IPython's Audio function
import scipy
sample_rate=16000
scipy.io.wavfile.write("sts-cat-spa.wav", rate=sample_rate, data=audio_array_from_text) 
