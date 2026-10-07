"""
Comprehensive Rules Compiler for RL MUD Colorizer (v5)
Enriched with patterns from Velkyn (caster), Thildarg (classic client),
and community standard RL color formatting.
"""

import json
from pathlib import Path

BASE_DIR = Path(r"C:\Users\Compumar\mud_colorizer")
RULES_FILE = BASE_DIR / "rules.json"

RULES_DATA = {
    "theme": {
        "bg": "#000000",
        "default_fg": "#c0c0c0",
        "font_family": "'Bitstream Vera Sans Mono', 'Courier New', monospace"
    },
    "colors": {
        "white": "#ffffff",
        "silver": "#c0c0c0",
        "gray": "#808080",
        "dark_gray": "#555555",
        "red": "#ff4444",
        "dark_red": "#aa0000",
        "bright_red": "#ff0000",
        "green": "#00ff00",
        "dark_green": "#008000",
        "yellow": "#ffff00",
        "olive": "#717100",
        "blue": "#0800ff",
        "dark_blue": "#0000aa",
        "cyan": "#00ffff",
        "dark_cyan": "#008080",
        "magenta": "#ff00ff"
    },
    "race_colors": {
        "elfo": "#008000",
        "elf": "#008000",
        "melf": "#008000",
        "semi-elfo": "#008000",
        "s-e": "#008000",
        "enano": "#808000",
        "ena": "#808000",
        "kobold": "#800000",
        "kob": "#800000",
        "drow": "#808080",
        "mdro": "#808080",
        "semi-drow": "#808080",
        "s-d": "#808080",
        "duergar": "#800080",
        "duer": "#800080",
        "drg": "#800080",
        "goblin": "#00ff00",
        "gob": "#00ff00",
        "gnomo": "#00ffff",
        "gno": "#00ffff",
        "humano": "#ffff00",
        "hum": "#ffff00",
        "gnoll": "#ff0000",
        "gnl": "#ff0000",
        "gnol": "#ff0000",
        "halfling": "#ff00ff",
        "hal": "#ff00ff",
        "hlf": "#ff00ff",
        "lagarto": "#0000ff",
        "hombre-lagarto": "#0000ff",
        "hlag": "#0000ff",
        "lag": "#0000ff",
        "minotauro": "#c0c0c0",
        "min": "#c0c0c0",
        "mino": "#c0c0c0",
        "orco": "#ffffff",
        "semi-orco": "#ffffff",
        "orc": "#ffffff",
        "s-o": "#ffffff",
        "ogro-mago": "#008080",
        "ogro": "#008080",
        "org": "#008080",
        "orgo": "#008080"
    },
    "room_colors": {},
    "rules": [
        # --- 1. PROMPTS & HEALTH DELTAS ---
        {
            "id": "prompt_full",
            "category": "prompt",
            "priority": 10,
            "pattern": r"^(?:>|\])?\s*(Pvs?:\s*(?:\d+(?:[/(]\d+\)?)?)?)(?:\s*\(([+-]?\d+)\))?(\s*Pe:\s*\d+(?:[/(]\d+\)?)?)?(?:\s*\(([+-]?\d+)\))?(.*)$",
            "type": "composite_prompt_extended"
        },
        {
            "id": "prompt_pe_xp",
            "category": "prompt",
            "priority": 10,
            "pattern": r"^(?:>|\])?\s*(Pe:\s*\d+(?:[/(]\d+\)?)?)(?:\s*\(([+-]?\d+)\))?(.*)$",
            "replace": r'<span style="color: #008000; font-weight: bold;">$1</span><span style="color: #008000;">$2$3</span>'
        },
        {
            "id": "prompt_hp_delta",
            "category": "prompt",
            "priority": 11,
            "pattern": r"^(?:>|\])?\s*(HP:\s*)([+-]?\d+)\s*$",
            "type": "composite_hp_delta"
        },
        {
            "id": "prompt_symbol_alone",
            "category": "prompt",
            "priority": 12,
            "pattern": r"^(?:>|\])\s*$",
            "replace": r'<span style="color: #c0c0c0;">&gt; </span>'
        },

        # --- 2. SYSTEM EXP, GLORY, LOGROS & LOCKS (GRAY BASE + HIGHLIGHTED NUMBERS) ---
        {
            "id": "system_exp",
            "category": "system",
            "priority": 20,
            "pattern": r"^(?:[>\]]\s*)?(\[Obtienes )(\d+)( puntos de experiencia\])\s*$",
            "replace": r'<span style="color: #c0c0c0;">$1</span><span style="color: #ffffff; font-weight: bold;">$2</span><span style="color: #c0c0c0;">$3</span>'
        },
        {
            "id": "system_glory",
            "category": "system",
            "priority": 21,
            "pattern": r"^(?:[>\]]\s*)?(\[Obtienes )(\d+)( puntos de gloria\])\s*$",
            "replace": r'<span style="color: #c0c0c0;">$1</span><span style="color: #ffff00; font-weight: bold;">$2</span><span style="color: #c0c0c0;">$3</span>'
        },
        {
            "id": "system_oficio",
            "category": "system",
            "priority": 22,
            "pattern": r"^(?:[>\]]\s*)?(\[Obtienes )(\d+)( puntos? de oficio\])\s*$",
            "replace": r'<span style="color: #c0c0c0;">$1</span><span style="color: #ffffff; font-weight: bold;">$2</span><span style="color: #c0c0c0;">$3</span>'
        },
        {
            "id": "system_logro",
            "category": "system",
            "priority": 23,
            "pattern": r"^(?:[>\]]\s*)?(\[Obtienes el logro ')('?[^']+?'?)(' \([^)]+\)\])\s*$",
            "replace": r'<span style="color: #c0c0c0;">$1</span><span style="color: #ffff00; font-weight: bold;">$2</span><span style="color: #c0c0c0;">$3</span>'
        },
        {
            "id": "system_lock",
            "category": "system",
            "priority": 24,
            "pattern": r"^(?:[>\]]\s*)?(\[El bloqueo )('?[^']+?'?)(\s+termina\])\s*$",
            "replace": r'<span style="color: #c0c0c0;">$1</span><span style="color: #ffff00;">$2</span><span style="color: #c0c0c0;">$3</span>'
        },
        {
            "id": "system_faith",
            "category": "system",
            "priority": 25,
            "pattern": r"^(?:[>\]]\s*)?(\[Tu fe en .+? ha (?:disminuido|aumentado) en )(\d+)( puntos\])\s*$",
            "replace": r'<span style="color: #c0c0c0;">$1</span><span style="color: #ffffff; font-weight: bold;">$2</span><span style="color: #c0c0c0;">$3</span>'
        },
        {
            "id": "system_tiradas",
            "category": "system",
            "priority": 26,
            "pattern": r"^(?:[>\]]\s*)?(\[)(Tiradas)(\]:?\s+.*?\s+Tirada:\s+\d+\s*\()((?:Éxito|Fallo|Exito))(\)\.?)\s*$",
            "type": "composite_tirada"
        },
        {
            "id": "system_info_tags",
            "category": "system",
            "priority": 27,
            "pattern": r"^(?:[>\]]\s*)?(\[)(INFO|AYUDA|ADVERTENCIA|ERROR)(\]:\s*)(.*)$",
            "type": "composite_info"
        },
        {
            "id": "system_command_queue",
            "category": "system",
            "priority": 28,
            "pattern": r"^(?:[>\]]\s*)?(Cola de comandos borrada \(')(peleas parar)(' detendr[áa] los (?:ataques|combates) si es lo que quer[íi]as\)\.?)\s*$",
            "replace": r'<span style="color: #c0c0c0;">$1</span><span style="color: #ffff00;">$2</span><span style="color: #c0c0c0;">$3</span>'
        },
        {
            "id": "system_buff_tracker",
            "category": "system",
            "priority": 29,
            "pattern": r"^(?:[>\]]\s*)?(Pieles:)(\d+)\s*$",
            "replace": r'<span style="color: #008000;">$1</span><span style="color: #ffff00; font-weight: bold;">$2</span>'
        },

        # --- 3. CHANNELS & COMMUNICATION ---
        {
            "id": "channels_standard",
            "category": "channel",
            "priority": 30,
            "pattern": r"^(?:[>\]]\s*)?(\[[A-Za-z0-9_]+\])(\s+[^:]+:)(.*)$",
            "replace": r'<span style="color: #008080;">$1</span><span style="color: #ffffff;">$2</span><span style="color: #00ffff;">$3</span>'
        },
        {
            "id": "say_player",
            "category": "channel",
            "priority": 31,
            "pattern": r"^(?:[>\]]\s*)?(Dices(?: en [^:]+)?:)(.*)$",
            "replace": r'<span style="color: #00ffff;">$1</span><span style="color: #ffffff;">$2</span>'
        },
        {
            "id": "say_other",
            "category": "channel",
            "priority": 32,
            "pattern": r"^(?:[>\]]\s*)?([A-Z][a-z0-9'-]+ dice(?: en [^:]+)?:)(.*)$",
            "replace": r'<span style="color: #008080;">$1</span><span style="color: #c0c0c0;">$2</span>'
        },
        {
            "id": "tell_player",
            "category": "channel",
            "priority": 33,
            "pattern": r"^(?:[>\]]\s*)?([A-Z][a-z0-9'-]+ te dice:)(.*)$",
            "replace": r'<span style="color: #00ffff;">$1</span><span style="color: #ffffff;">$2</span>'
        },

        # --- 4. SPELLS, CASTING & MAGICAL EFFECTS ---
        {
            "id": "spell_chant",
            "category": "spell",
            "priority": 40,
            "pattern": r"^(?:[>\]]\s*)?([A-ZÁÉÍÓÚ][\w\s'-]+?\s+pronuncia el cántico:\s*|Pronuncias el cántico:\s*)('[^']+')$",
            "replace": r'<span style="color: #008080;">$1</span><span style="color: #00ffff; font-style: italic;">$2</span>'
        },
        {
            "id": "spell_cast_start",
            "category": "spell",
            "priority": 41,
            "pattern": r"^(?:[>\]]\s*)?(.*?(?:formular el hechizo|formular el cántico|obrar un hechizo)\s*)('[^']+'\.?)",
            "replace": r'<span style="color: #ffffff;">$1</span><span style="color: #00ffff;">$2</span>'
        },
        {
            "id": "spell_cast_enemy",
            "category": "spell",
            "priority": 42,
            "pattern": r"^(?:[>\]]\s*)?([A-ZÁÉÍÓÚ][\w\s'-]+?\s+(?:empieza a formular un hechizo|mueve la boca mientras dice lo que para ti son palabras sin sentido)\b.*)$",
            "replace": r'<span style="color: #ff00f3; font-weight: bold;">$1</span>'
        },
        {
            "id": "spell_cast_enemy_stop",
            "category": "spell",
            "priority": 43,
            "pattern": r"^(?:[>\]]\s*)?([A-Z][a-z0-9'-]+\s+deja de formular\..*)$",
            "replace": r'<span style="color: #808080;">$1</span>'
        },
        {
            "id": "spell_completion",
            "category": "spell",
            "priority": 44,
            "pattern": r"^(?:[>\]]\s*)?(Terminas tu hechizo\s*.*|Tu hechizo (?:de '[^']+' )?termina\s*.*)$",
            "type": "composite_spell_completion"
        },
        {
            "id": "spell_projectiles_invocations",
            "category": "spell",
            "priority": 45,
            "pattern": r"^(?:([>\]])\s*)?(#\s*)?(¡?El cielo ruge cuando invocas un relámpago\b.*|\d+\s+misiles mágicos surgen de tus dedos e impactan\b.*|¡?Invocas\b.*|\d+\s+rayos caen desde el cielo\b.*|Un rayo (?:de [^.]+ surge de|impacta (?:sobre|junto a))\b.*|Alzas tu mano, y alrededor de la misma comienzan a formarse\b.*|Trazas con ágiles movimientos en tus dedos\b.*|Posas las manos en el suelo e invocas\b.*|Tu hechizo termina a golpe de trompeta.*)$",
            "type": "composite_magic_missiles"
        },
        {
            "id": "spell_failed_distracted",
            "category": "spell",
            "priority": 46,
            "pattern": r"^(?:[>\]]\s*)?(.*?(?:pierde la concentración|arruinado|no eres capaz de concentrarte|Estás realizando los movimientos de un hechizo|Tus objetivos ya no están al alcance|Tu maniobra de \w+ se ve interrumpida|resiste los efectos de tu hechizo).*)$",
            "replace": r'<span style="color: #ff8080;">$1</span>'
        },
        {
            "id": "spell_healing_effect",
            "category": "spell",
            "priority": 47,
            "pattern": r"^(?:[>\]]\s*)?(Curas\s+(?:algunas|todas|gran parte)\s+de\s+(?:tus|las)\s+heridas\b.*?\.?)\s*$",
            "replace": r'<span style="color: #ff0000;">$1</span>'
        },

        # --- 5. MOVEMENTS, ROOM EXITS & ENTITIES ---
        {
            "id": "room_exits_inline",
            "category": "movement",
            "priority": 50,
            "pattern": r"^(?:([>\]])\s*)?(.+?)\s+([\[\(](?:\|?[a-zA-ZáéíóúÁÉÍÓÚ]+\|?)(?:,(?:\|?[a-zA-ZáéíóúÁÉÍÓÚ]+\|?))*[\]\)])\s*$",
            "type": "composite_room_exits"
        },
        {
            "id": "room_title_standalone",
            "category": "movement",
            "priority": 50,
            "pattern": r"^(?:([>\]])\s*)?([A-ZÁÉÍÓÚ][\w\s'-]+:\s+[A-ZÁÉÍÓÚ][\w\s'-]+)\s*$",
            "type": "composite_room_title"
        },
        {
            "id": "movement_enter_exit",
            "category": "movement",
            "priority": 51,
            "pattern": r"^(?:([>\]])\s*)?((?:\b(?:un|una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez)\s+)?[*|\-~/]*\s*[A-Za-zÁÉÍÓÚáéíóúñÑ0-9\x27_-]+(?:\s+[|*\-~/]+)?\s*(?:\((?:Hlag|Lag|Melf|Elf|S-e|Gob|Gno|Hum|Orc|S-o|Ena|Mdro|Drow|S-d|Hal|Hlf|Duer|Drg|Min|Mino|Gnl|Gnol|Kob|Org|Orgo|Drax|Ctd|Cent|Kuo|Ggt|S-g)\)(?:es)?(?:\s+\([^)]+\))?|(?:\([^)]+\))?)?(?:\s*[|*\-~/]+)?)\s+(se va en dirección|se va hacia|huye hacia|se dirige a|llega nadando desde|llega de la superficie|llega de la|llega desde|se va|llega)\s+(.*?)\.?$",
            "type": "composite_movement"
        },
        {
            "id": "room_exits_list",
            "category": "movement",
            "priority": 52,
            "pattern": r"^(?:[>\]]\s*)?(Puedes ver (?:una|dos|tres|cuatro|cinco|seis|[a-z]+) salidas?:\s*)(.*)$",
            "replace": r'<span style="color: #c0c0c0;">$1</span><span style="color: #ffff00;">$2</span>'
        },
        {
            "id": "room_player_present",
            "category": "movement",
            "priority": 53,
            "pattern": r"^(?:([>\]])\s*)?([^.\n]*?\((?:Hlag|Lag|Melf|Elf|S-e|Gob|Gno|Hum|Orc|S-o|Ena|Mdro|Drow|S-d|Hal|Hlf|Duer|Drg|Min|Mino|Gnl|Gnol|Kob|Org|Orgo|Drax|Ctd|Cent|Kuo|Ggt|S-g)\)[^.\n]*?)\s+(está aquí|están aquí|está allí|están allí)\.\s*$",
            "type": "composite_room_player"
        },
        {
            "id": "room_npc_present",
            "category": "movement",
            "priority": 53,
            "pattern": r"^(?:([>\]])\s*)?([^.\n]+?)\s+(está aquí|están aquí|está allí|están allí)\.\s*$",
            "type": "composite_room_npc"
        },
        {
            "id": "follower_player_notification",
            "category": "movement",
            "priority": 54,
            "pattern": r"^(?:([>\]])\s*)?([A-ZÁÉÍÓÚ][a-z0-9'-].*?\((?:Hlag|Lag|Melf|Elf|S-e|Gob|Gno|Hum|Orc|S-o|Ena|Mdro|Drow|S-d|Hal|Hlf|Duer|Drg|Min|Mino|Gnl|Gnol|Kob|Org|Orgo|Drax|Ctd|Cent|Kuo|Ggt|S-g)\).*?)\s+(te sigue|te siguen)\.\s*$",
            "type": "composite_follower_player"
        },
        {
            "id": "follower_npc_notification",
            "category": "movement",
            "priority": 54,
            "pattern": r"^(?:[>\]]\s*)?([A-Z][a-z0-9'-].*?)\s+(te sigue|te siguen)\.\s*$",
            "replace": r'<span style="color: #c0c0c0;">$1 $2.</span>'
        },
        {
            "id": "corpse_room",
            "category": "movement",
            "priority": 55,
            "pattern": r"^(?:[>\]]\s*)?((?:Cuerpo|Restos putrefactos|Cadáver|Esqueleto) de [^.]+?\.|(?:Charco|Charcos) de sangre\.?)\s*$",
            "replace": r'<span style="color: #aa0000; font-weight: bold;">$1</span>'
        },

        # --- 6. COMBAT (DEATH, FATAL BLOWS, CRITS, ATTACKS) ---
        {
            "id": "combat_death_broadcast",
            "category": "combat",
            "priority": 60,
            "pattern": r"^(?:[>\]]\s*)?(.*?(?:ha muerto a manos de|ha muerto\.|cae al suelo sin vida|da un grito desgarrador|orbita al Limbo).*)$",
            "replace": r'<span style="color: #ff0000; font-weight: bold;">$1</span>'
        },
        {
            "id": "combat_under_attack",
            "category": "combat",
            "priority": 60,
            "pattern": r"^(?:[>\]]\s*)?(Est[áa]s siendo atacado por\s+.*?\.)\s*$",
            "replace": r'<span style="color: #ff0000; font-weight: bold;">$1</span>'
        },
        {
            "id": "combat_fatal_blow",
            "category": "combat",
            "priority": 61,
            "pattern": r"^(?:[>\]]\s*)?(Propinas el golpe mortal a\s+.*)$",
            "replace": r'<span style="color: #00ff00; font-weight: bold;">$1</span>'
        },
        {
            "id": "combat_crit_eviscerate",
            "category": "combat",
            "priority": 62,
            "pattern": r"^(?:[>\]]\s*)?(.*?(?:eviscera|destriparte|un enorme boquete|sangre y carne triturada).*)$",
            "replace": r'<span style="color: #ff0000;">$1</span>'
        },
        {
            "id": "combat_skin_absorb",
            "category": "combat",
            "priority": 62,
            "pattern": r"^(?:[>\]]\s*)?(\*?\s*)(El ataque de\s+.*?\s+rebota en tu piel de piedra\.)\s*$",
            "replace": r'<span style="color: #ffff00;">$1$2</span>'
        },
        {
            "id": "combat_dodge_parry",
            "category": "combat",
            "priority": 63,
            "pattern": r"^(?:[>\]]\s*)?((?:#|\*)?\s*.*?(?:\b(?:esquiva|esquivas|esquivar|para|paras|parar|bloquea|bloqueas|bloquear)\b.*?(?:\b(?:tu ataque|su ataque|el ataque|el impacto|el golpe|la maniobra|la embestida|una lluvia)\b|mientras parpadea absorviendo)|fallas tu ataque|eludes la búsqueda|¡?Logras (?:esquivar|parar|bloquear)\b.*?).*)$",
            "replace": r'<span style="color: #808080;">$1</span>'
        },
        {
            "id": "combat_enemy_attack",
            "category": "combat",
            "priority": 64,
            "pattern": r"^(?:[>\]]\s*)?(\*?\s*)(.*? te (?:intenta\s+)?(?:golpea|corta|desgarra|lacera|fustiga|clava|rasguña|entierra|muerde|patea|raja|aplasta|arremete|abraza|sorbe|alcanza|fulmina|purifica|perfora|corrompe|apuñalar|mutilar|desmembrar)\b.*)$",
            "replace": r'<span style="color: #aa0000;">*</span> <span style="color: #cc6666;">$2</span>'
        },
        {
            "id": "combat_enemy_maneuver",
            "category": "combat",
            "priority": 65,
            "pattern": r"^(?:([>\]])\s*)?(!\s*)?([A-Za-zÁÉÍÓÚáéíóúñÑ0-9'|\-/() ]+?)\s+(se prepara para ejecutar|se prepara para|tensa sus músculos|se echa hacia atrás|empieza a centrar|comienza a serpentear|te examina|examina las defensas de|te mira fijamente)\b(.*)$",
            "type": "composite_enemy_maneuver"
        },
        {
            "id": "combat_poison_effects",
            "category": "combat",
            "priority": 66,
            "pattern": r"^(?:[>\]]\s*)?(.*?(?:te envenena|ponzoña virulenta|garras contaminadas|saliva tóxica).*)$",
            "replace": r'<span style="color: #cc6666;">$1</span>'
        },
        {
            "id": "combat_player_attacks",
            "category": "combat",
            "priority": 67,
            "pattern": r"^(?:([>\]])\s*)?(?:(#\s+)(.+)|(\*\s*)?(?:¡)?(Tu\s+(?:ataque|estocada|golpe|flecha|corte|puñetazo|patada|mordisco|zarpazo|mandoble|hachazo|embestida)\s+(?:desgarra|atraviesa|corta|raja|golpea|impacta|sorbe|alcanza|penetra|rebota|falla|choca)\b|Tu\s+[A-ZÁÉÍÓÚ][\w\s'-]+(?:se ilumina cuando|atraviesa|desgarra|golpea)\b|(?:Muerdes|Pateas|Golpeas|Desgarras|Atraviesas|Clavas|Rajas|Rajás|Cortas|Aplastas|Cabeceas|Alcanzas|Perforas|Enfermas|Envenenas|Hundes|Laceras|Pinchas|Fustigas|Empalas|Trituras|Acoceas|Descargas una furia de golpes)\b)(.*))$",
            "type": "composite_player_combat"
        },

        # --- 7. BUFFS, SKILLS, EQUIPMENT & CRAFTING ---
        {
            "id": "system_buff_expire",
            "category": "system",
            "priority": 70,
            "pattern": r"^(?:[>\]]\s*)?(Tu armadura deja de estar expuesta\b.*|Tu capa derrama parte de la sangre\b.*|Tu resistencia de [a-z]+ se desvanece\b.*|Tu capacidad de movimiento vuelve\b.*|Tu poder mágico vuelve\b.*)$",
            "replace": r'<span style="color: #808080;">$1</span>'
        },
        {
            "id": "system_equipment_action",
            "category": "system",
            "priority": 71,
            "pattern": r"^(?:[>\]]\s*)?((?:Dejas de sostener|Empuñas|Te pones|Te quitas|Estás intentando equilibrar|Finalmente equilibras)\s+.*)$",
            "replace": r'<span style="color: #c0c0c0;">$1</span>'
        },
        {
            "id": "system_crafting_skinning",
            "category": "system",
            "priority": 72,
            "pattern": r"^(?:[>\]]\s*)?((?:Armado con tu|Continúas desollando|Continúas con tu sucio trabajo|Tras dedicar largos minutos desollando)\s+.*)$",
            "replace": r'<span style="color: #c0c0c0;">$1</span>'
        },
        {
            "id": "system_actions_warning",
            "category": "system",
            "priority": 73,
            "pattern": r"^(?:[>\]]\s*)?(Ignorando\s+.*|No puedes\s+.*|No estás\s+.*|No hay nadie\s+.*|El objetivo\s+.*|Parece que\s+.*|Ese nombre\s+.*|Has usado\s+.*|No tienes\s+.*)\s*$",
            "replace": r'<span style="color: #808080;">$1</span>'
        },
        {
            "id": "skills_player_prep",
            "category": "skill",
            "priority": 74,
            "pattern": r"^(?:[>\]]\s*)?(\+\s*)(.*)$",
            "replace": r'<span style="color: #ffff00; font-weight: bold;">+</span> <span style="color: #0800ff;">$2</span>'
        },
        {
            "id": "skills_actions",
            "category": "skill",
            "priority": 75,
            "pattern": r"^(?:[>\]]\s*)?(Empiezas a\b.*|Intentas\b.*|Logras\b.*|Finalmente logras\b.*|Consigues zafarte\b.*|Te preparas para\b.*|Te mueves en silencio\b.*|Sufres cuando tus músculos\b.*|Tras tu dolorosa conversi[oó]n\b.*|Agotado, eres incapaz\b.*)$",
            "replace": r'<span style="color: #0800ff;">$1</span>'
        },

        # --- 8. PLAYER COMMAND ECHOES ---
        {
            "id": "command_explicit_prompt",
            "category": "command",
            "priority": 80,
            "pattern": r"^(?:>|\])\s+([a-zA-Z0-9_'-]+.*)$",
            "replace": r'<span style="color: #c0c0c0;">&gt; </span><span style="color: #717100;">$1</span>'
        },
        {
            "id": "command_standalone_short",
            "category": "command",
            "priority": 81,
            "pattern": r"^(ojear|mirar|w|si\s+[a-z]+|no|se|so|ne|n|s|e|o|d|arriba|abajo|norte|sur|este|oeste|noreste|noroeste|sudeste|sudoeste|esc|buscar|deso|desollar|sigilar|esconderse|quitar\s+.*|poner\s+.*|coger\s+.*|dejar\s+.*|F\d+|1|2|3|4|5|11|111|cc|int|l|l\s+.*|q|r|pa|co|mo|dn|os|hi|z|a|ge|gne|cn|re|li|gl|lr|cme|cse|cle|cic\s+.*|formular\s+.*|cobardia\s+\d+|vendar\s+.*|nick\s+.*|mnick\s+.*|nickear\s+.*|estado\s+.*|des\s+.*|trepar\s+.*|saltar\s+.*|sacudir\s+.*|peleas\s+.*|stop|parar|pc|go|gn|gs|c|ab|gar|sg|ac|abalanzarse(?:\s+.*)?|desgarrar(?:\s+.*)?|morder(?:\s+.*)?|tajar(?:\s+.*)?|aplastar(?:\s+.*)?|golpecertero(?:\s+.*)?|corte(?:\s+.*)?|estocada(?:\s+.*)?|furia(?:\s+.*)?|concentraci[oó]n)$",
            "replace": r'<span style="color: #717100;">$1</span>'
        }
    ]
}

