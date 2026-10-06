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
            
        # Match rules in priority order
        for rule in self.compiled_rules:
            m = rule['_regex'].match(raw_text)
            if not m:
                continue
                
            rule_type = rule.get('type')
            
            # 1. Composite Prompt Handler
            if rule_type == 'composite_prompt_extended':
                return self._render_prompt_extended(m)
                
            # 2. Composite HP Delta Handler
            elif rule_type == 'composite_hp_delta':
                prefix, delta = m.groups()
                d_color = "#ff0000" if delta.startswith('-') else "#00ff00"
                return f'<span style="color: #008000;">{html.escape(prefix)}</span><span style="color: {d_color}; font-weight: bold;">{html.escape(delta)}</span>'
                
            # 3. Composite Movement Handler
            elif rule_type == 'composite_movement':
                return self._render_movement(m)
                
            # 4. Composite Tirada Handler
            elif rule_type == 'composite_tirada':
                return self._render_tirada(m)
                
            # 5. Composite Info Handler
            elif rule_type == 'composite_info':
                return self._render_info(m)
                
            # 6. Composite Spell Completion
            elif rule_type == 'composite_spell_completion':
                return self._render_spell_completion(m)
                
            # 7. Composite Magic Missiles
            elif rule_type == 'composite_magic_missiles':
                prompt_sym, prefix_sym, rest = m.groups()
                prompt_html = '<span style="color: #c0c0c0;">&gt; </span>' if prompt_sym else ''
                p_html = '<span style="color: #0000ff;">#</span> ' if prefix_sym else ''
                return f'{prompt_html}{p_html}<span style="color: #8cc4ff;">{html.escape(rest)}</span>'
                
            # 8. Composite Enemy Maneuver
            elif rule_type == 'composite_enemy_maneuver':
                return self._render_enemy_maneuver(m)

            # 9. Composite Player Combat
            elif rule_type == 'composite_player_combat':
                return self._render_player_combat(m)

            # 10. Composite Room Player
            elif rule_type == 'composite_room_player':
                return self._render_room_player(m)

            # 11. Composite Room NPC
            elif rule_type == 'composite_room_npc':
                return self._render_room_npc(m)

            # 12. Composite Follower Player
            elif rule_type == 'composite_follower_player':
                return self._render_follower_player(m)

            # 13. Composite Room Exits
            elif rule_type == 'composite_room_exits':
                res = self._render_room_exits(m)
                if res is not None:
                    return res

            # 14. Composite Room Title
            elif rule_type == 'composite_room_title':
                res = self._render_room_title(m)
                if res is not None:
                    return res
                
            # 15. Direct Regex Replacement
            elif 'replace' in rule:
                return self._apply_template(m, rule['replace'])
                
        # Default unstyled text
        escaped = html.escape(raw_text)
        return f'<span style="color: {self.theme.get("default_fg", "#c0c0c0")};">{escaped}</span>'

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
        if clean_title in self.room_colors:
            return self.room_colors[clean_title]
        if ':' in clean_title:
            zone = clean_title.split(':')[0].strip()
            if zone in self.room_colors:
                return self.room_colors[zone]
        if ' - ' in clean_title:
            zone = clean_title.split(' - ')[0].strip()
            if zone in self.room_colors:
                return self.room_colors[zone]
        return fallback

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
        escaped = html.escape(line)
        escaped = re.sub(r"(&#x27;[^&]+&#x27;|'[^']+')", r'<span style="color: #00ffff;">\1</span>', escaped)
        return f'<span style="color: #c0c0c0;">{escaped}</span>'

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
        return f'{prompt_html}<span style="color: #c0c0c0;">{colored_players} {html.escape(verb)}.</span>'

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
            
        escaped_body = html.escape(body)
        
        # Highlight damage ranges/brackets like (290-599) or [123]
        escaped_body = re.sub(
            r'(\()(\d+)(?:(-)(\d+))?(\))',
            r'<span style="color: #ffff00;">\1</span><span style="color: #ff0000; font-weight: bold;">\2</span><span style="color: #ffffff;">\3</span><span style="color: #ff0000; font-weight: bold;">\4</span><span style="color: #ffff00;">\5</span>',
            escaped_body
        )
        
        prefix_html = ""
        if prefix_sym:
            if '#' in prefix_sym:
                prefix_html = '<span style="color: #008000;">#</span> '
            elif '*' in prefix_sym:
                prefix_html = '<span style="color: #008000;">*</span> '
                
        return f'{prompt_html}{prefix_html}<span style="color: #00ff00;">{escaped_body}</span>'

    def _apply_template(self, m, template):
        res = template
        for i, val in enumerate(m.groups(), start=1):
            escaped_val = html.escape(val if val is not None else "")
            res = res.replace(f"${i}", escaped_val)
        return res

    def colorize_text(self, plain_text):
        trimmed = (plain_text or "").replace('\r\n', '\n').rstrip('\n')
        normalized = re.sub(r'\n{3,}', '\n\n', trimmed)
        lines = normalized.split('\n') if normalized else []
        rendered_lines = [self.colorize_line(line) for line in lines]
        content_html = "<br />".join(rendered_lines) + "<br />"
        
        return f'<font color="#cccccc" size="2"><div>{content_html}</div></font>'


if __name__ == '__main__':
    from build_rules import save_rules
    save_rules()
