import os
import re

input_file = "britannica_eb11.tab"
output_file = "britannica_eb11.dsl"

header = """#NAME "Encyclopaedia Britannica 11th Ed"
#INDEX_LANGUAGE "English"
#CONTENTS_LANGUAGE "English"
"""

section_pattern = re.compile(r'(\s+[A-Z][a-zA-Z0-9\s]+?\.?\s*—)')
em_space = "\u2003\u2003" 

print("Pass 1: Building a smart memory bank of headwords...")
headwords_db = set()

try:
    with open(input_file, 'r', encoding='utf-8') as f_in:
        for line in f_in:
            if '\t' in line:
                hw = line.split('\t')[0].strip()
                # istitle() ensures we grab multi-word titles like "Martin Luther" 
                # as long as both words are capitalized.
                if hw.istitle() and len(hw) > 4:
                    headwords_db.add(hw)

    print(f"Loaded {len(headwords_db)} valid headwords for cross-referencing.")
    print("Pass 2: Formatting text and injecting multi-word hyperlinks...")

    with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-16') as f_out:
        f_out.write(header + "\n")
        
        count = 0
        for line in f_in:
            if '\t' in line:
                headword, definition = line.split('\t', 1)
                current_hw = headword.strip()
                
                # Smart function to handle multi-word sequences
                def link_replacer(match):
                    phrase = match.group(1)
                    words = phrase.split()
                    n = len(words)
                    
                    result = []
                    i = 0
                    # Sliding window: Try to find the longest matching phrase first
                    while i < n:
                        match_found = False
                        for j in range(n, i, -1):
                            sub_phrase = " ".join(words[i:j])
                            
                            # If the sequence exists and isn't the current article
                            if sub_phrase in headwords_db and sub_phrase != current_hw:
                                result.append(f"<<{sub_phrase}>>")
                                i = j  # Skip ahead past the words we just linked
                                match_found = True
                                break
                                
                        # If no multi-word or single-word match was found, leave the word alone
                        if not match_found:
                            result.append(words[i])
                            i += 1
                            
                    return " ".join(result)

                parts = section_pattern.split(definition.strip())
                formatted_pieces = []
                current_header = ""
                
                for part in parts:
                    if not part.strip():
                        continue
                        
                    if section_pattern.match(part):
                        if formatted_pieces:
                            formatted_pieces.append("[br]")
                        clean_header = part.strip()
                        current_header = f"[b][i][c maroon]{clean_header}[/c][/i][/b] "
                    else:
                        body = part.strip()
                        
                        # UPDATED REGEX: Captures sequences of one OR MORE capitalized words separated by spaces
                        linked_body = re.sub(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', link_replacer, body)
                        
                        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', linked_body)
                        paragraphs = []
                        
                        if len(sentences) > 6:
                            for i in range(0, len(sentences), 5):
                                paragraphs.append(" ".join(sentences[i:i+5]))
                        else:
                            paragraphs.append(linked_body)
                        
                        if current_header:
                            formatted_pieces.append(f"[m1]{current_header}{paragraphs[0]}[/m]")
                            current_header = ""
                        else:
                            formatted_pieces.append(f"[m1]{em_space}{paragraphs[0]}[/m]")
                        
                        for p in paragraphs[1:]:
                            formatted_pieces.append(f"[m1]{em_space}{p}[/m]")
                
                final_definition = "\n\t".join(formatted_pieces)
                
                f_out.write(f"{current_hw}\n")
                f_out.write(f"\t{final_definition}\n")
                count += 1
                
    print(f"Success! Converted, formatted, and smartly hyperlinked {count} entries into {output_file}.")

except FileNotFoundError:
    print(f"Error: Could not find '{input_file}'. Make sure it is in the same folder.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")