from pathlib import Path
from engine import RLColorizer

c = RLColorizer()

# Desktop
desk = Path(r"C:\Users\Compumar\Desktop\color_logs\log_plano.txt")
if desk.exists():
    out = c.colorize_text(desk.read_text(encoding='utf-8'))
    (Path(r"C:\Users\Compumar\mud_colorizer\output\desktop_log_reconstructed.html")).write_text(out, encoding='utf-8')
    print("Desktop log updated.")

# 57317
p57317 = Path(r"C:\Users\Compumar\mud_colorizer\output\log_57317_pure_plain.txt")
if p57317.exists():
    out = c.colorize_text(p57317.read_text(encoding='utf-8'))
    (Path(r"C:\Users\Compumar\mud_colorizer\output\log_57317_colorized.html")).write_text(out, encoding='utf-8')
    print("57317 log updated.")
