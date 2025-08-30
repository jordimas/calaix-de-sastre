import multiprocessing
import json
import polib
import time
from itertools import islice
from langchain_community.chat_models import ChatLlamaCpp
from langchain.schema import SystemMessage, HumanMessage  # safer than raw tuples

local_model = "/home/jordi/sc/llama/llama.cpp/download/google_gemma-3-12b-it-Q8_0.gguf"

llm = ChatLlamaCpp(
    temperature=0,
    model_path=local_model,
    n_ctx=8192,
    n_gpu_layers=8,
    n_batch=64,          # adjust for your VRAM, but no need to be huge
    max_tokens=64,        # small—it's a single-line JSON classification
    n_threads=max(1, multiprocessing.cpu_count()),
    repeat_penalty=1.1,   # softer penalty helps short JSON
    top_p=1.0,            # fully deterministic with temperature=0
    verbose=False,
)

BATCH_SIZE = 1  # keeping your value

def batch_iterable(iterable, size):
    iterator = iter(iterable)
    while batch := list(islice(iterator, size)):
        yield batch

def extract_po_strings(po_file_path):
    po = polib.pofile(po_file_path)
    translations = [
        (
            (entry.msgid or "").replace("_", "").strip(),
            (entry.msgstr or "").replace("_", "").strip(),
            ((entry.comment or "") + " " + (entry.tcomment or "")).strip(),
        )
        for entry in po
        if entry.msgid and entry.msgstr and not entry.fuzzy
    ]
    return translations

def translate(english: str, catalan: str) -> dict:
    """
    Returns a dict with keys:
      - label: "OK" or "ERROR"
      - type: "opposite" | "unrelated" | None
      - reason: short string (<= 10 words)
    Any parsing failure -> ERROR/unrelated with reason.
    """
    system = SystemMessage(
        content=(
            "You are a strict translation auditor. "
            "Decide if the Catalan text matches the English source."
        )
    )

    # Few-shot to stabilize behavior
    examples = [
        HumanMessage(content=(
            "TASK:\n"
            "Check ONLY these two error types:\n"
            "1) Opposite meaning (contradiction/negation of key idea).\n"
            "2) Completely unrelated to the English (topic mismatch).\n\n"
            "Respond with ONE minified JSON line:\n"
            '{"label":"OK"|"ERROR","type":"opposite"|"unrelated"|null,"reason":"<=10 words"}\n'
            "If unsure, choose ERROR with type 'unrelated'.\n\n"
            "English: '''Open the image in a new tab.'''\n"
            "Catalan: '''Obre la imatge en una pestanya nova.'''"
        )),
        SystemMessage(content='{"label":"OK","type":null,"reason":"Matches source"}'),
        HumanMessage(content=(
            "English: '''Enable the feature to allow uploads.'''\n"
            "Catalan: '''Desactiva la funció per permetre pujades.'''"
        )),
        SystemMessage(content='{"label":"ERROR","type":"opposite","reason":"Negation mismatch"}'),
        HumanMessage(content=(
            "English: '''Click Save to keep your changes.'''\n"
            "Catalan: '''Aquest menú mostra les preferències del teclat.'''"
        )),
        SystemMessage(content='{"label":"ERROR","type":"unrelated","reason":"Different topic"}'),
    ]

    task = HumanMessage(content=(
        "TASK:\n"
        "Check ONLY these two error types:\n"
        "1) Opposite meaning (contradiction/negation of key idea).\n"
        "2) Completely unrelated to the English (topic mismatch).\n\n"
        "Respond with ONE minified JSON line:\n"
        '{"label":"OK"|"ERROR","type":"opposite"|"unrelated"|null,"reason":"<=10 words"}\n'
        "No prose, no code fences, no explanations.\n"
        "If unsure, choose ERROR with type 'unrelated'.\n\n"
        f"English: '''{english}'''\n"
        f"Catalan: '''{catalan}'''"
    ))

    ai_msg = llm.invoke([system, *examples, task])

    raw = (ai_msg.content or "").strip()
    # take last line (some models prepend a newline)
    line = raw.splitlines()[-1].strip()
    try:
        data = json.loads(line)
        # minimal validation
        if data.get("label") not in {"OK", "ERROR"}:
            raise ValueError("bad label")
        if data.get("label") == "OK":
            data["type"] = None
            data["reason"] = data.get("reason") or "Matches source"
        else:
            if data.get("type") not in {"opposite", "unrelated"}:
                data["type"] = "unrelated"
            if not data.get("reason"):
                data["reason"] = "Mismatch"
        return data
    except Exception:
        return {"label": "ERROR", "type": "unrelated", "reason": "Non-JSON response"}

def _write(english: str, catalan: str, result: dict, fh):
    fh.write(f"English: {english}\n")
    fh.write(f"Catalan: {catalan}\n")
    fh.write(f"Result: {json.dumps(result, ensure_ascii=False)}\n")
    fh.write("\n-----------------------\n")

    print(f"English: {english}")
    print(f"Catalan: {catalan}")
    print(f"Result: {json.dumps(result, ensure_ascii=False)}")
    print("\n-----------------------\n")

if __name__ == "__main__":
    po_file = "/home/jordi/sc/tmt/tmt/src/output/gimp-tm.po"

    strings = list(extract_po_strings(po_file))
    total_strings = len(strings)
    errors = 0

    start_time = time.time()

    with open("output2.txt", "w", encoding="utf-8") as file:    
        for idx, (en, ca, _meta) in enumerate(strings, start=1):
            res = translate(en, ca)
            
            if idx % 50 == 0:
                percent_done = (idx / total_strings) * 100
                total_time = time.time() - start_time                
                print(f"Progress: {percent_done:.2f}% - {idx}/{total_strings} | Time: {total_time} seconds")

            if res["label"] == "OK":
                continue

            errors += 1
            _write(en, ca, res, file)


    total_time = time.time() - start_time
    print(f"Strings analyzed: {total_strings}")
    print(f"Total errors detected: {errors}")
    print(f"Total time used: {total_time:.2f} seconds")

