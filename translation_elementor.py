import re
import time
import os
from deep_translator import GoogleTranslator

# --- CONFIGURATION ---
INPUT_FILE = 'your-export.xml'      
OUTPUT_FILE = 'translated-export.xml' 
SOURCE_LANG = 'en'                  
TARGET_LANG = 'es'                  
SLEEP_TIME = 0.2                    
# ---------------------

translator = GoogleTranslator(source=SOURCE_LANG, target=TARGET_LANG)

# This regex matches HTML tags (e.g., <div class="x">) AND Shortcodes (e.g., [vc_row])
TAG_PATTERN = re.compile(r'(</?[a-zA-Z][^>]*>|\[/?[a-zA-Z_][^\]]*\])')

def translate_single_chunk(text):
    if not text.strip():
        return text
    try:
        return translator.translate(text)
    except Exception as e:
        print(f"   [!] Error translating chunk: {e}")
        return text

def translate_smart_text(text):
    """
    Splits text by HTML tags and Shortcodes. 
    Only translates the plain text between them.
    """
    if not text.strip():
        return text
    
    # Split the text into a list of tags/shortcodes and plain text
    parts = TAG_PATTERN.split(text)
    translated_parts = []
    
    for part in parts:
        if TAG_PATTERN.match(part):
            # It's an HTML tag or a Shortcode. DO NOT TRANSLATE. Keep it exactly as is.
            translated_parts.append(part)
        else:
            # It's plain text. Translate it.
            if part.strip():
                translated_parts.append(translate_single_chunk(part))
                time.sleep(SLEEP_TIME)
            else:
                # It's just whitespace, keep it to preserve formatting
                translated_parts.append(part)
                
    return "".join(translated_parts)

# --- Regex Replacement Functions ---

def replace_content(match):
    prefix, text, suffix = match.group(1), match.group(2), match.group(3)
    print(f"   Translating Content block ({len(text)} chars)...")
    # We translate the text safely
    translated_text = translate_smart_text(text)
    return prefix + translated_text + suffix

def replace_excerpt(match):
    prefix, text, suffix = match.group(1), match.group(2), match.group(3)
    print(f"   Translating Excerpt...")
    return prefix + translate_smart_text(text) + suffix

def replace_title(match):
    prefix, text, suffix = match.group(1), match.group(2), match.group(3)
    print(f"   Translating Title: {text[:50]}...")
    return prefix + translate_single_chunk(text) + suffix

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Could not find '{INPUT_FILE}'.")
        return

    print(f"Reading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        xml_content = f.read()

    print("Starting SMART translation (Protecting HTML & Shortcodes)...")
    
    # 1. Translate Content
    content_pattern = re.compile(r'(<content:encoded><!\[CDATA\[)(.*?)(\]\]></content:encoded>)', re.DOTALL)
    xml_content = content_pattern.sub(replace_content, xml_content)

    # 2. Translate Excerpts
    excerpt_pattern = re.compile(r'(<excerpt:encoded><!\[CDATA\[)(.*?)(\]\]></excerpt:encoded>)', re.DOTALL)
    xml_content = excerpt_pattern.sub(replace_excerpt, xml_content)

    # 3. Translate Titles
    title_pattern = re.compile(r'(<title>)(.*?)(</title>)')
    xml_content = title_pattern.sub(replace_title, xml_content)

    # NOTE: We intentionally DO NOT touch <wp:postmeta>. 
    # This protects Elementor's _elementor_data JSON and other critical plugin settings.

    print(f"\nTranslation complete! Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    print("Success! Your page builder layouts should now be intact.")

if __name__ == "__main__":
    main()