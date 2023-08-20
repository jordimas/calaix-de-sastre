import polib
import sys

def main():
    po = polib.pofile(sys.argv[1])
    
    catalan = {}
    for entry in po.translated_entries():
        catalan[entry.msgid] = entry.msgstr 

    po = polib.pofile(sys.argv[2])
    
    diff = 0
    name_1 = sys.argv[1].replace(".po", "")
    name_2 = sys.argv[2].replace(".po", "")
    for entry in po.translated_entries():
        cat_msgstr = catalan.get(entry.msgid)
        if not cat_msgstr:
            continue
        
        if cat_msgstr == entry.msgstr:
            continue
            
        diff += 1
        print(f"English: {entry.msgid}")
        print(f"{name_1}: {entry.msgstr}")
        print(f"{name_2}: {cat_msgstr}\n")

    total = len(po.translated_entries())
    pdiff = diff * 100 / total
    print(f"Total entries {total}")
    print(f"Different: {diff} ({pdiff:.2f}%)")

if __name__ == "__main__":
    main()
