import polib
import os
import google.generativeai as genai
from itertools import islice

try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    print("Please set the variable, for example: export GOOGLE_API_KEY='YOUR_API_KEY'")
    exit()

model = genai.GenerativeModel("gemini-2.5-pro")


def verify(sentences):
    prompt = (
        "Verify if there are major errors in the translation from English to Catalan. Be to the point in explanations. Do not mention what is correct."
        f"{sentences}"
    )

    response = model.generate_content(prompt)
    return response.text


def extract_po_strings(po_file_path):
    po = polib.pofile(po_file_path)

    translations = [
        (
            entry.msgid.replace("_", ""),
            entry.msgstr.replace("_", ""),
            "" + entry.comment + entry.tcomment,
        )
        for entry in po
        if entry.msgid and entry.msgstr
    ]
    return translations


def batch_iterable(iterable, size):
    iterator = iter(iterable)
    while batch := list(islice(iterator, size)):
        yield batch


import time

BATCH_SIZE = 100

if __name__ == "__main__":
    po_file = "gnome-calendar.po"

    errors = 0
    strings = list(extract_po_strings(po_file))  # Convert to list to get length
    total_strings = len(strings)

    start_time = time.time()  # Start timing overall process

    with open('output.txt', 'w') as file:
        for i, batch in enumerate(batch_iterable(strings, BATCH_SIZE)):
            batch_start = time.time()  # Start timing for batch

            r = verify(batch)
            file.write(f"{r}")
            file.write("-----------------------")

            # Calculate % completed
            processed = min((i + 1) * BATCH_SIZE, total_strings)
            percent_done = (processed / total_strings) * 100

            batch_time = time.time() - batch_start
            print(f"Progress: {percent_done:.2f}% | Batch time: {batch_time:.2f} seconds")

    total_time = time.time() - start_time
    print(f"Strings analyzed: {total_strings}")
    print(f"Total errors detected: {errors}")
    print(f"Total time used: {total_time:.2f} seconds")

