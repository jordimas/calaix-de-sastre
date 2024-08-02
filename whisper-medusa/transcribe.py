from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torchaudio
import torch

# Load the Whisper model and processor
model_name = "aiola/whisper-medusa-v1"
processor = WhisperProcessor.from_pretrained(model_name)
model = WhisperForConditionalGeneration.from_pretrained(model_name)

# Load your audio file
def load_and_prepare_audio(file_path):
    # Load audio
    audio, sample_rate = torchaudio.load(file_path)
        
    return audio.squeeze(), sample_rate

# Load and prepare audio
audio, sample_rate = load_and_prepare_audio("Andrew_Dessler.wav")

# Convert audio to input features
input_features = processor(audio, sampling_rate=sample_rate, return_tensors="pt").input_features 

# Generate token ids
with torch.no_grad():
    predicted_ids = model.generate(input_features)

transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
print("** Transcription:", transcription)

