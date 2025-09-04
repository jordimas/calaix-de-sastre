for i in 1 2 2_1 3 3_1 4 5; do
    python reviewer.py --prompt_version "$i"
    python reviewer.py --prompt_version "$i" --max 1000
done


