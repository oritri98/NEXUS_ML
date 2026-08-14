import re

html_file = 'index.html'

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()


with open(html_file, 'w', encoding='utf-8') as f:
    f.write(new_content)
