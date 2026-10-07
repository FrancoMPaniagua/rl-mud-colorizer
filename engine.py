"""
Reinos de Leyenda (RL) Colorizer Engine (v5)
Transforms plain-text MUD logs into clean, accurate HTML formatted with terminal colors.
"""

import re
import json
import html
from pathlib import Path

BASE_DIR = Path(r"C:\Users\Compumar\mud_colorizer")
RULES_FILE = BASE_DIR / "rules.json"

MUDLET_HEADER = (
    "<!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.01//EN' 'http://www.w3.org/TR/html4/strict.dtd'>\n"
    "<html>\n"
    " <head>\n"
    "  <meta http-equiv='content-type' content='text/html; charset=utf-8'>  <meta name='generator' content='Mudlet MUD Client version: 4.19.1'>\n"
    "  <title>Mudlet, main console extract from Reinos de Leyenda profile</title>\n"
    "  <style type='text/css'>\n"
    "   <!-- body { font-family: 'Bitstream Vera Sans Mono', 'Courier New', 'Monospace', 'Courier'; font-size: 100%; line-height: 1.125em; white-space: pre-wrap; color:rgb(255,255,255); background-color:rgb(0,0,0);}\n"
    "        span { white-space: pre-wrap; } -->\n"
    "  </style>\n"
    "  </head>\n"
    "  <body><div>"
)
MUDLET_FOOTER = " </div></body>\n</html>"
DEFAULT_MUDLET_STYLE = "color: rgb(192,192,192); background: rgb(0,0,0); "


def hex_to_rgb(hex_str):
    h = hex_str.strip().lstrip("#")
    if len(h) == 3:
        return int(h[0] * 2, 16), int(h[1] * 2, 16), int(h[2] * 2, 16)
    if len(h) == 6:
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return 192, 192, 192


def parse_color_to_rgb(val):
    if not val:
        return None
    val = val.strip()
    if val.startswith("#"):
        return hex_to_rgb(val)
    m = re.match(r"rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", val, re.IGNORECASE)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    named = {
        'white': (255, 255, 255),
        'silver': (192, 192, 192),
        'gray': (128, 128, 128),
        'green': (0, 128, 0),
        'red': (255, 0, 0),
        'yellow': (255, 255, 0),
        'blue': (8, 0, 255),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'black': (0, 0, 0),
    }
    return named.get(val.lower(), (192, 192, 192))


def style_to_mudlet(style_str):
    color_m = re.search(r'color:\s*([^;"]+)', style_str, re.IGNORECASE)
    bg_m = re.search(r'background(?:-color)?:\s*([^;"]+)', style_str, re.IGNORECASE)

    fg_rgb = (192, 192, 192)
    if color_m:
        parsed = parse_color_to_rgb(color_m.group(1))
        if parsed:
            fg_rgb = parsed

    bg_rgb = (0, 0, 0)
    if bg_m:
        parsed = parse_color_to_rgb(bg_m.group(1))
        if parsed:
            bg_rgb = parsed

    if "underline" in style_str.lower():
        return f"color: rgb({fg_rgb[0]},{fg_rgb[1]},{fg_rgb[2]}); background: rgb({bg_rgb[0]},{bg_rgb[1]},{bg_rgb[2]});  text-decoration: underline"
    return f"color: rgb({fg_rgb[0]},{fg_rgb[1]},{fg_rgb[2]}); background: rgb({bg_rgb[0]},{bg_rgb[1]},{bg_rgb[2]}); "


def normalize_line_to_mudlet(line_html):
    if not line_html:
        return ""

    converted = re.sub(r'style="([^"]*)"', lambda m: f'style="{style_to_mudlet(m.group(1))}"', line_html)

    tokens = []
    pos = 0
    span_pattern = re.compile(r'<span\s+style="([^"]*)">(.*?)</span>')
    for m in span_pattern.finditer(converted):
        start, end = m.span()
        if start > pos:
            bare = converted[pos:start]
            if bare:
                tokens.append((DEFAULT_MUDLET_STYLE, bare))
        tokens.append((m.group(1), m.group(2)))
        pos = end

    if pos < len(converted):
        bare = converted[pos:]
        if bare:
            tokens.append((DEFAULT_MUDLET_STYLE, bare))

    merged = []
    for s_attr, content in tokens:
        if not content:
            continue
        if merged and merged[-1][0] == s_attr:
            merged[-1] = (s_attr, merged[-1][1] + content)
        else:
            merged.append((s_attr, content))

    return "".join(f'<span style="{s}">{c}</span>' for s, c in merged)


