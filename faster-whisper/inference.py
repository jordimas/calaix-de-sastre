from faster_whisper import WhisperModel

model = WhisperModel("small", device="auto")

segments, info = model.transcribe("file.mp3")

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
    if segment.end > 60:
        break

