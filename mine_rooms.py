import re
import html
import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(r"C:\Users\Compumar\mud_colorizer")
COLORED_DIR = BASE_DIR / "cache_colored"
ACC_DIR = BASE_DIR / "accessibility_logs"

tag_token_re = re.compile(r'(<[^>]+>|[^<]+)')
color_attr_re = re.compile(r'(?:color=[\'"]?([^\'"\s>]+)[\'"]?|color:\s*([^;\'"\s>]+))', re.I)
exit_regex = re.compile(r'[\[\(]([a-zA-ZáéíóúÁÉÍÓÚ,\|\s-]+)[\]\)]')
valid_dirs = {'n', 's', 'e', 'o', 'ne', 'no', 'se', 'so', 'ar', 'ab', 'arriba', 'abajo', 'norte', 'sur', 'este', 'oeste', 'sudoeste', 'sudeste', 'noreste', 'noroeste', 'entrar', 'salir', 'subir', 'bajar'}

def clean_room_name(raw_name):
    t = re.sub(r'<[^>]+>', '', raw_name)
    t = html.unescape(t)
    t = re.sub(r'.*extract from Reinos de Leyenda profile\s*', '', t, flags=re.I)
    t = re.sub(r'\[Viajar aqu[íi]\]\s*:\s*', '', t, flags=re.I)
    t = re.sub(r'^\s*[\d\w:.-]*\s*[>\]]\s*', '', t)
    t = re.sub(r'^\s*\d+\s*', '', t)
    t = re.sub(r'^[>\]]\s*', '', t)
    t = re.sub(r'\s*-\s*', ' - ', t)
    t = re.sub(r'\s*:\s*', ': ', t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()

def parse_styled_spans(chunk_html):
    color_stack = []
    spans = []
    for token in tag_token_re.findall(chunk_html):
        if token.startswith('<'):
            if token.startswith('</'):
                if color_stack:
                    color_stack.pop()
            elif token.startswith('<font') or token.startswith('<span'):
                is_bold = ('font-weight:bold' in token.lower() or 'font-weight: bold' in token.lower())
                m = color_attr_re.search(token)
                if m:
                    raw_c = (m.group(1) or m.group(2)).strip().lower()
                    if '192,192,192' in raw_c or raw_c in ['silver', '#c0c0c0']:
                        c = '#ffffff' if is_bold else '#c0c0c0'
                    elif '255,255,255' in raw_c or raw_c in ['white', '#ffffff']:
                        c = '#ffffff'
                    elif '255,255,0' in raw_c or raw_c in ['yellow', '#ffff00']:
                        c = '#ffff00'
                    elif '0,255,0' in raw_c or raw_c in ['lime', '#00ff00']:
                        c = '#00ff00'
                    elif '0,128,0' in raw_c or '0,136,0' in raw_c or raw_c in ['green', '#008000', 'darkgreen']:
                        c = '#008000'
                    elif '0,255,255' in raw_c or raw_c in ['cyan', '#00ffff']:
                        c = '#00ffff'
                    elif '0,128,128' in raw_c or '0,136,136' in raw_c or raw_c in ['teal', '#008080', '#008888']:
                        c = '#008080'
                    elif '128,128,0' in raw_c or '113,113,0' in raw_c or '136,136,0' in raw_c or raw_c in ['olive', '#808000', '#888800']:
                        c = '#808000'
                    elif '255,0,0' in raw_c or raw_c in ['red', '#ff0000']:
                        c = '#ff0000'
                    elif '128,0,0' in raw_c or raw_c in ['maroon', '#800000']:
                        c = '#800000'
                    elif '0,0,255' in raw_c or raw_c in ['blue', '#0000ff']:
                        c = '#0000ff'
                    elif '128,0,128' in raw_c or raw_c in ['purple', '#800080']:
                        c = '#800080'
                    else:
                        c = '#008000'
                    color_stack.append(c)
                else:
                    color_stack.append('#ffffff' if is_bold else (color_stack[-1] if color_stack else None))
        else:
            txt = html.unescape(token)
            if txt:
                spans.append((color_stack[-1] if color_stack else None, txt))
    return spans

def infer_fallback_color(title_lower):
    """Infers the best RL color for a room based on its zone and terrain keywords."""
    if title_lower.startswith("anduar:"):
        return "#ffffff"
    if "senda de las colinas de anduar" in title_lower or "campos de anduar" in title_lower:
        return "#ffffff"
    if "exterior de anduar" in title_lower or "ruinas de la muralla" in title_lower:
        return "#ffff00"
    if title_lower == "senda del alba":
        return "#ffffff"
    if title_lower == "campos de cultivo":
        return "#ffff00"
    if "golthur" in title_lower or "erial" in title_lower or "catacumbas" in title_lower or "cueva" in title_lower or "caverna" in title_lower or "subterr" in title_lower:
        return "#808000"
    if "aethia" in title_lower:
        return "#00ff00"
    if "pueblo de naduk" in title_lower or "naduk" in title_lower:
        return "#ffff00"
    if "catedral" in title_lower or "templo" in title_lower or "avenida" in title_lower or "calle" in title_lower or "plaza" in title_lower:
        return "#ffffff"
    if "camino" in title_lower or "senda" in title_lower or "puente" in title_lower or "carretera" in title_lower:
        return "#008080"
    if "lago" in title_lower or "río" in title_lower or "rio" in title_lower or "orilla" in title_lower or "mar" in title_lower or "playa" in title_lower:
        return "#0000ff"
    return "#008000"

def select_best_room_color(spans, full_title):
    title_lower = full_title.lower()
    if title_lower.startswith("anduar:"):
        return "#ffffff"
    if "senda de las colinas de anduar" in title_lower or "campos de anduar" in title_lower:
        return "#ffffff"
    if "exterior de anduar" in title_lower or "ruinas de la muralla" in title_lower:
        return "#ffff00"
    if title_lower == "senda del alba":
        return "#ffffff"
    if title_lower == "campos de cultivo":
        return "#ffff00"
        
    valid_colored_spans = []
    for col, txt in spans:
        letters = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜËë]', '', txt)
        if len(letters) >= 2 and col:
            valid_colored_spans.append((col, len(letters), txt))
            
    # Exclude default terminal silver/gray #c0c0c0, #cccccc
    vibrant = [s for s in valid_colored_spans if s[0] not in ['#c0c0c0', '#cccccc', '#d4d4d4', '#808080']]
    if vibrant:
        weights = Counter()
        for col, weight, txt in vibrant:
            weights[col] += weight
        return weights.most_common(1)[0][0]
        
    # If no vibrant color in spans, infer appropriate fallback
    return infer_fallback_color(title_lower)

