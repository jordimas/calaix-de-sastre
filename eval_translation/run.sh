sudo pkill -9 python
sudo pkill -9 python3
sleep 30m
cd dataset && python generate.py && cd ..
python reviewer.py --prompt_version 3_1
#python reviewer.py --prompt_version 3_1 --max 1000

