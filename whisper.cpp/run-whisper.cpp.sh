ffmpeg -i 15GdH5.mp3 -ar 16000 -ac 1 -c:a pcm_s16le input.wav -y 
./main  --threads 14  -m models/ggml-medium.bin -f input.wav -l ca -otxt  -osrt

