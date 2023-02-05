import os
from evaluate import load
import sys
from transformers.models.whisper.english_normalizer import BasicTextNormalizer
whisper_norm = BasicTextNormalizer()

def evaluate(reference_file, prediction_file):
    with open(reference_file) as f:
        reference = f.read()

    with open(prediction_file) as f:
        prediction = f.read()
    
    _wer = load("wer")
    wer_score = _wer.compute(predictions=[whisper_norm(prediction)], references=[whisper_norm(reference)])
    wer_score = wer_score * 100
    
    normalizer = BasicTextNormalizer()

    wer_score_normalized = _wer.compute(predictions=[normalizer(prediction)], references=[normalizer(reference)])
    wer_score_normalized = wer_score_normalized * 100

    return wer_score, wer_score_normalized
    
def single_model(model):
    wer_score, time = inference("samples/15GdH9-curt.mp3", model)
    print(f"time: {time}, wer: {wer_score:.2f}, model: {model}")
                 
def main():
    reference_file = "15GdH9-curt.txt"
    prediction_files = ["15GdH9-curt-medium.wav.txt",
                        "15GdH9-curt-sc-medium-2000.wav.txt"]
    descriptions = ["Transcription done using OpenAI medium model with whisper.cpp tool",
                    "Transcription done using fine-tuned medium model (https://huggingface.co/jordimas/whisper-medium-ca-2000steps) with whisper.cpp tool"]
    for i in range(0, len(prediction_files)):
        prediction_file = prediction_files[i]
        description = descriptions[i]
        wer_score, wer_score_normalized = evaluate(reference_file, prediction_file)
        print(f"description: {description}")
        print(f"file: {prediction_file}")
        print(f"wer: {wer_score:.2f}")
        print(f"wer normalized: {wer_score_normalized:.2f}\n")

if __name__ == "__main__":
    main()
