import os
import sys

# pyglossary mydict.txt ./mydict --sort --write-format=StardictMergeSyns

if len(sys.argv) < 2:
    print("Usage: python generate_syn.py <base_filename> [synonyms_file]")
    sys.exit(1)

# Get base filename and optional synonyms file
FILENAME_BASE = sys.argv[1]
SYNONYMS_FILE = sys.argv[2] if len(sys.argv) > 2 else "synonyms.txt"

def extract_idx_words(idx_file, offset_size=4):
    """Extract headwords from .idx binary file."""
    words = []
    with open(idx_file, 'rb') as f:
        while True:
            word_bytes = bytearray()
            while True:
                ch = f.read(1)
                if not ch:
                    return words
                if ch == b'\x00':
                    break
                word_bytes += ch
            word = word_bytes.decode('utf-8')
            words.append(word)
            f.read(offset_size + 4)  # Skip offset + length
    return words


def create_syn_file(synonyms_file, idx_file, output_file, offset_size=4):
    """Create sorted .syn file from synonym list and .idx word list."""
    idx_words = extract_idx_words(idx_file, offset_size)
    word_to_index = {word: i for i, word in enumerate(idx_words)}
    entries = []

    with open(synonyms_file, 'r', encoding='utf-8') as f:
        for line in f:
            if '\t' not in line:
                continue
            synonym, target = line.strip().split('\t')
            if target not in word_to_index:
                print(f"❗ Skipping: '{synonym}' → '{target}' (not found in .idx)")
                continue
            entries.append((synonym, word_to_index[target]))

    # 🔠 Sort entries by synonym (case-insensitive)
    entries.sort(key=lambda x: x[0].lower())

    with open(output_file, 'wb') as f:
        for synonym, index in entries:
            f.write(synonym.encode('utf-8') + b'\x00')
            f.write(index.to_bytes(4, 'big'))

    print(f"✅ Created sorted synonym file: {output_file} ({len(entries)} entries)")
    return len(entries)


def update_ifo_file(ifo_path, synonym_count):
    """Update or insert synwordcount in the .ifo file."""
    if not os.path.exists(ifo_path):
        print(f"⚠️ .ifo file not found: {ifo_path}")
        return

    with open(ifo_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    found = False
    for i, line in enumerate(lines):
        if line.startswith('synwordcount='):
            lines[i] = f"synwordcount={synonym_count}\n"
            found = True
            break

    if not found:
        for i, line in enumerate(lines):
            if line.startswith("version="):
                lines.insert(i + 1, f"synwordcount={synonym_count}\n")
                break

    with open(ifo_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"✅ Updated '{ifo_path}' with synwordcount={synonym_count}")


# ===== MAIN WRAPPER =====
def generate_syn_and_update_ifo(base_name, synonyms_file="synonyms.txt", offset_size=4):
    idx_file = f"{base_name}.idx"
    ifo_file = f"{base_name}.ifo"
    syn_output_file = f"{base_name}.syn"

    syn_count = create_syn_file(synonyms_file, idx_file, syn_output_file, offset_size)
    update_ifo_file(ifo_file, syn_count)

# === Run it ===
generate_syn_and_update_ifo(FILENAME_BASE, SYNONYMS_FILE)
