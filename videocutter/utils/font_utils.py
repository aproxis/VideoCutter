# videocutter/utils/font_utils.py
# Utility functions for font-related operations.

import os
from fontTools.ttLib import TTFont

def get_font_name(font_path):
    """
    Extracts the full font name from a font file.
    Falls back to the filename if the name cannot be extracted.
    """
    try:
        font = TTFont(font_path)
        name = ''
        # Iterate through name records to find the full font name (nameID 4)
        for record in font['name'].names:
            if record.nameID == 4:  # Full font name
                try:
                    # Attempt to decode using the record's encoding
                    name = record.string.decode(record.getEncoding())
                except Exception:
                    # Fallback to UTF-8 if specific encoding fails
                    name = record.string.decode('utf-8', errors='ignore')
                break  # Found the full font name
        font.close()
        if name:
            return name
        else:
            # If no nameID 4 found, try nameID 1 (Family name) as a fallback before filename
            for record in font['name'].names:
                if record.nameID == 1: # Font Family name
                    try:
                        name = record.string.decode(record.getEncoding())
                    except:
                        name = record.string.decode('utf-8', errors='ignore')
                    if name: break
            font.close()
            if name: return name

    except Exception as e:
        print(f"Error extracting font name from {font_path}: {e}")
    
    # Fallback to filename without extension if no name could be extracted
    return os.path.basename(font_path).split('.')[0]

# TODO: Add other font-related utilities:
# - Function to resolve font paths (check local 'fonts/' dir, then system dirs)

if __name__ == "__main__":
    # Example usage (requires a font file for testing)
    # Create a dummy font file for testing if needed, or point to an existing one
    # test_font_path = "path/to/your/font.otf" 
    # if os.path.exists(test_font_path):
    #     font_name = get_font_name(test_font_path)
    #     print(f"Extracted font name: {font_name}")
    # else:
    #     print(f"Test font file not found at {test_font_path}. Skipping example.")
    print("font_utils.py executed directly (for testing).")
