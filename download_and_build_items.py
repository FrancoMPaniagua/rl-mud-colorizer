import urllib.request
import json
import re
import html
from pathlib import Path

BASE_DIR = Path(r"C:\Users\Compumar\mud_colorizer")
ITEMS_FILE = BASE_DIR / "items.json"

KNOWN_TAGS = {
    'BOLD', 'NOBOLD', 'RESET', 'RED', 'GREEN', 'YELLOW', 'BLUE',
    'MAGENTA', 'CYAN', 'WHITE', 'BLACK', 'ORANGE', 'FLASH'
}

# Standard Mudlet ANSI 16-color table
NORMAL_LPC_COLORS = {
    'RED': (178, 24, 24),       # dark red
    'GREEN': (0, 128, 0),       # dark green
    'YELLOW': (113, 113, 0),    # dark yellow / olive
    'BLUE': (0, 0, 128),        # dark blue
    'MAGENTA': (128, 0, 128),   # dark magenta
    'CYAN': (0, 128, 128),      # dark cyan / teal
    'WHITE': (192, 192, 192),   # standard silver/white
    'BLACK': (0, 0, 0),         # black
    'ORANGE': (255, 140, 0)     # orange
}

BOLD_LPC_COLORS = {
    'RED': (255, 0, 0),         # bright red
    'GREEN': (0, 255, 0),       # bright green
    'YELLOW': (255, 255, 0),    # bright yellow
    'BLUE': (0, 0, 255),        # bright blue
    'MAGENTA': (255, 0, 255),   # bright magenta
    'CYAN': (0, 255, 255),      # bright cyan / celeste
    'WHITE': (255, 255, 255),   # bright white
    'BLACK': (128, 128, 128),   # bright black / gray
    'ORANGE': (255, 165, 0)     # bright orange
}

# Words that should never be matched on their own as an item
GENERIC_STOPWORDS = {
    'de', 'del', 'la', 'el', 'los', 'las', 'un', 'una', 'unos', 'unas',
    'con', 'sin', 'por', 'para', 'en', 'sobre', 'y', 'o', 'al'
}

def parse_lpc_item(short_raw):
    """
    Parses LPC color string into (clean_name, rendered_spans)
    rendered_spans: list of ((r, g, b), text)
    """
    tokens = short_raw.split('%^')
    clean_parts = []
    
    current_color_tag = None
    is_bold = False
    
    spans = []
    for t in tokens:
        if not t:
            continue
        tag = t.upper()
        if tag in KNOWN_TAGS:
            if tag == 'BOLD':
                is_bold = True
            elif tag in ('NOBOLD', 'RESET'):
                is_bold = False
                if tag == 'RESET':
                    current_color_tag = None
            elif tag in NORMAL_LPC_COLORS:
                current_color_tag = tag
        else:
            # It is text
            clean_parts.append(t)
            if current_color_tag:
                rgb = BOLD_LPC_COLORS[current_color_tag] if is_bold else NORMAL_LPC_COLORS[current_color_tag]
            else:
                rgb = BOLD_LPC_COLORS['WHITE'] if is_bold else NORMAL_LPC_COLORS['WHITE']
            spans.append((rgb, t))
            
    # Merge consecutive spans with same color
    merged_spans = []
    for rgb, txt in spans:
        if merged_spans and merged_spans[-1][0] == rgb:
            merged_spans[-1] = (rgb, merged_spans[-1][1] + txt)
        else:
            merged_spans.append((rgb, txt))
            
    clean_name = re.sub(r'\s+', ' ', "".join(clean_parts)).strip()
    return clean_name, merged_spans

def strip_trailing_parenthesis_from_spans(spans):
    """Strips trailing ( Izquierdo ), ( Derecho ), etc. from end of spans to match clean item name."""
    full_text = "".join(txt for _, txt in spans)
    m = re.search(r'\s*\([^)]*\)\s*$', full_text)
    if not m:
        return spans
    cut_len = len(m.group(0))
    new_spans = []
    chars_to_remove = cut_len
    for rgb, txt in reversed(spans):
        if chars_to_remove >= len(txt):
            chars_to_remove -= len(txt)
            continue
        elif chars_to_remove > 0:
            new_spans.append((rgb, txt[:-chars_to_remove]))
            chars_to_remove = 0
        else:
            new_spans.append((rgb, txt))
    return list(reversed(new_spans))

def spans_to_html(spans):
    """Generates Mudlet span HTML for item spans."""
    out = []
    for (r, g, b), txt in spans:
        escaped = html.escape(txt)
        out.append(f'<span style="color: rgb({r},{g},{b}); background: rgb(0,0,0); ">{escaped}</span>')
    return "".join(out)

def download_all_items():
    print("Downloading all items from Armería API (https://armeria.reinosdeleyenda.es/api/items)...")
    all_raw_items = []
    offset = 0
    limit = 100
    
    while True:
        url = f"https://armeria.reinosdeleyenda.es/api/items?limit={limit}&offset={offset}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                items = data.get('data', [])
                if not items:
                    break
                all_raw_items.extend(items)
                total = data.get('meta', {}).get('total', 0)
                print(f"  Fetched {len(all_raw_items)} / {total} items...")
                if len(all_raw_items) >= total:
                    break
                offset += limit
        except Exception as e:
            print(f"Error fetching offset {offset}: {e}")
            break
            
    print(f"\nTotal items fetched from Armería: {len(all_raw_items)}")
    
    # Process items according to Option A:
    # 1. Must have explicit color codes (%^ in short)
    # 2. Must have at least 2 words (e.g. not a single generic word like "espada", "capa", "arco")
    # 3. Clean name length >= 5
    
    catalog = {}
    ignored_single_word = []
    ignored_uncolored = []
    
    for it in all_raw_items:
        short = it.get('short', '').strip()
        if not short:
            continue
            
        if '%^' not in short:
            ignored_uncolored.append(short)
            continue
            
        clean_name, spans = parse_lpc_item(short)
        
        # Clean name sanity checks
        # Remove parenthetical notes like ( Izquierdo ), ( Derecho ) from clean matching name
        base_match_name = re.sub(r'\s*\([^)]*\)\s*$', '', clean_name).strip()
        base_match_name = re.sub(r'^\s*dos\s+', '', base_match_name, flags=re.I).strip()
        base_match_name = re.sub(r'^\s*tres\s+', '', base_match_name, flags=re.I).strip()
        
        words = [w for w in base_match_name.split() if w.lower() not in GENERIC_STOPWORDS]
        if len(words) < 2:
            ignored_single_word.append(base_match_name)
            continue
            
        if len(base_match_name) < 5:
            continue
            
        clean_spans = strip_trailing_parenthesis_from_spans(spans)
        item_html = spans_to_html(clean_spans)
        
        # Save by key for exact lookup or regex
        key = base_match_name
        # Keep longest representation if duplicate
        if key not in catalog or len(catalog[key]['html']) < len(item_html):
            catalog[key] = {
                'id': it.get('id'),
                'tipo': it.get('tipo'),
                'raw_short': short,
                'name': base_match_name,
                'html': item_html
            }

    print(f"\nFiltered Unique Artifacts & Colored Items (Option A): {len(catalog)}")
    print(f"Ignored plain uncolored items: {len(ignored_uncolored)}")
    print(f"Ignored single-word generic colored items: {len(ignored_single_word)} (e.g.: {ignored_single_word[:10]})")
    
    # Save to items.json
    with open(ITEMS_FILE, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        
    print(f"Saved {len(catalog)} colored items to: {ITEMS_FILE}")

if __name__ == '__main__':
    download_all_items()
