/**
 * Reinos de Leyenda (RL) Colorizer Engine - JavaScript Edition (v5)
 * Mirrors engine.py with 100% fidelity.
 */

function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#x27;');
}

class RLColorizerJS {
    constructor(config) {
        this.config = config || (typeof window !== 'undefined' ? window.COLORIZER_RULES : null);
        if (!this.config) {
            throw new Error("No configuration rules provided for RLColorizerJS.");
        }
        this.theme = this.config.theme || {
            bg: "#000000",
            default_fg: "#c0c0c0",
            font_family: "'Bitstream Vera Sans Mono', 'Courier New', monospace"
        };
        this.colors = this.config.colors || {};
        this.raceColors = this.config.race_colors || {};
        this.roomColors = this.config.room_colors || {};
        
        this.racesStr = "Hlag|Lag|Melf|Elf|S-e|Gob|Gno|Hum|Orc|S-o|Ena|Mdro|Drow|S-d|Hal|Hlf|Duer|Drg|Min|Mino|Gnl|Gnol|Kob|Org|Orgo|Drax|Ctd|Cent|Kuo|Ggt|S-g";
        this.raceTagRegex = new RegExp(`\\((?:${this.racesStr})\\)`, 'i');
        this.playerEntityPattern = `((?:\\b(?:un|una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez)\\s+)?[*|\\-~/]*\\s*[A-Za-zÁÉÍÓÚáéíóúñÑ0-9\\x27_-]+(?:\\s+[|*\\-~/]+)?\\s*\\((?:${this.racesStr})\\)(?:es)?(?:\\s*[|*\\-~/]+)?)`;
        this.cardinalRegex = /\b(norte|sur|este|oeste|noreste|noroeste|sudeste|sudoeste|arriba|abajo|n|s|e|o|ne|no|se|so)\b/i;
        
        const sortedRules = [...this.config.rules].sort((a, b) => (a.priority || 100) - (b.priority || 100));
        this.compiledRules = sortedRules.map(r => ({
            ...r,
            _regex: new RegExp(r.pattern)
        }));
    }

    colorizeLine(line) {
        let rawText = line.replace(/\r?\n$/, '');
        rawText = rawText.replace(/&gt;/g, '>').replace(/&lt;/g, '<').replace(/&amp;/g, '&');

        if (!rawText.trim()) {
            return "";
        }

        for (const rule of this.compiledRules) {
            const m = rule._regex.exec(rawText);
            if (!m) continue;

            const type = rule.type;

            // 1. Composite Prompt Handler
            if (type === 'composite_prompt_extended') {
                return this._renderPromptExtended(m);
            }
            // 2. Composite HP Delta Handler
            else if (type === 'composite_hp_delta') {
                const prefix = m[1];
                const delta = m[2];
                const dColor = delta.startsWith('-') ? "#ff0000" : "#00ff00";
                return `<span style="color: #008000;">${escapeHtml(prefix)}</span><span style="color: ${dColor}; font-weight: bold;">${escapeHtml(delta)}</span>`;
            }
            // 3. Composite Movement Handler
            else if (type === 'composite_movement') {
                return this._renderMovement(m);
            }
            // 4. Composite Tirada Handler
            else if (type === 'composite_tirada') {
                return this._renderTirada(m);
            }
            // 5. Composite Info Handler
            else if (type === 'composite_info') {
                return this._renderInfo(m);
            }
            // 6. Composite Spell Completion
            else if (type === 'composite_spell_completion') {
                return this._renderSpellCompletion(m);
            }
            // 7. Composite Magic Missiles
            else if (type === 'composite_magic_missiles') {
                const promptSym = m[1];
                const prefixSym = m[2];
                const rest = m[3];
                const promptHtml = promptSym ? '<span style="color: #c0c0c0;">&gt; </span>' : '';
                const pHtml = prefixSym ? '<span style="color: #0000ff;">#</span> ' : '';
                return `${promptHtml}${pHtml}<span style="color: #8cc4ff;">${escapeHtml(rest)}</span>`;
            }
            // 8. Composite Enemy Maneuver
            else if (type === 'composite_enemy_maneuver') {
                return this._renderEnemyManeuver(m);
            }
            // 9. Composite Player Combat
            else if (type === 'composite_player_combat') {
                return this._renderPlayerCombat(m);
            }
            // 10. Composite Room Player
            else if (type === 'composite_room_player') {
                return this._renderRoomPlayer(m);
            }
            // 11. Composite Room NPC
            else if (type === 'composite_room_npc') {
                return this._renderRoomNpc(m);
            }
            // 12. Composite Follower Player
            else if (type === 'composite_follower_player') {
                return this._renderFollowerPlayer(m);
            }
            // 13. Composite Room Exits
            else if (type === 'composite_room_exits') {
                const res = this._renderRoomExits(m);
                if (res !== null) return res;
            }
            // 14. Composite Room Title
            else if (type === 'composite_room_title') {
                const res = this._renderRoomTitle(m);
                if (res !== null) return res;
            }
            // 15. Direct Regex Replacement
            else if (rule.replace) {
                return this._applyTemplate(m, rule.replace);
            }
        }

        // Default silver fallback
        return `<span style="color: ${this.theme.default_fg || '#c0c0c0'};">${escapeHtml(rawText)}</span>`;
    }

