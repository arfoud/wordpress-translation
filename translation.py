import re
import time
import os
from deep_translator import GoogleTranslator

# --- CONFIGURATION ---
INPUT_FILE = 'post.xml'      # Replace with your actual XML filename
OUTPUT_FILE = 'post-es.xml' # The new translated file
SOURCE_LANG = 'en'                  # English
TARGET_LANG = 'es'                  # Spanish
SLEEP_TIME = 0.5                    # Seconds to wait between chunks to avoid Google rate limits
# ---------------------

translator = GoogleTranslator(source=SOURCE_LANG, target=TARGET_LANG)

def translate_single_chunk(text):
    """Translates a single chunk of text, handling empty strings and errors."""
    if not text.strip():
        return text
    try:
        return translator.translate(text)
    except Exception as e:
        print(f"   [!] Translation error: {e}. Returning original text for this chunk.")
        return text

def translate_text(text):
    """
    Splits text into chunks to respect the 5000 character limit of Google Translate.
    Splits by newlines first to preserve HTML structure.
    """
    if not text.strip():
        return text
    
    paragraphs = text.split('\n')
    translated_paragraphs = []
    current_chunk = ""
    
    for p in paragraphs:
        # If adding this paragraph exceeds the 4500 char safe limit
        if len(current_chunk) + len(p) + 1 > 4500:
            if current_chunk:
                translated_paragraphs.append(translate_single_chunk(current_chunk))
                time.sleep(SLEEP_TIME) # Prevent rate limiting
                current_chunk = ""
            
            # If a single line/paragraph is still too long, split by words
            if len(p) > 4500:
                words = p.split(' ')
                word_chunk = ""
                for w in words:
                    if len(word_chunk) + len(w) + 1 > 4500:
                        translated_paragraphs.append(translate_single_chunk(word_chunk))
                        time.sleep(SLEEP_TIME)
                        word_chunk = w + " "
                    else:
                        word_chunk += w + " "
                if word_chunk:
                    current_chunk = word_chunk
            else:
                current_chunk = p + "\n"
        else:
            current_chunk += p + "\n"
            
    if current_chunk:
        translated_paragraphs.append(translate_single_chunk(current_chunk))
        time.sleep(SLEEP_TIME)
        
    return "".join(translated_paragraphs)

# --- Regex Replacement Functions ---
# We use regex to perfectly preserve the XML tags and CDATA wrappers.

def replace_title(match):
    prefix, text, suffix = match.group(1), match.group(2), match.group(3)
    print(f"   Translating Title: {text[:50]}...")
    return prefix + translate_text(text) + suffix

def replace_content(match):
    prefix, text, suffix = match.group(1), match.group(2), match.group(3)
    print(f"   Translating Content block ({len(text)} chars)...")
    return prefix + translate_text(text) + suffix

def replace_excerpt(match):
    prefix, text, suffix = match.group(1), match.group(2), match.group(3)
    print(f"   Translating Excerpt: {text[:50]}...")
    return prefix + translate_text(text) + suffix

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Could not find '{INPUT_FILE}'. Please check the filename.")
        return

    print(f"Reading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        xml_content = f.read()

    print("Starting translation... (This may take a while for large files)")
    
    # 1. Translate Content (Do this first so inner tags don't get messed up)
    # Matches: <content:encoded><![CDATA[ ... ]]></content:encoded>
    content_pattern = re.compile(r'(<content:encoded><!\[CDATA\[)(.*?)(\]\]></content:encoded>)', re.DOTALL)
    xml_content = content_pattern.sub(replace_content, xml_content)

    # 2. Translate Excerpts
    # Matches: <excerpt:encoded><![CDATA[ ... ]]></excerpt:encoded>
    excerpt_pattern = re.compile(r'(<excerpt:encoded><!\[CDATA\[)(.*?)(\]\]></excerpt:encoded>)', re.DOTALL)
    xml_content = excerpt_pattern.sub(replace_excerpt, xml_content)

    # 3. Translate Titles
    # Matches: <title> ... </title>
    title_pattern = re.compile(r'(<title>)(.*?)(</title>)')
    xml_content = title_pattern.sub(replace_title, xml_content)

    print(f"\nTranslation complete! Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    print("Success! You can now import 'translated-export.xml' into WordPress.")

if __name__ == "__main__":
    main()
