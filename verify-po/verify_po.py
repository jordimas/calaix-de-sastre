import polib
import multiprocessing
from langchain_community.chat_models import ChatLlamaCpp


# See: https://github.com/google-gemini/gemma-cookbook


local_model = "/home/jordi/sc/llama/llama.cpp/download/gemma-2-27b-it-Q4_K_M.gguf"
local_model = "/home/jordi/sc/llama/llama.cpp/download/gemma-2-9b-it-Q4_K_M.gguf"


llm = ChatLlamaCpp(
    temperature=0,
    model_path=local_model,
    n_ctx=8192,
    n_gpu_layers=8,
    n_batch=300,  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
    max_tokens=512,
    n_threads=multiprocessing.cpu_count() - 1,
    repeat_penalty=1.5,
    top_p=0.5,
    verbose=False,
)


def verify(sentence, target):
    prompt_v1 = [
        (
            "human",
            f"Verify if there are major errors in the translation from English to Catalan."
            f" A major error is a servere mistranslation, missing words, or severe incorrect meaning."
            f" Respond with 'YES' if the translation is correct, otherwise respond 'NO' and briefly explain the issue."
            f"\n\nEnglish: {sentence}\nCatalan: {target}",
        )
    ]

    prompt_v2 = [
        (
            "human",
            f"Verify if there are major errors in the translation from English to Catalan. A major error is:"
            f" - A servere mistranslation, missing words, or severe incorrect meaning."
            f" - A servere mistranslation, missing words, or severe incorrect meaning."
            f" Respond with 'YES' if the translation has a major error, otherwise respond 'NO' and briefly explain the issue."
            f"\n\nEnglish: {sentence}\nCatalan:´´´{target}´´´",
        )
    ]

    prompt_v3 = [
        (
            "human",
            f"Verify if there are major errors in the translation from English to Catalan. "
            f" A major error is ONLY a seriously incorrect meaning mistake in the Catalan translation."
            f" Respond with 'YES' if the translation contains a major issue and briefly explain the issue. Otherwise, respond 'NO'"
            f'\n\nEnglish: "{sentence}"\nCatalan: "{target}"',
        )
    ]

    prompt_v4 = [
        (
            "human",
            f"Verify if there are major errors in the translation from English to Catalan. "
            f" A major error is ONLY:"
            f" - When the meaning of the translation is opposite"
            f" - When the meaning of the translation has nothing to do with the original"                                    
            f" Respond with 'YES' if the translation contains a major issue and briefly explain the issue. Otherwise, respond 'NO'"
            f'\n\nEnglish: "{sentence}"\nCatalan: "{target}"',
        )
    ]

    ai_msg = llm.invoke(prompt_v4)
    return ai_msg.content.strip()


def extract_po_strings(po_file_path):
    po = polib.pofile(po_file_path)

    translations = [
        (
            entry.msgid.replace("_", ""),
            entry.msgstr.replace("_", ""),
            "" + entry.comment + " " + entry.tcomment,
        )
        for entry in po
        if entry.msgid and entry.msgstr
    ]
    return translations


# Example usage
if __name__ == "__main__":
    po_file = "gimp-doc.po"

    errors = 0
    strings = 0
    for source, target, comment in extract_po_strings(po_file):
        strings += 1
#        if strings < 881:
#            continue

        result = verify(source, target)

        if "yes" == result.lower().strip()[0:3]:
            if comment:
                print(f"Comment: {comment}")
        
            print(f"Source: {source} ({strings})")
            print(f"Target: {target}")


            print(f"Result: {result}\n----------------------------\n")

            errors += 1

    print(f"model: {local_model}")
    print(f"Strings analized: {strings}")
    print(f"Total errors detected: {errors}")
