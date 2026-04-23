# SLOB-to-DSL
Convert SLOB file dictionaries to DSL for easier formatting.

This project shall do the following:
1. Convert from SLOB format to DSL format for easier editing and greater compatibility across dictionary applications.
2. Rectify the regrettable 'phone-style' formatting of the SLOB file, that being a dark background, large text and excessive text wrapping.

This project shall be completed by the first of May, 2026.

Project Log:
1. Using TAB file, convert via Python to DSL using regular expressions.
2. Split up entries by header (HEADER --) to make entries easier to read.
3. Change header text to be bold, italic and colored for easy parsing.
4. Automatically split up giant entries into smaller paragraphs. This splits the encylcopedia every 5th sentence of an entry, since there is no way to know without re-ocr-ing the dictionary exactly where the original splits were. 
	Better to have automatic breaks that are incorrect than no breaks at all.