def build_full_catalog():
    html_files = sorted(COLORED_DIR.glob("*.html"))
    room_colors = {}
    room_casing = {}

    for f in html_files:
        content = f.read_text(encoding='utf-8', errors='ignore')
        chunks = re.split(r'<br\s*/?>|\n', content)
        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk or ('[' not in chunk and '(' not in chunk):
                continue
            m_exit = exit_regex.search(chunk)
            if not m_exit:
                continue
            exits_raw = m_exit.group(1).strip()
            exit_tokens = [x.strip('|- ') for x in exits_raw.split(',')]
            if not any(t.lower() in valid_dirs for t in exit_tokens if t):
                continue

            before_exits_html = chunk[:m_exit.start()]
            full_title = clean_room_name(before_exits_html)

            if len(full_title) < 4 or len(full_title) > 90:
                continue
            if full_title.endswith(':') or '->' in full_title or '- >' in full_title or full_title.lower() == 'sl':
                continue
            if any(w in full_title.lower() for w in ['obtienes', 'puntos de', 'experiencia', 'daña', 'golpea', 'ataca', 'pvs:', 'hp:', 'dices en', 'bloqueo', 'salidas']):
                continue

            spans = parse_styled_spans(before_exits_html)
            room_color = select_best_room_color(spans, full_title)
            key = full_title.lower()
            if room_color:
                room_colors.setdefault(key, Counter())[room_color] += 1
                room_casing[key] = full_title

    # Add rooms from accessibility logs
    acc_files = sorted(ACC_DIR.glob("*.txt"))
    for f in acc_files:
        lines = f.read_text(encoding='utf-8', errors='replace').splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            m = exit_regex.search(line)
            if m and (line.endswith(']') or line.endswith('] ') or line.endswith(')') or line.endswith(') ')):
                exits_raw = m.group(1).strip()
                exit_tokens = [x.strip('|- ') for x in exits_raw.split(',')]
                if not any(t.lower() in valid_dirs for t in exit_tokens if t):
                    continue
                before_exits = line[:m.start()]
                full_title = clean_room_name(before_exits)
                if len(full_title) < 4 or len(full_title) > 90:
                    continue
                if full_title.endswith(':') or '->' in full_title or '- >' in full_title or full_title.lower() == 'sl':
                    continue
                if any(w in full_title.lower() for w in ['obtienes', 'puntos de', 'experiencia', 'daña', 'golpea', 'ataca', 'pvs:', 'hp:', 'dices en', 'bloqueo', 'salidas']):
                    continue
                key = full_title.lower()
                if key not in room_colors:
                    col = infer_fallback_color(key)
                    room_colors[key] = Counter({col: 1})
                    room_casing[key] = full_title

    catalog = {}
    for key, counter in room_colors.items():
        canonical_name = room_casing[key]
        best_color, count = counter.most_common(1)[0]
        catalog[canonical_name] = best_color

    # Add zone fallback definitions directly into catalog
    zone_defaults = {
        "anduar": "#ffffff",
        "exterior de anduar": "#ffff00",
        "ruinas de la muralla": "#ffff00",
        "ruinas de la muralla de anduar": "#ffff00",
        "ruinas de la muralla este de anduar": "#ffff00",
        "ruinas de la muralla norte de anduar": "#ffff00",
        "ruinas de la muralla oeste de anduar": "#ffff00",
        "ruinas de la muralla sur de anduar": "#ffff00",
        "takome": "#ffffff",
        "pueblo de naduk": "#ffff00",
        "aethia": "#00ff00",
        "grimoszk": "#00ff00",
        "galador": "#ffffff",
        "catedral de eralie": "#ffffff",
        "catedral de seldar": "#008000",
        "bosque de orgoth": "#008000",
        "golthur orod": "#808000",
        "erial de los condenados": "#808000",
    }
    for z, c in zone_defaults.items():
        if z not in [k.lower() for k in catalog]:
            catalog[z] = c

    # Save to rooms.json
    out_file = BASE_DIR / "rooms.json"
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"Total catalog size: {len(catalog)} rooms saved to {out_file}!")
    dist = Counter(catalog.values())
    print("\nColor distribution in new catalog:")
    for c, cnt in dist.most_common():
        print(f"  {c}: {cnt}")
        
    c0_count = sum(1 for v in catalog.values() if v in ['#c0c0c0', '#cccccc', '#d4d4d4'])
    print(f"\nRooms with #c0c0c0 in catalog: {c0_count} (Must be 0!)")

if __name__ == '__main__':
    build_full_catalog()
