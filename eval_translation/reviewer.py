import multiprocessing
import time
from langchain_community.chat_models import ChatLlamaCpp
from langchain.schema import SystemMessage, HumanMessage  # safer than raw tuples
from translate.storage.tmx import tmxfile
import os
from datetime import datetime
import yaml
import argparse
import logging


local_model = "/home/jordi/sc/llama/llama.cpp/download/google_gemma-3-27b-it-Q8_0.gguf"


# Configure logging
logging.basicConfig(
    filename="reviewer.log",  # log file name
    filemode="w",  # append mode ('w' to overwrite each run)
    level=logging.INFO,  # minimum log level
    format="%(asctime)s - %(levelname)s - %(message)s",
)


llm = ChatLlamaCpp(
    temperature=0,
    model_path=local_model,
    n_ctx=2048,
    n_gpu_layers=8,
    n_batch=64,  # adjust for your VRAM, but no need to be huge
    max_tokens=128,
    n_threads=max(1, multiprocessing.cpu_count()),
    repeat_penalty=1.1,  # softer penalty helps short JSON
    top_p=1.0,  # fully deterministic with temperature=0
    verbose=False,
)


def get_args():
    parser = argparse.ArgumentParser(
        description="Run translation reviewer with a specific prompt version."
    )
    parser.add_argument(
        "--prompt_version",
        type=str,
        default="2_1",  # default value if not provided
        help="Version of the prompt to use (e.g., 2_1, 3_0, etc.)",
    )

    parser.add_argument(
        "--max",
        type=int,
        default=200,
        help="Maximum number to process",
    )

    args = parser.parse_args()
    return args.prompt_version, args.max


prompt_version, MAX = get_args()


def load_prompt():
    # Open the file in read mode
    with open(f"config/prompt-v{prompt_version}.txt", "r") as file:
        data = file.read()  # Read the entire file into a variable

    return data


def load_metadata():
    with open(f"config/metadata-v{prompt_version}.yml", "r") as file:
        config = yaml.safe_load(file)

    return config


prompt = load_prompt()
metadata = load_metadata()


def translate(english: str, catalan: str) -> str:
    english = english.replace("_", "")
    catalan = catalan.replace("_", "")
    messages = [
        SystemMessage(content=(prompt)),
        HumanMessage(content=f"English: '''{english}'''\nCatalan: '''{catalan}'''"),
    ]
    ai_msg = llm.invoke(messages)
    answer = (ai_msg.content or "").strip()
    logging.info(f"s: {english}")
    logging.info(f"t: {catalan}")
    logging.info(f"a: {answer}\n")
    return answer


def _write(english: str, catalan: str, note: str, result: str, fh, status: str):
    lines = [
        f"English: {english}",
        f"Catalan: {catalan}",
    ]

    if note:
        lines.append(f"Note: {note}")

    lines.append(f"Result: {result}")
    lines.append(f"Status: {status}")
    lines.append("\n-----------------------\n")

    content = "\n".join(lines)
    fh.write(content + "\n")
    print(content)


def load_strings(dataset):
    # Open the TMX file
    with open(dataset, "rb") as file:
        tmx = tmxfile(file, "en", "ca")

    strings = []
    for tu in tmx.unit_iter():
        source = tu.source
        target = tu.target
        note = tu.getnotes()
        strings.append((source, target, note))
    return strings


if __name__ == "__main__":
    dataset = "dataset/dataset.tmx"

    strings = load_strings(dataset)
    total_strings = min(len(strings), MAX)
    errors = 0

    start_time = time.time()

    tp = fp = fn = tn = 0
    processed = 0
    with open(
        f"output/results-v{prompt_version}-{MAX}.txt", "w", encoding="utf-8"
    ) as file:
        for idx, (en, ca, note) in enumerate(strings, start=1):
            res = translate(en, ca)
            processed += 1

            if idx % 10 == 0 or idx == MAX:
                percent_done = (idx / total_strings) * 100
                total_time = time.time() - start_time

                precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                set_sec = processed / total_time * 60 if (total_time) > 0 else 0
                print(
                    f"Progress: {percent_done:.2f}% - {idx}/{total_strings} | set/min: {set_sec:.2f}| "
                    f"Time: {total_time:.2f}s | "
                    f"TP: {tp}, TN: {tn}, FP: {fp}, FN: {fn} | "
                    f"Precision: {precision:.2f}, Recall: {recall:.2f}"
                )

            if idx > 0 and idx == MAX:
                break

            if res.upper().startswith("NO"):
                if note:
                    fn += 1
                    _write(en, ca, note, res, file, "fn")
                    continue
                else:
                    tn += 1
                continue

            if note:
                tp += 1
                _write(en, ca, note, res, file, "tp")
            else:
                fp += 1
                _write(en, ca, note, res, file, "fp")

    total_time = time.time() - start_time
    total_time = f"{total_time:.2f}"
    print(f"Total time used: {total_time:} seconds")

    csv = f"output/stats_{MAX}.csv"
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    if os.path.exists(csv):
        # File exists, append data
        mode = "a"
        write_header = False
    else:
        # File doesn't exist, create file and write header
        mode = "w"
        write_header = True

    goal = metadata["goal"]
    with open(csv, mode, encoding="utf-8") as fh:
        if write_header:
            header = "date_time\tprompt_version\tgoal\ttp\tfp\tfn\ttn\tprecision\trecall\ttotal_time\tstrings"
            fh.write(header + "\n")

        # Get current date and time in a readable format
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context = f"{now}\t{prompt_version}\t{goal}\t{tp}\t{fp}\t{fn}\t{tn}\t{precision:.2f}\t{recall:.2f}\t{total_time}\t{processed}"
        fh.write(context + "\n")
