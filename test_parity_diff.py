import subprocess
from pathlib import Path
from engine import RLColorizer

# Colorize with Python
p_colorizer = RLColorizer()
plain_path = Path(r"C:\Users\Compumar\mud_colorizer\output\log_57317_pure_plain.txt")
raw_text = plain_path.read_text(encoding='utf-8')
py_output = p_colorizer.colorize_text(raw_text)

# Colorize with Node.js
node_script = """
const fs = require('fs');
const { RLColorizerJS } = require('./webapp/engine.js');
const rules = JSON.parse(fs.readFileSync('./rules.json', 'utf8'));
const c = new RLColorizerJS(rules);
const text = fs.readFileSync('./output/log_57317_pure_plain.txt', 'utf8');
process.stdout.write(c.colorizeText(text));
"""
Path("temp_node_runner.js").write_text(node_script, encoding='utf-8')
node_proc = subprocess.run(["node", "temp_node_runner.js"], capture_output=True, text=True, encoding='utf-8')
node_output = node_proc.stdout

py_lines = py_output.split('<br />')
node_lines = node_output.split('<br />')

print(f"Total Python lines: {len(py_lines)}")
print(f"Total Node.js lines: {len(node_lines)}")

diffs = 0
for i, (p_line, n_line) in enumerate(zip(py_lines, node_lines)):
    if p_line != n_line:
        diffs += 1
        if diffs <= 5:
            print(f"\nDiff at line {i+1}:")
            print("PY:  ", p_line)
            print("NODE:", n_line)

if diffs == 0 and py_output == node_output:
    print("\n>>> SUCCESS! PERFECT 100% PARITY BETWEEN PYTHON AND JAVASCRIPT! <<<")
else:
    print(f"\nTotal line differences: {diffs}, exact match: {py_output == node_output}")

Path("temp_node_runner.js").unlink(missing_ok=True)
