import multiprocessing
import json
import time
from itertools import islice
from langchain_community.chat_models import ChatLlamaCpp
from langchain.schema import SystemMessage, HumanMessage  # safer than raw tuples
from translate.storage.tmx import tmxfile


# local_model = "/home/jordi/sc/llama/llama.cpp/download/gpt-oss-20b-UD-Q8_K_XL.gguf"
local_model = "/home/jordi/sc/llama/llama.cpp/download/google_gemma-3-27b-it-Q8_0.gguf"


import logging

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
    n_ctx=8192,
    n_gpu_layers=8,
    n_batch=64,  # adjust for your VRAM, but no need to be huge
    max_tokens=512,
    n_threads=max(1, multiprocessing.cpu_count()),
    repeat_penalty=1.1,  # softer penalty helps short JSON
    top_p=1.0,  # fully deterministic with temperature=0
    verbose=False,
)


def translate(english: str, catalan: str) -> str:
    messages = [
        SystemMessage(
            content=(
                "You are an expert English-to-Catalan translation reviewer.\n"
                "Your task is to check ONLY for these two types of errors:\n"
                "1) Complete contradiction: the Catalan translation reverses or negates the key meaning of the English.\n"
                "2) Topic mismatch: the Catalan translation is about a completely different subject than the English.\n\n"
                "Do NOT report:\n"
                " - Differences in tone, style, or formality.\n"
                " - Errors you are not highly confident about.\n\n"
                "Response format:\n"
                " - If there is an error, respond YES with a brief explanation.\n"
                " - If there is no error, respond NO with no explanation."
            )
        ),
        HumanMessage(content=f"English: '''{english}'''\nCatalan: '''{catalan}'''"),
    ]

    ai_msg = llm.invoke(messages)
    answer = (ai_msg.content or "").strip()
    logging.info(f"s: {english}")
    logging.info(f"t: {catalan}")
    logging.info(f"a: {answer}\n")
    return answer


def _write(english: str, catalan: str, note: str, result: str, fh):
    lines = [
        f"English: {english}",
        f"Catalan: {catalan}",
    ]

    if note:
        lines.append(f"Note: {note}")

    lines.append(f"Result: {result}")
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
    total_strings = len(strings)
    errors = 0

    start_time = time.time()

    tp = fp = fn = tn = 0
    with open("output.txt", "w", encoding="utf-8") as file:
        for idx, (en, ca, note) in enumerate(strings, start=1):
            res = translate(en, ca)

            if idx % 10 == 0:
                percent_done = (idx / total_strings) * 100
                total_time = time.time() - start_time

                precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0

                print(
                    f"Progress: {percent_done:.2f}% - {idx}/{total_strings} | "
                    f"Time: {total_time:.2f}s | "
                    f"TP: {tp}, TN: {tn}, FP: {fp}, FN: {fn} | "
                    f"Precision: {precision:.2f}, Recall: {recall:.2f}"
                )

            if res.upper().startswith("NO"):
                if note:
                    fn += 1
                else:
                    tn += 1
                continue

            if note:
                tp += 1
            else:
                fp += 1

            errors += 1
            _write(en, ca, note, res, file)

    total_time = time.time() - start_time
    print(f"Strings analyzed: {total_strings}")
    print(f"Total errors detected: {errors}")
    print(f"Total time used: {total_time:.2f} seconds")