    _renderPromptExtended(m) {
        const pvs = m[1];
        const pvsDelta = m[2];
        const pe = m[3];
        const peDelta = m[4];
        const extra = m[5];

        let out = '';
        if (pvs) {
            out += `<span style="color: #008000; font-weight: bold;">${escapeHtml(pvs)}</span>`;
        }

        if (pvsDelta) {
            const color = pvsDelta.startsWith('-') ? "#ff0000" : (pvsDelta.startsWith('+') ? "#00ff00" : "#008000");
            const prefixSpace = (pvs && !pvs.endsWith(' ')) ? ' ' : '';
            out += `${prefixSpace}<span style="color: #008000;">(</span><span style="color: ${color}; font-weight: bold;">${escapeHtml(pvsDelta)}</span><span style="color: #008000;">)</span>`;
        }

        if (pe) {
            out += `<span style="color: #008000;">${escapeHtml(pe)}</span>`;
        }

        if (peDelta) {
            const color = peDelta.startsWith('-') ? "#ff0000" : (peDelta.startsWith('+') ? "#00ff00" : "#008000");
            const prefixSpace = (pe && !pe.endsWith(' ')) ? ' ' : '';
            out += `${prefixSpace}<span style="color: #008000;">(</span><span style="color: ${color}; font-weight: bold;">${escapeHtml(peDelta)}</span><span style="color: #008000;">)</span>`;
        }

        if (extra) {
            out += `<span style="color: #008000;">${escapeHtml(extra)}</span>`;
        }

        return out;
    }

    getRaceColor(text) {
        if (!text) return "#ffff00";
        const m = this.raceTagRegex.exec(text);
        if (m) {
            const rawTag = m[0].slice(1, -1).toLowerCase();
            return this.raceColors[rawTag] || "#ffff00";
        }
        return "#ffff00";
    }

    _colorizePlayerEntities(text) {
        const regex = new RegExp(this.playerEntityPattern, 'gi');
        let parts = [];
        let lastEnd = 0;
        let match;
        while ((match = regex.exec(text)) !== null) {
            const start = match.index;
            const end = regex.lastIndex;
            if (start > lastEnd) {
                parts.push(escapeHtml(text.slice(lastEnd, start)));
            }
            const rawMatched = match[1];
            const token = rawMatched.trim();
            const leadingWs = rawMatched.slice(0, rawMatched.length - rawMatched.trimStart().length);
            const trailingWs = rawMatched.slice(rawMatched.trimEnd().length);
            const color = this.getRaceColor(token);
            parts.push(escapeHtml(leadingWs) + `<span style="color: ${color};">${escapeHtml(token)}</span>` + escapeHtml(trailingWs));
            lastEnd = end;
            if (regex.lastIndex === match.index) regex.lastIndex++;
        }
        if (lastEnd < text.length) {
            parts.push(escapeHtml(text.slice(lastEnd)));
        }
        return parts.join('');
    }

    _renderMovement(m) {
        const promptSym = m[1];
        const actor = m[2];
        const verb = m[3];
        const dest = m[4];
        const promptHtml = promptSym ? '<span style="color: #c0c0c0;">&gt; </span>' : '';
        const tagM = this.raceTagRegex.exec(actor);
        const actorColor = tagM ? this.getRaceColor(actor) : "#c0c0c0";
        const actorHtml = tagM
            ? `<span style="color: ${actorColor}; font-weight: bold;">${escapeHtml(actor)}</span>`
            : `<span style="color: #c0c0c0;">${escapeHtml(actor)}</span>`;
        const verbHtml = `<span style="color: #ffffff;">${escapeHtml(verb)}</span>`;
        const destHtml = `<span style="color: #c0c0c0;">${escapeHtml(dest)}.</span>`;
        return `${promptHtml}${actorHtml} ${verbHtml} ${destHtml}`;
    }

