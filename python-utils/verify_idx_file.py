# Usage: python verify_idx_file.py mydict.idx
import sys

# Check if enough arguments are passed
if len(sys.argv) < 2:
    print("Usage: python verify_idx_file.py <idx_filename>")
    sys.exit(1)

# Get the idx filename from the command line argument
IDX_FILE = sys.argv[1]

# Quick script to preview the first 10 headwords in the .idx file
def preview_idx_words(idx_file, offset_size=4):
    words = []
    with open(idx_file, 'rb') as f:
        for _ in range(10):  # First 10 entries
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

# Print the preview of the first 10 words
print(preview_idx_words(IDX_FILE, offset_size=4))
