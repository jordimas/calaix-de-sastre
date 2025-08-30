sudo pkill -9 python
sudo pkill -9 python3
cd dataset && python generate.py && cd ..
python reviewer.py
