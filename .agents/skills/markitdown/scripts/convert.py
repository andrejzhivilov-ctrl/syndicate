import sys
import os
from markitdown import MarkItDown

if len(sys.argv) < 2:
    print("Usage: convert.py <input_file> [output_file.md]")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(input_file)[0] + ".md"

md = MarkItDown()
res = md.convert(input_file)

with open(output_file, "w", encoding="utf-8") as f:
    f.write(res.text_content)

print(f"Successfully converted {input_file} -> {output_file} ({len(res.text_content)} chars)")
