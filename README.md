# Reinos de Leyenda (RL) - MUD Log Colorizer

Colorizador de logs de combate y rol para **[Reinos de Leyenda (RL)](https://reinosdeleyenda.com/)**, diseñado específicamente para que jugadores que juegan en **modo accesibilidad (sin colores / lectores de pantalla)** puedan convertir sus logs en bruto a formato HTML con la paleta de colores visual oficial del cliente Mudlet para subirlos directamente a **[Deathlogs](https://deathlogs.com/)**.

---

## 🌐 Probar en vivo (GitHub Pages)

👉 **[Abrir RL Log Colorizer en vivo](https://FrancoMPaniagua.github.io/rl-mud-colorizer/)**

---

## ✨ Características Principales

* **Formato 1:1 Nativo para Deathlogs:**
  * Genera el bloque HTML estándar de Mudlet (`<font color="#cccccc" size="2"><div>...<br /></div></font>`).
  * Sin saltos de línea `\n` redundantes para evitar el problema de doble interlineado dentro del `<PRE>` de Deathlogs.
  * Botón de copiado directo con un solo clic listo para pegar en el formulario de envío.
* **100% Paridad entre Python y JavaScript:**
  * Motor dual: [`engine.py`](engine.py) y [`webapp/engine.js`](webapp/engine.js) ejecutan exactamente la misma lógica y producen resultados carácter a carácter idénticos.
* **Colores Oficiales por Raza de Jugador:**
  * Identificación precisa de jugadores mediante sufijos de raza (`(Elf)`, `(Melf)`, `(Orc)`, `(Mdro)`, `(Gob)`, etc.).
  * No colorea NPCs genéricos como si fueran jugadores.
* **Catálogo de Habitaciones (Rooms):**
  * Más de 280 habitaciones catalogadas con su color exacto minado a partir de logs reales de jugadores videntes (zonas urbanas en plata, bosques en verde, templos en blanco, caminos de agua en cian, mesetas en oliva, etc.).
  * Habitaciones no catalogadas usan el verde por defecto (`#008000`).
* **Soporte Completo de Combate y Magia:**
  * Ataques propios en verde brillante (`#00ff00`) con números de daño resaltados.
  * Maniobras y preparación de enemigos en fucsia/rojo.
  * Esquivas, paradas y bloqueos en gris tenue (`#808080`).
  * Cánticos y finalización de hechizos en cian (`#00ffff`).

---

## 🎨 Leyenda Oficial de Razas

| Raza / Etiqueta | Color | Código Hex |
| :--- | :--- | :--- |
| **Elfo / Semi-Elfo** (`Elf`, `Melf`, `S-e`) | Verde | `#008000` |
| **Enano** (`Ena`, `Enano`) | Oliva | `#808000` |
| **Kobold** (`Kob`) | Granate / Rojo oscuro | `#800000` |
| **Drow / Semi-Drow** (`Mdro`, `Drow`, `S-d`) | Gris | `#808080` |
| **Duergar** (`Duer`, `Drg`) | Púrpura | `#800080` |
| **Goblin** (`Gob`) | Verde lima | `#00ff00` |
| **Gnomo** (`Gno`) | Cian | `#00ffff` |
| **Humano** (`Hum`) | Amarillo | `#ffff00` |
| **Gnoll** (`Gnl`, `Gnol`) | Rojo brillante | `#ff0000` |
| **Halfling** (`Hal`, `Hlf`) | Magenta | `#ff00ff` |
| **Lagarto / Hombre-Lagarto** (`Lag`, `Hlag`) | Azul | `#0000ff` |
| **Minotauro** (`Min`, `Mino`) | Plata | `#c0c0c0` |
| **Orco / Semi-Orco** (`Orc`, `S-o`) | Blanco | `#ffffff` |
| **Ogro-Mago / Ogro** (`Org`, `Orgo`) | Cian oscuro / Teal | `#008080` |

---

## 🚀 Uso Rápido

### Opción 1: Aplicación Web (Navegador)
1. Entra a la web en **[GitHub Pages](https://FrancoMPaniagua.github.io/rl-mud-colorizer/)**.
2. Pega tu log en el panel izquierdo (o arrastra un archivo `.txt`).
3. Haz clic en **Copiar para Deathlogs**.
4. Pega el contenido directamente en el formulario de subida de [Deathlogs.com](https://deathlogs.com/).

### Opción 2: Línea de comandos (Python)

```bash
# Colorizar un log desde un archivo de texto
python -c "from engine import RLColorizer; from pathlib import Path; c = RLColorizer(); print(c.colorize_text(Path('tu_log.txt').read_text(encoding='utf-8')))" > log_colorizado.html
```

---

## 🛠️ Estructura del Proyecto

```text
├── engine.py              # Motor principal en Python
├── build_rules.py         # Compilador de reglas a JSON y JS
├── mine_rooms.py          # Extractor de habitaciones desde logs videntes
├── rooms.json             # Catálogo de 280+ rooms y sus colores
├── rules.json             # Reglas compiladas de colorizado
├── test_parity_diff.py    # Test de paridad 100% entre Python y JS
├── webapp/                # Aplicación Web estática
│   ├── index.html         # Interfaz de usuario
│   ├── style.css          # Estilos MUD terminal
│   ├── app.js             # Controlador de eventos y UI
│   ├── engine.js          # Motor JavaScript (espejo de engine.py)
│   └── rules.js           # Reglas compiladas para el navegador
└── .github/workflows/
    └── deploy.yml         # Despliegue automático a GitHub Pages
```

---

## 🧪 Pruebas y Validación de Paridad

Para verificar que los motores de Python y JavaScript producen exactamente la misma salida sin discrepancias:

```bash
python test_parity_diff.py
```

Resultado esperado:
```text
Total Python lines: 2475
Total Node.js lines: 2475
>>> SUCCESS! PERFECT 100% PARITY BETWEEN PYTHON AND JAVASCRIPT! <<<
```

---

## 🤝 Fork y Contribuciones

Si eres un jugador de RL o desarrollador y quieres agregar nuevas reglas, colores de rooms o habilidades:

1. Haz un **Fork** de este repositorio.
2. Si agregas o modificas reglas en `build_rules.py` o habitaciones en `rooms.json`, ejecuta:
   ```bash
   python build_rules.py
   python test_parity_diff.py
   ```
3. Envía tu **Pull Request**.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
