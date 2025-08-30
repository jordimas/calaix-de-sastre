import multiprocessing
import json
import time
from itertools import islice
from langchain_community.chat_models import ChatLlamaCpp
from langchain.schema import SystemMessage, HumanMessage  # safer than raw tuples
from translate.storage.tmx import tmxfile


local_model = "/home/jordi/sc/llama/llama.cpp/download/gpt-oss-20b-UD-Q8_K_XL.gguf"
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
                "You are an English to Catalan translation reviewer expert.\n"
                "Check ONLY these two error types:\n"
                "1) Completely opposite meaning (contradiction/negation of key idea).\n"
                "2) Completely topic mismatch to the English.\n"
                "Respond YES if there is an error with a short explanation.\n"
                "Respond NO if there is no error with no explanation."
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


def translate_old(english: str, catalan: str) -> str:

    task = (
        "TASK:\n"
        "You are an English to Catalan translation reviewer expert.\n"
        "Check ONLY these two error types:\n"
        "1) Opposite meaning (contradiction/negation of key idea).\n"
        "2) Completely topic mismatch to the English.\n"
        "Respond YES if there is an error with a short explanation:\n"
        "Respond NO if there is no error with no explanation\n"
        f"English: '''{english}'''\n"
        f"Catalan: '''{catalan}'''"
    )

    ai_msg = llm.invoke(task)

    answer = (ai_msg.content or "").strip()
    logging.info(f"s: {english}")
    logging.info(f"t: {catalan}")
    logging.info(f"a: {answer}\n")
    return answer


def _write(english: str, catalan: str, result: str, fh):
    fh.write(f"English: {english}\n")
    fh.write(f"Catalan: {catalan}\n")
    fh.write(f"Result:  {result}\n")
    fh.write("\n-----------------------\n")

    print(f"English: {english}")
    print(f"Catalan: {catalan}")
    print(f"Result: {result}")
    print("\n-----------------------\n")


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

    with open("output.txt", "w", encoding="utf-8") as file:
        for idx, (en, ca, note) in enumerate(strings, start=1):
            res = translate(en, ca)

            if res.upper().startswith("NO"):
                continue

            if idx % 50 == 0:
                percent_done = (idx / total_strings) * 100
                total_time = time.time() - start_time
                print(
                    f"Progress: {percent_done:.2f}% - {idx}/{total_strings} | Time: {total_time} seconds"
                )

            errors += 1
            _write(en, ca, res, file)

    total_time = time.time() - start_time
    print(f"Strings analyzed: {total_strings}")
    print(f"Total errors detected: {errors}")
    print(f"Total time used: {total_time:.2f} seconds")
