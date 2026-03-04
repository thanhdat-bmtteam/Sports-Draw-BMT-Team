import os, re

sb_url = os.environ.get('SB_URL', '')
sb_key = os.environ.get('SB_KEY', '')

if not sb_url or not sb_key:
    print("ERROR: Missing SUPABASE_URL or SUPABASE_ANON_KEY secrets")
    exit(1)

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace obfuscated _cfg block with real values (split for mild obfuscation)
u1, u2, u3 = sb_url[:12], sb_url[12:28], sb_url[28:]
k = sb_key
k1, k2, k3, k4 = k[:20], k[20:55], k[55:100], k[100:]

new_cfg = (
    "// config\n"
    "const _cfg = {\n"
    f'  _a: "{u1}" + "{u2}" + "{u3}",\n'
    f'  _b: ["{k1}","{k2}","{k3}","{k4}"].join("")\n'
    "};\n"
    "const SUPABASE_URL = _cfg._a;\n"
    "const SUPABASE_ANON_KEY = _cfg._b;"
)

# Replace the existing _cfg block
pattern = r'// config \(split for obfuscation\)\nconst _cfg[\s\S]*?const SUPABASE_ANON_KEY = _cfg\._b;'
if re.search(pattern, content):
    content = re.sub(pattern, new_cfg, content)
    print("Secrets injected via regex OK")
else:
    # Fallback: direct string replace
    old = (
        "// config (split for obfuscation)\n"
        "const _cfg = {"
    )
    idx = content.find(old)
    if idx != -1:
        end = content.find("const SUPABASE_ANON_KEY = _cfg._b;", idx) + len("const SUPABASE_ANON_KEY = _cfg._b;")
        content = content[:idx] + new_cfg + content[end:]
        print("Secrets injected via index OK")
    else:
        print("WARNING: Could not find _cfg block, injecting directly")
        content = re.sub(r'const SUPABASE_URL\s*=\s*[^;]+;', f'const SUPABASE_URL = "{sb_url}";', content)
        content = re.sub(r'const SUPABASE_ANON_KEY\s*=\s*[^;]+;', f'const SUPABASE_ANON_KEY = "{sb_key}";', content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("inject_secrets.py completed successfully")