    _renderFollowerPlayer(m) {
        const promptSym = m[1];
        const actor = m[2];
        const verb = m[3];
        const promptHtml = promptSym ? '<span style="color: #c0c0c0;">&gt; </span>' : '';
        const actorColor = this.getRaceColor(actor);
        return `${promptHtml}<span style="color: ${actorColor}; font-weight: bold;">${escapeHtml(actor)}</span> <span style="color: #c0c0c0;">${escapeHtml(verb)}.</span>`;
    }

    getRoomColor(roomTitle, fallback = null) {
        if (!roomTitle) return fallback || "#008000";
        let cleanTitle = roomTitle.replace(/\s*-\s*/g, ' - ').replace(/\s*:\s*/g, ': ').replace(/\s+/g, ' ').trim().toLowerCase();
        if (this.roomColors[cleanTitle]) {
            return this.roomColors[cleanTitle];
        }
        if (cleanTitle.includes(':')) {
            const zone = cleanTitle.split(':')[0].trim();
            if (this.roomColors[zone]) return this.roomColors[zone];
        }
        if (cleanTitle.includes(' - ')) {
            const zone = cleanTitle.split(' - ')[0].trim();
            if (this.roomColors[zone]) return this.roomColors[zone];
        }
        return fallback;
    }

    _renderRoomExits(m) {
        const promptSym = m[1];
        const roomTitle = m[2];
        const exits = m[3];
        const promptHtml = promptSym ? '<span style="color: #c0c0c0;">&gt; </span>' : '';
        const color = this.getRoomColor(roomTitle, "#008000");
        return `${promptHtml}<span style="color: ${color}; font-weight: bold;">${escapeHtml(roomTitle)}</span> <span style="color: #00ffff;">${escapeHtml(exits)}</span>`;
    }

    _renderRoomTitle(m) {
        const promptSym = m[1];
        const roomTitle = m[2];
        const color = this.getRoomColor(roomTitle, null);
        if (!color) return null;
        const promptHtml = promptSym ? '<span style="color: #c0c0c0;">&gt; </span>' : '';
        return `${promptHtml}<span style="color: ${color}; font-weight: bold;">${escapeHtml(roomTitle)}</span>`;
    }

    _renderTirada(m) {
        const b1 = m[1];
        const tag = m[2];
        const body = m[3];
        const result = m[4];
        const b2 = m[5];
        const resColor = (result.includes('Éxito') || result.includes('Exito')) ? "#00ff00" : "#ff0000";

        return (
            `<span style="color: #c0c0c0;">[</span>` +
            `<span style="color: #ffff00; font-weight: bold;">${escapeHtml(tag)}</span>` +
            `<span style="color: #c0c0c0;">${escapeHtml(body)}</span>` +
            `<span style="color: ${resColor}; font-weight: bold;">${escapeHtml(result)}</span>` +
            `<span style="color: #c0c0c0;">${escapeHtml(b2)}</span>`
        );
    }

    _renderInfo(m) {
        const b1 = m[1];
        const tag = m[2];
        const sep = m[3];
        const rest = m[4];
        const tagColors = {
            'INFO': '#ffff00',
            'AYUDA': '#ff00ff',
            'ADVERTENCIA': '#ffaa00',
            'ERROR': '#ff0000'
        };
        const tcolor = tagColors[tag] || '#ffff00';

        return (
            `<span style="color: #c0c0c0;">[</span>` +
            `<span style="color: ${tcolor}; font-weight: bold;">${escapeHtml(tag)}</span>` +
            `<span style="color: #c0c0c0;">${escapeHtml(sep)}${escapeHtml(rest)}</span>`
        );
    }

