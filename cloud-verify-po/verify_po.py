import os
import sys
import polib
from itertools import islice
import time
import google.generativeai as genai

try:
    import openai
except ImportError:
    openai = None  # Will check dynamically if OpenAI is needed


# Configure Google API
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    exit()


def verify(sentences, provider):
    text = ""
    for source, target, comment in sentences:
        text += f"English: {source}\n"
        text += f"Catalan: {target}\n\n"
        text += f"Comment: {comment}\n\n"

    prompt = (
        "Verify if there are major errors in the translation from English to Catalan. "
        "Be to the point in explanations. Do not mention what is correct. "
        "Do not review the comments but provide them as context when reporting an issue. "
        f"{text}"
    )

    if provider.lower() == "gemini":
        model = genai.GenerativeModel("gemini-2.5-pro")
        generation_config = genai.types.GenerationConfig(temperature=0)
        response = model.generate_content(prompt, generation_config=generation_config)
        return response.text

    elif provider.lower() == "openai":
        if openai is None:
            raise ImportError("OpenAI module not installed. Install with `pip install openai`.")

        if "OPENAI_API_KEY" not in os.environ:
            raise EnvironmentError("OPENAI_API_KEY not set in environment variables.")

        openai.api_key = os.environ["OPENAI_API_KEY"]

        response = openai.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content

    else:
        raise ValueError("Invalid provider. Use 'gemini' or 'openai'.")


def extract_po_strings(po_file_path):
    po = polib.pofile(po_file_path)
    translations = [
        (
            entry.msgid.replace("_", ""),
            entry.msgstr.replace("_", ""),
            (entry.comment or "") + (entry.tcomment or ""),
        )
        for entry in po
        if entry.msgid and entry.msgstr and not entry.fuzzy
    ]
    return translations


def batch_iterable(iterable, size):
    iterator = iter(iterable)
    while batch := list(islice(iterator, size)):
        yield batch


BATCH_SIZE = 400

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_po.py <po_file> [provider]")
        sys.exit(1)

    po_file = sys.argv[1]
    provider = sys.argv[2] if len(sys.argv) > 2 else "gemini"

    if not os.path.isfile(po_file):
        print(f"Error: File '{po_file}' does not exist.")
        sys.exit(1)

    # Determine output filename
    base, _ = os.path.splitext(po_file)
    output_file = f"{base}-{provider}.txt"

    strings = list(extract_po_strings(po_file))
    total_strings = len(strings)

    start_time = time.time()

    with open(output_file, "w") as file:
        for i, batch in enumerate(batch_iterable(strings, BATCH_SIZE)):
            batch_start = time.time()
            processed = min((i + 1) * BATCH_SIZE, total_strings)
            percent_done = (processed / total_strings) * 100

            r = verify(batch, provider=provider)
            file.write(f"{r}\n")
            file.write("\n-----------------------\n")

            batch_time = time.time() - batch_start
            print(f"Progress: {percent_done:.2f}% | Batch time: {batch_time:.2f} seconds")

    total_time = time.time() - start_time
    print(f"Strings analyzed: {total_strings}")
    print(f"Output written to: {output_file}")
    print(f"Total time used: {total_time:.2f} seconds")

