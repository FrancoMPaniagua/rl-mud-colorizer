import urllib.request
import json
import re
import html
from pathlib import Path
from collections import Counter

BASE_DIR = Path(r"C:\Users\Compumar\mud_colorizer")
ITEMS_FILE = BASE_DIR / "items.json"

KNOWN_TAGS = {
    'BOLD', 'NOBOLD', 'RESET', 'RED', 'GREEN', 'YELLOW', 'BLUE',
    'MAGENTA', 'CYAN', 'WHITE', 'BLACK', 'ORANGE', 'FLASH'
}

LPC_COLOR_MAP = {
    'RED': '#ff0000',
    'GREEN': '#008000',
    'YELLOW': '#ffff00',
    'BLUE': '#0000ff',
    'MAGENTA': '#ff00ff',
    'CYAN': '#00ffff',
    'WHITE': '#ffffff',
    'BLACK': '#808080',
    'ORANGE': '#ff8800'
}

# Words that should never be matched on their own as an item
GENERIC_STOPWORDS = {
    'de', 'del', 'la', 'el', 'los', 'las', 'un', 'una', 'unos', 'unas',
    'con', 'sin', 'por', 'para', 'en', 'sobre', 'y', 'o', 'al'
}

def parse_lpc_item(short_raw):
    """
    Parses LPC color string into (clean_name, rendered_spans)
    rendered_spans: list of (color, is_bold, text)
    """
    tokens = short_raw.split('%^')
    clean_parts = []
    
    current_color = None
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
                    current_color = None
            elif tag in LPC_COLOR_MAP:
                current_color = LPC_COLOR_MAP[tag]
        else:
            # It is text
            # If bold and green/white, in terminal bold green is bright green
            eff_color = current_color
            if not eff_color:
                eff_color = '#ffffff' if is_bold else '#c0c0c0'
            elif eff_color == '#008000' and is_bold:
                eff_color = '#00ff00'
            elif eff_color == '#ff0000' and is_bold:
                eff_color = '#ff4444'
                
            clean_parts.append(t)
            spans.append((eff_color, is_bold, t))
            
    # Merge consecutive spans with same styling
    merged_spans = []
    for col, bold, txt in spans:
        if merged_spans and merged_spans[-1][0] == col and merged_spans[-1][1] == bold:
            merged_spans[-1] = (col, bold, merged_spans[-1][2] + txt)
        else:
            merged_spans.append((col, bold, txt))
            
    clean_name = re.sub(r'\s+', ' ', "".join(clean_parts)).strip()
    return clean_name, merged_spans

def spans_to_html(spans):
    """Generates Mudlet span HTML for item spans."""
    out = []
    for col, bold, txt in spans:
        escaped = html.escape(txt)
        # Parse hex to rgb
        h = col.lstrip('#')
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        bold_style = "font-weight: bold; " if bold else ""
        out.append(f'<span style="color: rgb({r},{g},{b}); background: rgb(0,0,0); {bold_style}">{escaped}</span>')
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
    # 3. Clean name length >= 6
    
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
            
        item_html = spans_to_html(spans)
        
        # Save by lowercase key for exact lookup or regex
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
    
    print("\nSample processed items (first 20):")
    for k in list(catalog.keys())[:20]:
        print(f"  {k:<45} -> {catalog[k]['html'][:80]}...")

if __name__ == '__main__':
    download_all_items()
