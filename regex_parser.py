import re
import requests
import hashlib
import os

def generate_sri_hash(file_content):
    hash_object = hashlib.sha384(file_content)
    return 'sha384-' + hash_object.hexdigest()

def process_file(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()

    # Simple regex to find all script tags with an https src attribute
    script_regex = re.compile(r'<script[^>]+src="https[^>]+>', re.IGNORECASE)

    def add_integrity(match):
        script_tag = match.group(0)
        # Check if 'integrity' is already present in the script tag
        if 'integrity' not in script_tag:
            src = re.search(r'src="([^"]+)"', script_tag)
            if src:
                try:
                    response = requests.get(src.group(1))
                    response.raise_for_status()
                    integrity_hash = generate_sri_hash(response.content)
                    return script_tag[:-1] + f' integrity="{integrity_hash}" crossorigin="anonymous">'
                except requests.RequestException as e:
                    print(f"Failed to download {src.group(1)}: {e}")
        return script_tag

    updated_content = script_regex.sub(add_integrity, file_content)

    with open(file_path, 'w') as file:
        file.write(updated_content)

def traverse_directories(start_path):
    for root, dirs, files in os.walk(start_path):
        for file in files:
            if file.endswith('.html'):
                process_file(os.path.join(root, file))


start_directory = 'PATH/TO/TEMPLATES'
traverse_directories(start_directory)

