import os
import hashlib
import requests
import re
from bs4 import BeautifulSoup

def generate_sri_hash(file_content):
    hash_object = hashlib.sha384(file_content)
    return 'sha384-' + hash_object.hexdigest()

def update_html_file(file_path, script_updates):
    with open(file_path, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')

    for script_tag in soup.find_all('script', {'src': True}):
        src = script_tag.get('src')
        if src and src.startswith('https') and src in script_updates:
            script_tag['integrity'] = script_updates[src]
            script_tag['crossorigin'] = 'anonymous'

    with open(file_path, 'w') as file:
        file.write(str(soup))

def process_html_file(file_path):
    script_updates = {}
    with open(file_path, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')

    for script_tag in soup.find_all('script', {'src': True}):
        if not script_tag.get('integrity'):
            print("working...")
            src = script_tag['src']
            if src.startswith('https'):
                try:
                    print(f"Downloading: {src}")
                    response = requests.get(src)
                    response.raise_for_status()
                    integrity_value = generate_sri_hash(response.content)
                    script_updates[src] = integrity_value
                except requests.RequestException as e:
                    print(f"Failed to download {src}: {e}")

    if script_updates:
        update_html_file(file_path, script_updates)

def traverse_directories(start_path):
    for root, dirs, files in os.walk(start_path):
        for file in files:
            if file.endswith('.html'):
                process_html_file(os.path.join(root, file))

start_directory = 'PATH/TO/TEMPLATES'
traverse_directories(start_directory)