ROOMS_FILE = BASE_DIR / "rooms.json"
ITEMS_FILE = BASE_DIR / "items.json"
WEBAPP_RULES_FILE = BASE_DIR / "webapp" / "rules.js"

def save_rules():
    if ROOMS_FILE.exists():
        with open(ROOMS_FILE, 'r', encoding='utf-8') as rf:
            rooms_catalog = json.load(rf)
        RULES_DATA["room_colors"] = {k.lower(): v for k, v in rooms_catalog.items()}
        print(f"Loaded {len(RULES_DATA['room_colors'])} room colors from rooms.json")
    else:
        print("Warning: rooms.json not found!")

    if ITEMS_FILE.exists():
        with open(ITEMS_FILE, 'r', encoding='utf-8') as itf:
            items_catalog = json.load(itf)
        RULES_DATA["item_colors"] = {k: v['html'] for k, v in items_catalog.items()}
        print(f"Loaded {len(RULES_DATA['item_colors'])} colored items from items.json")
    else:
        print("Warning: items.json not found!")

    with open(RULES_FILE, 'w', encoding='utf-8') as f:
        json.dump(RULES_DATA, f, indent=2, ensure_ascii=False)
    print(f"Generated v5 rules.json at: {RULES_FILE}")
    
    WEBAPP_RULES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(WEBAPP_RULES_FILE, 'w', encoding='utf-8') as f:
        f.write("// Auto-generated from build_rules.py\nwindow.COLORIZER_RULES = ")
        json.dump(RULES_DATA, f, indent=2, ensure_ascii=False)
        f.write(";\n")
    print(f"Generated webapp/rules.js at: {WEBAPP_RULES_FILE}")

if __name__ == '__main__':
    save_rules()