    _renderSpellCompletion(m) {
        const line = m[0];
        let escaped = escapeHtml(line);
        escaped = escaped.replace(/(&#x27;[^&]+&#x27;|'[^']+')/g, '<span style="color: #00ffff;">$1</span>');
        return `<span style="color: #c0c0c0;">${escaped}</span>`;
    }

    _renderEnemyManeuver(m) {
        const promptSym = m[1];
        const alertSym = m[2];
        const actor = m[3];
        const verb = m[4];
        const rest = m[5] || "";
        const promptHtml = promptSym ? '<span style="color: #c0c0c0;">&gt; </span>' : '';
        const alertHtml = alertSym ? '<span style="color: #ff0000; font-weight: bold;">!</span> ' : '';
        const tagM = this.raceTagRegex.exec(actor);
        const actorColor = tagM ? this.getRaceColor(actor) : "#ff4444";
        const actorHtml = `<span style="color: ${actorColor}; font-weight: bold;">${escapeHtml(actor)}</span>`;
        const actionHtml = `<span style="color: #ff8080;">${escapeHtml(verb + rest)}</span>`;
        return `${promptHtml}${alertHtml}${actorHtml} ${actionHtml}`;
    }

    _renderRoomPlayer(m) {
        const promptSym = m[1];
        const players = m[2];
        const verb = m[3];
        const promptHtml = promptSym ? '<span style="color: #c0c0c0;">&gt; </span>' : '';
        const coloredPlayers = this._colorizePlayerEntities(players);
        return `${promptHtml}<span style="color: #c0c0c0;">${coloredPlayers} ${escapeHtml(verb)}.</span>`;
    }

    _renderRoomNpc(m) {
        const promptSym = m[1];
        const npc = m[2];
        const verb = m[3];
        const promptHtml = promptSym ? '<span style="color: #c0c0c0;">&gt; </span>' : '';
        return `${promptHtml}<span style="color: #c0c0c0;">${escapeHtml(npc)} ${escapeHtml(verb)}.</span>`;
    }

    _renderPlayerCombat(m) {
        const promptSym = m[1];
        const hashPrefix = m[2];
        const hashBody = m[3];
        const starPrefix = m[4];
        const verb = m[5];
        const rest = m[6];

        const promptHtml = promptSym ? '<span style="color: #c0c0c0;">&gt; </span>' : '';

        let prefixSym = "";
        let body = "";
        if (hashPrefix) {
            prefixSym = hashPrefix;
            body = hashBody || "";
        } else {
            prefixSym = starPrefix || "";
            body = (verb || "") + (rest || "");
        }

        const fullLine = prefixSym + body;

        const lower = fullLine.toLowerCase();
        if (lower.includes('esquiva tu ataque') ||
            lower.includes('fallas tu ataque') ||
            lower.includes('bloquea tu') ||
            lower.includes('consigue parar') ||
            lower.includes('consigue esquivar')) {
            return `${promptHtml}<span style="color: #808080;">${escapeHtml(fullLine)}</span>`;
        }

        let escapedBody = escapeHtml(body);
        escapedBody = escapedBody.replace(
            /(\()(\d+)(?:(-)(\d+))?(\))/g,
            `<span style="color: #ffff00;">$1</span><span style="color: #ff0000; font-weight: bold;">$2</span><span style="color: #ffffff;">$3</span><span style="color: #ff0000; font-weight: bold;">$4</span><span style="color: #ffff00;">$5</span>`
        );

        let prefixHtml = "";
        if (prefixSym) {
            if (prefixSym.includes('#')) {
                prefixHtml = '<span style="color: #008000;">#</span> ';
            } else if (prefixSym.includes('*')) {
                prefixHtml = '<span style="color: #008000;">*</span> ';
            }
        }

        return `${promptHtml}${prefixHtml}<span style="color: #00ff00;">${escapedBody}</span>`;
    }

    _applyTemplate(m, template) {
        let res = template;
        for (let i = 1; i < m.length; i++) {
            const escapedVal = escapeHtml(m[i] || '');
            res = res.replaceAll(`$${i}`, escapedVal);
        }
        return res;
    }

    colorizeText(plainText) {
        const trimmed = (plainText || '').replace(/\r\n/g, '\n').replace(/\n+$/, '');
        const normalized = trimmed.replace(/\n{3,}/g, '\n\n');
        const lines = normalized ? normalized.split('\n') : [];
        const renderedLines = lines.map(line => this.colorizeLine(line));
        const contentHtml = renderedLines.join('<br />') + '<br />';

        return `<font color="#cccccc" size="2"><div>${contentHtml}</div></font>`;
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { RLColorizerJS, escapeHtml };
}
