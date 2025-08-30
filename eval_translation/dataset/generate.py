import polib
import subprocess
from pathlib import Path

# Paths to your original po files
PO1 = Path("gnome-ui.po")
PO2 = Path("gnome-docs.po")

# Output smaller po files
SMALL1 = Path("intermediate/gnome-ui-small.po")
SMALL2 = Path("intermediate/gnome-ui-small.po")

# Output tmx files
TMX1 = Path("file1.tmx")
TMX2 = Path("file2.tmx")
MERGED_TMX = Path("merged.tmx")

# Step 1: Read and truncate PO files
from pathlib import Path
import polib

def truncate_po(src: Path, dst: Path, limit: int = 500):
    po = polib.pofile(src)
    new_po = polib.POFile()

    # Copy metadata
    new_po.metadata = po.metadata

    total_entries = len(po)
    if total_entries <= limit:
        # If fewer than limit, just copy everything
        selected_entries = po
    else:
        step = total_entries / limit
        selected_entries = [po[int(i * step)] for i in range(limit)]

    for entry in selected_entries:
        new_po.append(entry)

    new_po.save(dst)
    

def merge_tmx(file1, file2, file3, output):
    # Open files in binary mode
    with open(file1, "rb") as f1, open(file2, "rb") as f2, open(file3, "rb") as f3:
        tmx1 = tmx.tmxfile(f1, 'utf-8')
        tmx2 = tmx.tmxfile(f2, 'utf-8')
        tmx3 = tmx.tmxfile(f3, 'utf-8')

        # Merge units from second and third files into the first
        for unit in tmx2.units:
            tmx1.addunit(unit)
        for unit in tmx3.units:
            tmx1.addunit(unit)

    # Save merged TMX
    with open(output, "wb") as f:
        tmx1.savefile(f)

    # Print number of saved segments
    print(f"Merged TMX contains {len(tmx1.units)} segments.")

truncate_po(PO1, SMALL1)
truncate_po(PO2, SMALL2)

# Step 2: Convert smaller PO files to TMX using translate-toolkit (po2tmx)
subprocess.run(["po2tmx", str(SMALL1), str(TMX1), "-l ca"], check=True)
subprocess.run(["po2tmx", str(SMALL2), str(TMX2), "-l ca"], check=True)

merge_tmx("errors.tmx", "file1.tmx", "file2.tmx", "merged.tmx")


print(f"TMX saved as {MERGED_TMX}")

