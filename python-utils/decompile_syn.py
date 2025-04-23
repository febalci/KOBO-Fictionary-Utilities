import sys

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

            f.read(offset_size + 4)  # Skip offset + length
            words.append(word)
    return words

def decompile_syn_file(base_name, output_txt="decompiled_synonyms.txt", offset_size=4):
    """Decompile .syn file and map synonyms to headwords from the .idx file."""
    syn_file = f"{base_name}.syn"
    idx_file = f"{base_name}.idx"
    
    idx_words = extract_idx_words(idx_file, offset_size)
    synonyms = []

    with open(syn_file, 'rb') as f:
        while True:
            word_bytes = bytearray()
            while True:
                ch = f.read(1)
                if not ch:
                    break  # End of file
                if ch == b'\x00':
                    break
                word_bytes += ch
            if not word_bytes:
                break

            synonym = word_bytes.decode('utf-8')
            index_bytes = f.read(4)
            if len(index_bytes) < 4:
                break
            target_index = int.from_bytes(index_bytes, 'big')

            if target_index < len(idx_words):
                target_word = idx_words[target_index]
            else:
                target_word = f"[INVALID_INDEX_{target_index}]"

            synonyms.append((synonym, target_word))

    # Output to text file
    with open(output_txt, 'w', encoding='utf-8') as f:
        for synonym, target in synonyms:
            f.write(f"{synonym}\t{target}\n")

    print(f"✅ Decompiled to '{output_txt}' with {len(synonyms)} entries.")

# Check if we have the base name as a command line argument
if len(sys.argv) < 2:
    print("Usage: python decompile_syn_file.py <base_name>")
else:
    base_name = sys.argv[1]
    decompile_syn_file(base_name)
