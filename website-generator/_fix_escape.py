with open('generator.py', encoding='utf-8') as f:
    content = f.read()

# Fix the bad \w \s escape sequences in the JS regex inside the Python string
bad = "    .replace(/[^\\w\\s-]/g,'').replace(/[\\s_-]+/g,'-') || 'your-shop';"
good = "    .replace(/[^\\\\w\\\\s-]/g,'').replace(/[\\\\s_-]+/g,'-') || 'your-shop';"

count = content.count(bad)
print(f'Found {count} occurrence(s) to fix')
content = content.replace(bad, good)

with open('generator.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done.')
