# wordpress-translation
You can automatically translate your WordPress website
The Solution: A "Smart" Translation Script
To fix this, we need a script that only translates the plain text and completely ignores HTML tags, HTML attributes, and Shortcode parameters.
Here is the upgraded, "Page-Builder Safe" script.
Step 1: Update your libraries
You only need deep-translator. (Open terminal):

pip install deep-translator

Step 2: The Python Script

Save the following code as translate_wp.py in the same folder as your XML file.

python translate_wp.py

Watch the console. It will print out what it is translating. Because of the time.sleep() added to prevent Google from blocking your IP, it will take some time for large files.

Step 3: Import into WordPress

Go to your WordPress Dashboard -> Tools -> Import.
Choose WordPress and install the importer if you haven't already.
Upload your new translated-export.xml file.
Important: When asked to "Assign authors" or "Import attachments", make sure to check "Download and import file attachments" if you want the images to come over (Note: images will keep their original English filenames, but the text inside the posts will be Spanish).
Why this script is safe:
Ignores Metadata: It deliberately skips <wp:postmeta>. Translating metadata often breaks serialized PHP arrays or JSON, which will crash your WordPress import.
Ignores Categories: It skips <category> tags. If you translate category names, WordPress won't be able to map them to your existing categories and will create duplicate, broken ones.
Preserves CDATA: The regex specifically looks for the <![CDATA[ wrappers and puts them back exactly as they were.
