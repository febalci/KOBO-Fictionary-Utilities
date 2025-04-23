import sys

# Check if enough arguments are passed
if len(sys.argv) < 2:
    print("Usage: python extract_words_from_idx.py <idx_filename> [output_txt]")
    sys.exit(1)

# Get the idx file path and optional output file path from the command-line arguments
IDX_FILE = sys.argv[1]  # The idx file path (e.g., 'mydict.idx')
OUTPUT_FILE = sys.argv[2] if len(sys.argv) > 2 else "idx_words.txt"  # The output file (default is 'idx_words.txt')

def extract_words_from_idx(idx_path, output_txt=OUTPUT_FILE, idx_offset_size=4):
    words = []

    with open(idx_path, 'rb') as f:
        while True:
            word_bytes = bytearray()
            while True:
                ch = f.read(1)
                if not ch:
                    break  # EOF
                if ch == b'\x00':
                    break
                word_bytes += ch

            if not word_bytes:
                break  # No more words

            word = word_bytes.decode('utf-8')
            words.append(word)

            # Skip offset + length (typically 4+4 bytes)
            f.read(idx_offset_size + 4)

    with open(output_txt, 'w', encoding='utf-8') as f:
        for word in words:
            f.write(word + '\n')

    print(f"✅ Extracted {len(words)} headwords to: {output_txt}")
    return words

# Run the function with the passed arguments
extract_words_from_idx(IDX_FILE, output_txt=OUTPUT_FILE, idx_offset_size=4)
