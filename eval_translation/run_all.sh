sudo pkill -9 python
sudo pkill -9 python3
cd dataset && python generate.py && cd ..

for i in 1 2 2_1 3; do
    python reviewer.py --prompt_version "$i"
done


