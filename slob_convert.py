import os
import re

input_file = "britannica_eb11.tab"
output_file = "britannica_eb11.dsl"

# GoldenDict/Lingvo requires this specific header at the top
header = """#NAME "Encyclopaedia Britannica 11th Ed"
#INDEX_LANGUAGE "English"
#CONTENTS_LANGUAGE "English"
"""

# Regex to find EB11 section headers (e.g., "History. —" or "Physical Features .—")
section_pattern = re.compile(r'(\s+[A-Z][a-zA-Z0-9\s]+?\.?\s*—)')

# We will use two Unicode Em-Spaces to create a distinct, traditional first-line indent
# An Em-space is roughly the width of a capital 'M', preventing the engine from collapsing the spaces.
em_space = "\u2003\u2003" 

print(f"Reading from {input_file} and injecting typographical first-line indents...")

try:
    with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-16') as f_out:
        f_out.write(header + "\n")
        
        count = 0
        for line in f_in:
            if '\t' in line:
                headword, definition = line.split('\t', 1)
                
                parts = section_pattern.split(definition.strip())
                formatted_pieces = []
                current_header = ""
                
                for part in parts:
                    if not part.strip():
                        continue
                        
                    if section_pattern.match(part):
                        # Insert a [br] to create a blank line before the new section
                        if formatted_pieces:
                            formatted_pieces.append("[br]")
                            
                        clean_header = part.strip()
                        current_header = f"[b][i][c maroon]{clean_header}[/c][/i][/b] "
                    else:
                        body = part.strip()
                        
                        # Split by sentences (Punctuation, space, Capital letter)
                        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', body)
                        paragraphs = []
                        
                        if len(sentences) > 6:
                            for i in range(0, len(sentences), 5):
                                paragraphs.append(" ".join(sentences[i:i+5]))
                        else:
                            paragraphs.append(body)
                        
                        # The first paragraph stays flush left with the header. 
                        # If there is NO header (e.g., the very start of the article), we give it the Em Space indent.
                        if current_header:
                            formatted_pieces.append(f"[m1]{current_header}{paragraphs[0]}[/m]")
                            current_header = ""
                        else:
                            formatted_pieces.append(f"[m1]{em_space}{paragraphs[0]}[/m]")
                        
                        # All subsequent paragraphs get [m1] (flush block) but start with Em Spaces for the first-line indent
                        for p in paragraphs[1:]:
                            formatted_pieces.append(f"[m1]{em_space}{p}[/m]")
                
                final_definition = "\n\t".join(formatted_pieces)
                
                f_out.write(f"{headword.strip()}\n")
                f_out.write(f"\t{final_definition}\n")
                count += 1
                
    print(f"Success! Converted and beautifully formatted {count} entries into {output_file}.")

except FileNotFoundError:
    print(f"Error: Could not find '{input_file}'. Make sure it is in the same folder.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")