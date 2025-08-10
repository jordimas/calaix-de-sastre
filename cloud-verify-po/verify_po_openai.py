import openai
import polib

client = openai.OpenAI()


def verify(sentence, target):
    system = (
        "Verify if there are major errors in the translation from English to Catalan."
        f" A major error is a servere mistranslation, missing words, or severe incorrect meaning."
        f" Respond with 'YES' if the translation is correct, otherwise respond 'NO' and briefly explain the issue."
    )  #                f"\n\nEnglish: {sentence}\nCatalan: {target}",

    user = f'Verify English to Catalan translation:"\n\nEnglish: {sentence}\nCatalan: {target}'

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        max_tokens=2000,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )

    message = response.choices[0].message.content
    #    print(f"system: {system}")
    #    print(f"user: {user}")
    #    print(f"message: {message}")
    return message


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


# Example usage
if __name__ == "__main__":
    po_file = "gnome-calendar.po"

    errors = 0
    strings = 0
    for source, target, comment in extract_po_strings(po_file):
        result = verify(source, target)
        strings += 1
        if "yes" != result.lower().strip()[0:3]:
            print(f"Source: {source} ({strings})")
            print(f"Target: {target}")

            if comment:
                print(f"Comment: {comment}")

            print(f"Result: {result}\n----------------------------\n")

    print(f"Strings analized: {strings}")
    print(f"Total errors detected: {errors}")
