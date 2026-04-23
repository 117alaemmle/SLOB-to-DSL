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

# --- THE BLACKLIST ---
# These words will never be linked if they appear by themselves.
# However, they WILL be linked if they are part of a longer valid name 
# (e.g., "Queen" is ignored, but "Mary, Queen of Scots" is linked).
blacklist = {
    # Days of the week
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    # Months of the year
    "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December",
    # Common Titles
    "King", "Queen", "Prince", "Princess", "Duke", "Lord", "Lady", "Sir", "Saint", "Pope"
}

print("Pass 1: Building a smart, un-inverted memory bank of headwords...")

headwords_db = {}

try:
    with open(input_file, 'r', encoding='utf-8') as f_in:
        for line in f_in:
            if '\t' in line:
                hw = line.split('\t')[0].strip()
                
                if hw.istitle() and len(hw) > 4:
                    headwords_db[hw] = hw
                    
                    if ", " in hw:
                        parts = hw.split(", ", 1)
                        natural_name = f"{parts[1]} {parts[0]}"
                        headwords_db[natural_name] = hw

    print(f"Loaded and mapped {len(headwords_db)} valid headwords and aliases.")
    print("Pass 2: Formatting text and injecting multi-word hyperlinks...")

    with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-16') as f_out:
        f_out.write(header + "\n")
        
        count = 0
        for line in f_in:
            if '\t' in line:
                headword, definition = line.split('\t', 1)
                current_hw = headword.strip()
                
                def link_replacer(match):
                    phrase = match.group(1)
                    words = phrase.split()
                    n = len(words)
                    
                    result = []
                    i = 0
                    while i < n:
                        match_found = False
                        for j in range(n, i, -1):
                            sub_phrase = " ".join(words[i:j])
                            
                            if sub_phrase in headwords_db:
                                target_hw = headwords_db[sub_phrase]
                                
                                # Check against self-linking AND the blacklist
                                if target_hw != current_hw and sub_phrase not in blacklist:
                                    result.append(f"<<{target_hw}>>")
                                    i = j
                                    match_found = True
                                    break
                                    
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
                        
                        linked_body = re.sub(r'\b([A-Z][a-z]+(?:\s+(?:[a-z]{1,3}\s+)?[A-Z][a-z]+)*)\b', link_replacer, body)
                        
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