class RLColorizer:
    def __init__(self, rules_path=RULES_FILE):
        with open(rules_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
            
        self.rules = sorted(self.config['rules'], key=lambda r: r.get('priority', 100))
        self.colors = self.config.get('colors', {})
        self.race_colors = self.config.get('race_colors', {})
        self.room_colors = self.config.get('room_colors', {})
        self.theme = self.config.get('theme', {})
        
        self.races_str = r'Hlag|Lag|Melf|Elf|S-e|Gob|Gno|Hum|Orc|S-o|Ena|Mdro|Drow|S-d|Hal|Hlf|Duer|Drg|Min|Mino|Gnl|Gnol|Kob|Org|Orgo|Drax|Ctd|Cent|Kuo|Ggt|S-g'
        self.race_tag_regex = re.compile(rf'\((?:{self.races_str})\)', re.IGNORECASE)
        self.player_entity_regex = re.compile(
            rf'((?:\b(?:un|una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez)\s+)?[*|\-~/]*\s*[A-Za-zÁÉÍÓÚáéíóúñÑ0-9\x27_-]+(?:\s+[|*\-~/]+)?\s*\((?:{self.races_str})\)(?:es)?(?:\s*[|*\-~/]+)?)',
            re.IGNORECASE
        )
        self.cardinal_regex = re.compile(r'\b(norte|sur|este|oeste|noreste|noroeste|sudeste|sudoeste|arriba|abajo|n|s|e|o|ne|no|se|so)\b', re.IGNORECASE)
        
        self.item_colors = self.config.get('item_colors', {})
        self.item_map = {k.lower(): v for k, v in self.item_colors.items()}
        if self.item_colors:
            sorted_keys = sorted(self.item_colors.keys(), key=len, reverse=True)
            self.item_regex = re.compile(
                r'(?<![a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ])(' + '|'.join(re.escape(k) for k in sorted_keys) + r')(?![a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ])',
                re.IGNORECASE
            )

        else:
            self.item_regex = None

        # Precompile regular expressions
        self.compiled_rules = []
        for r in self.rules:
            self.compiled_rules.append({
                **r,
                '_regex': re.compile(r['pattern'])
            })


    def colorize_line(self, line):
        raw_text = line.rstrip('\r\n')
        raw_text = raw_text.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')
        
        if not raw_text.strip():
            return ""
            
        line_html = None
        # Match rules in priority order
        for rule in self.compiled_rules:
            m = rule['_regex'].match(raw_text)
            if not m:
                continue
                
            rule_type = rule.get('type')
            
            # 1. Composite Prompt Handler
            if rule_type == 'composite_prompt_extended':
                line_html = self._render_prompt_extended(m)
                break
                
            # 2. Composite HP Delta Handler
            elif rule_type == 'composite_hp_delta':
                prefix, delta = m.groups()
                d_color = "#ff0000" if delta.startswith('-') else "#00ff00"
                line_html = f'<span style="color: #008000;">{html.escape(prefix)}</span><span style="color: {d_color}; font-weight: bold;">{html.escape(delta)}</span>'
                break
                
            # 3. Composite Movement Handler
            elif rule_type == 'composite_movement':
                line_html = self._render_movement(m)
                break
                
            # 4. Composite Tirada Handler
            elif rule_type == 'composite_tirada':
                line_html = self._render_tirada(m)
                break
                
            # 5. Composite Info Handler
            elif rule_type == 'composite_info':
                line_html = self._render_info(m)
                break
                
            # 6. Composite Spell Completion
            elif rule_type == 'composite_spell_completion':
                line_html = self._render_spell_completion(m)
                break
                
            # 7. Composite Magic Missiles
            elif rule_type == 'composite_magic_missiles':
                prompt_sym, prefix_sym, rest = m.groups()
                prompt_html = '<span style="color: #c0c0c0;">&gt; </span>' if prompt_sym else ''
                p_html = '<span style="color: #0000ff;">#</span> ' if prefix_sym else ''
                line_html = f'{prompt_html}{p_html}<span style="color: #8cc4ff;">{html.escape(rest)}</span>'
                break
                
            # 8. Composite Enemy Maneuver
            elif rule_type == 'composite_enemy_maneuver':
                line_html = self._render_enemy_maneuver(m)
                break

            # 9. Composite Player Combat
            elif rule_type == 'composite_player_combat':
                line_html = self._render_player_combat(m)
                break

            # 10. Composite Room Player
            elif rule_type == 'composite_room_player':
                line_html = self._render_room_player(m)
                break

            # 11. Composite Room NPC
            elif rule_type == 'composite_room_npc':
                line_html = self._render_room_npc(m)
                break

            # 12. Composite Follower Player
            elif rule_type == 'composite_follower_player':
                line_html = self._render_follower_player(m)
                break

            # 13. Composite Room Exits
            elif rule_type == 'composite_room_exits':
                res = self._render_room_exits(m)
                if res is not None:
                    line_html = res
                    break

            # 14. Composite Room Title
            elif rule_type == 'composite_room_title':
                res = self._render_room_title(m)
                if res is not None:
                    line_html = res
                    break
                
            # 15. Direct Regex Replacement
            elif 'replace' in rule:
                line_html = self._apply_template(m, rule['replace'])
                break
                
        if line_html is None:
            line_html = self._colorize_items_in_text(raw_text)
            
        return normalize_line_to_mudlet(line_html)

    def _colorize_items_in_text(self, raw_text):
        default_fg = self.theme.get("default_fg", "#c0c0c0")
        if not self.item_regex:
            return f'<span style="color: {default_fg};">{html.escape(raw_text)}</span>'

        last_idx = 0
        spans = []
        for m in self.item_regex.finditer(raw_text):
            start, end = m.span()
            if start > last_idx:
                non_item = raw_text[last_idx:start]
                spans.append(f'<span style="color: {default_fg};">{html.escape(non_item)}</span>')
            k = m.group(0).lower()
            spans.append(self.item_map.get(k, html.escape(m.group(0))))
            last_idx = end

        if last_idx == 0:
            return f'<span style="color: {default_fg};">{html.escape(raw_text)}</span>'

        if last_idx < len(raw_text):
            remaining = raw_text[last_idx:]
            spans.append(f'<span style="color: {default_fg};">{html.escape(remaining)}</span>')

        return "".join(spans)


    def _render_prompt_extended(self, m):
        pvs, pvs_delta, pe, pe_delta, extra = m.groups()
        out = []
        if pvs:
            out.append(f'<span style="color: #008000; font-weight: bold;">{html.escape(pvs)}</span>')
        
        if pvs_delta:
            color = "#ff0000" if pvs_delta.startswith('-') else ("#00ff00" if pvs_delta.startswith('+') else "#008000")
            prefix_space = ' ' if pvs and not pvs.endswith(' ') else ''
            out.append(f'{prefix_space}<span style="color: #008000;">(</span><span style="color: {color}; font-weight: bold;">{html.escape(pvs_delta)}</span><span style="color: #008000;">)</span>')
            
        if pe:
            out.append(f'<span style="color: #008000;">{html.escape(pe)}</span>')
            
        if pe_delta:
            color = "#ff0000" if pe_delta.startswith('-') else ("#00ff00" if pe_delta.startswith('+') else "#008000")
            prefix_space = ' ' if pe and not pe.endswith(' ') else ''
            out.append(f'{prefix_space}<span style="color: #008000;">(</span><span style="color: {color}; font-weight: bold;">{html.escape(pe_delta)}</span><span style="color: #008000;">)</span>')
            
        if extra:
            out.append(f'<span style="color: #008000;">{html.escape(extra)}</span>')
            
        return "".join(out)

    def get_race_color(self, text):
        if not text:
            return "#ffff00"
        m = self.race_tag_regex.search(text)
        if m:
            raw_tag = m.group(0)[1:-1].lower()
            return self.race_colors.get(raw_tag, "#ffff00")
        return "#ffff00"

    def _colorize_player_entities(self, text):
        parts = []
        last_end = 0
        for m in self.player_entity_regex.finditer(text):
            start, end = m.span(1)
            if start > last_end:
                parts.append(html.escape(text[last_end:start]))
            raw_matched = m.group(1)
            token = raw_matched.strip()
            leading_ws = raw_matched[:len(raw_matched) - len(raw_matched.lstrip())]
            trailing_ws = raw_matched[len(raw_matched.rstrip()):]
            color = self.get_race_color(token)
            parts.append(html.escape(leading_ws) + f'<span style="color: {color};">{html.escape(token)}</span>' + html.escape(trailing_ws))
            last_end = end
        if last_end < len(text):
            parts.append(html.escape(text[last_end:]))
        return "".join(parts)

    def _render_movement(self, m):
        prompt_sym, actor, verb, dest = m.groups()
        prompt_html = '<span style="color: #c0c0c0;">&gt; </span>' if prompt_sym else ''
        tag_m = self.race_tag_regex.search(actor)
        if tag_m:
            actor_color = self.get_race_color(actor)
            actor_html = f'<span style="color: {actor_color}; font-weight: bold;">{html.escape(actor)}</span>'
        else:
            actor_html = f'<span style="color: #c0c0c0;">{html.escape(actor)}</span>'
        verb_html = f'<span style="color: #ffffff;">{html.escape(verb)}</span>'
        dest_html = f'<span style="color: #c0c0c0;">{html.escape(dest)}.</span>'
        return f'{prompt_html}{actor_html} {verb_html} {dest_html}'

    def _render_follower_player(self, m):
        prompt_sym, actor, verb = m.groups()
        prompt_html = '<span style="color: #c0c0c0;">&gt; </span>' if prompt_sym else ''
        actor_color = self.get_race_color(actor)
        return f'{prompt_html}<span style="color: {actor_color}; font-weight: bold;">{html.escape(actor)}</span> <span style="color: #c0c0c0;">{html.escape(verb)}.</span>'

    def get_room_color(self, room_title, fallback=None):
        if not room_title:
            return fallback or "#008000"
        clean_title = re.sub(r'\s+', ' ', re.sub(r'\s*-\s*', ' - ', room_title)).strip().lower()
        clean_title = re.sub(r'\s*:\s*', ': ', clean_title)
        
        col = self.room_colors.get(clean_title)
        if col and col.lower() not in ['#c0c0c0', '#cccccc', '#d4d4d4', 'silver']:
            return col
            
        if ':' in clean_title:
            zone = clean_title.split(':')[0].strip()
            col = self.room_colors.get(zone)
            if col and col.lower() not in ['#c0c0c0', '#cccccc', '#d4d4d4', 'silver']:
                return col
                
        if ' - ' in clean_title:
            zone = clean_title.split(' - ')[0].strip()
            col = self.room_colors.get(zone)
            if col and col.lower() not in ['#c0c0c0', '#cccccc', '#d4d4d4', 'silver']:
                return col
                
        return fallback or "#008000"


    def _render_room_exits(self, m):
        prompt_sym, room_title, exits = m.groups()
        prompt_html = '<span style="color: #c0c0c0;">&gt; </span>' if prompt_sym else ''
        color = self.get_room_color(room_title, "#008000")
        return f'{prompt_html}<span style="color: {color}; font-weight: bold;">{html.escape(room_title)}</span> <span style="color: #00ffff;">{html.escape(exits)}</span>'

    def _render_room_title(self, m):
        prompt_sym, room_title = m.groups()
        color = self.get_room_color(room_title, None)
        if not color:
            return None
        prompt_html = '<span style="color: #c0c0c0;">&gt; </span>' if prompt_sym else ''
        return f'{prompt_html}<span style="color: {color}; font-weight: bold;">{html.escape(room_title)}</span>'

    def _render_tirada(self, m):
        b1, tag, body, result, b2 = m.groups()
        res_color = "#00ff00" if "Éxito" in result or "Exito" in result else "#ff0000"
        return (
            f'<span style="color: #c0c0c0;">[</span>'
            f'<span style="color: #ffff00; font-weight: bold;">{tag}</span>'
            f'<span style="color: #c0c0c0;">{html.escape(body)}</span>'
            f'<span style="color: {res_color}; font-weight: bold;">{result}</span>'
            f'<span style="color: #c0c0c0;">{b2}</span>'
        )

    def _render_info(self, m):
        b1, tag, sep, rest = m.groups()
        tag_colors = {
            'INFO': '#ffff00',
            'AYUDA': '#ff00ff',
            'ADVERTENCIA': '#ffaa00',
            'ERROR': '#ff0000'
        }
        tcolor = tag_colors.get(tag, '#ffff00')
        return (
            f'<span style="color: #c0c0c0;">[</span>'
            f'<span style="color: {tcolor}; font-weight: bold;">{tag}</span>'
            f'<span style="color: #c0c0c0;">{sep}{html.escape(rest)}</span>'
        )

    def _render_spell_completion(self, m):
        line = m.group(0)
        parts = []
        pos = 0
        for q_m in re.finditer(r"'[^']+'", line):
            start, end = q_m.span()
            if start > pos:
                parts.append(f'<span style="color: #c0c0c0;">{html.escape(line[pos:start])}</span>')
            parts.append(f'<span style="color: #00ffff;">{html.escape(q_m.group(0))}</span>')
            pos = end
        if pos < len(line):
            parts.append(f'<span style="color: #c0c0c0;">{html.escape(line[pos:])}</span>')
        return "".join(parts)

    def _render_enemy_maneuver(self, m):
        prompt_sym, alert_sym, actor, verb, rest = m.groups()
        prompt_html = '<span style="color: #c0c0c0;">&gt; </span>' if prompt_sym else ''
        alert_html = '<span style="color: #ff0000; font-weight: bold;">!</span> ' if alert_sym else ''
        tag_m = self.race_tag_regex.search(actor)
        if tag_m:
            actor_color = self.get_race_color(actor)
        else:
            actor_color = "#ff4444"
        actor_html = f'<span style="color: {actor_color}; font-weight: bold;">{html.escape(actor)}</span>'
        action_html = f'<span style="color: #ff8080;">{html.escape(verb + (rest or ""))}</span>'
        return f'{prompt_html}{alert_html}{actor_html} {action_html}'

    def _render_room_player(self, m):
        prompt_sym, players, verb = m.groups()
        prompt_html = '<span style="color: #c0c0c0;">&gt; </span>' if prompt_sym else ''
        colored_players = self._colorize_player_entities(players)
        return f'{prompt_html}{colored_players}<span style="color: #c0c0c0;"> {html.escape(verb)}.</span>'

    def _render_room_npc(self, m):
        prompt_sym, npc, verb = m.groups()
        prompt_html = '<span style="color: #c0c0c0;">&gt; </span>' if prompt_sym else ''
        return f'{prompt_html}<span style="color: #c0c0c0;">{html.escape(npc)} {html.escape(verb)}.</span>'

    def _render_player_combat(self, m):
        prompt_sym, hash_prefix, hash_body, star_prefix, verb, rest = m.groups()
        prompt_html = '<span style="color: #c0c0c0;">&gt; </span>' if prompt_sym else ''
        
        if hash_prefix:
            prefix_sym = hash_prefix
            body = hash_body or ""
        else:
            prefix_sym = star_prefix or ""
            body = (verb or "") + (rest or "")
            
        full_line = prefix_sym + body
        
        # Check if dodge, parry or miss
        if any(w in full_line.lower() for w in ['esquiva tu ataque', 'fallas tu ataque', 'bloquea tu', 'consigue parar', 'consigue esquivar']):
            return f'{prompt_html}<span style="color: #808080;">{html.escape(full_line)}</span>'
            
        # Highlight damage ranges/brackets like (290-599) or [123]
        parts = []
        pos = 0
        bracket_re = re.compile(r'(\()(\d+)(?:(-)(\d+))?(\))')
        for b_m in bracket_re.finditer(body):
            start, end = b_m.span()
            if start > pos:
                parts.append(f'<span style="color: #00ff00;">{html.escape(body[pos:start])}</span>')
            b1, d1, sep, d2, b2 = b_m.groups()
            parts.append(f'<span style="color: #ffff00;">{b1}</span><span style="color: #ff0000; font-weight: bold;">{d1}</span>')
            if sep:
                parts.append(f'<span style="color: #ffffff;">{sep}</span><span style="color: #ff0000; font-weight: bold;">{d2}</span>')
            parts.append(f'<span style="color: #ffff00;">{b2}</span>')
            pos = end
        if pos < len(body):
            parts.append(f'<span style="color: #00ff00;">{html.escape(body[pos:])}</span>')
            
        combat_html = "".join(parts)
        
        prefix_html = ""
        if prefix_sym:
            if '#' in prefix_sym:
                prefix_html = '<span style="color: #008000;">#</span> '
            elif '*' in prefix_sym:
                prefix_html = '<span style="color: #008000;">*</span> '
                
        return f'{prompt_html}{prefix_html}{combat_html}'

    def _apply_template(self, m, template):
        res = template
        for i, val in enumerate(m.groups(), start=1):
            escaped_val = html.escape(val if val is not None else "")
            res = res.replace(f"${i}", escaped_val)
        return res

    def colorize_text(self, plain_text):
        trimmed = (plain_text or "").replace('\r\n', '\n').rstrip('\n')
        normalized = re.sub(r'\n{3,}', '\n\n', trimmed)
        if not normalized:
            return MUDLET_HEADER + " </div></body>\n</html>"

        lines = normalized.split('\n')
        rendered_lines = [self.colorize_line(line) for line in lines]
        body_content = "\n".join(rendered_lines)

        return f"{MUDLET_HEADER}{body_content}\n </div></body>\n</html>"


if __name__ == '__main__':
    from build_rules import save_rules
    save_rules()
