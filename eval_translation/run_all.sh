for i in 3_1 3_2; do
    python reviewer.py --prompt_version "$i"
done

for i in 3_1 3_2; do
    python reviewer.py --prompt_version "$i" --max 1000
done



