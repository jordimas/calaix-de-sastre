from faster_whisper import WhisperModel

model_size = "medium"
compute_type = "float32"
model = WhisperModel(model_size, device="cpu", compute_type=compute_type,  cpu_threads=14)

print(f"model: {model_size}, compute_type {compute_type}")

for i in range(0,3):
    segments, info = model.transcribe("15GdH9-curt.mp3")

    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    for segment in segments:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
        if segment.end > 60:
            break

