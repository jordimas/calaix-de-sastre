from transformers import AutoProcessor
from transformers import SeamlessM4TModel
import scipy
import torch

model = SeamlessM4TModel.from_pretrained("facebook/hf-seamless-m4t-large")


device = "cuda:0" if torch.cuda.is_available() else "cpu"
model = model.to(device)

processor = AutoProcessor.from_pretrained("facebook/hf-seamless-m4t-large")

text = "Softcatalà és una associació sense ànim de lucre amb la missió de fomentar la presència i l'ús del català en tots els àmbits de les noves tecnologies"
text_inputs = processor(text = text, src_lang="cat", return_tensors="pt").to(device)

audio_array_from_text = model.generate(**text_inputs, tgt_lang="cat")[0].cpu().numpy().squeeze()

sample_rate=16000
scipy.io.wavfile.write("tts-softcatala.wav", rate=sample_rate, data=audio_array_from_text) 
