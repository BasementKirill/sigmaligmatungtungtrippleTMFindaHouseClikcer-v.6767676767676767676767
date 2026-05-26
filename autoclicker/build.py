import subprocess
import sys
from pathlib import Path

from PIL import Image

NAME = "tungtungtungsahursimgaligmaNGaClicker OP v.0.0.2"
PNG_ICON = "assets/Baddie.png"
ENTRY = "main.py"
DIST_DIR = "dist"

script_dir = Path(__file__).parent
png_path = script_dir / PNG_ICON

ico_path = None
if png_path.exists():
    ico_path = script_dir / "assets" / "icon.ico"
    img = Image.open(png_path)
    img.save(ico_path, format="ICO", sizes=[(256, 256)])
    print(f"[BUILD] Converted {PNG_ICON} -> icon.ico")

entry_path = str(script_dir / ENTRY)

cmds = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--noconsole",
    f"--name={NAME}",
    f"--icon={ico_path}" if ico_path else f"--icon={str(png_path)}",
    "--add-data", f"{script_dir / 'assets'};assets",
    "--distpath", str(script_dir / DIST_DIR),
    "--clean",
    "--noconfirm",
    entry_path
]

print(f"[BUILD] Compiling {ENTRY} -> {NAME}.exe ...")
result = subprocess.run(cmds, capture_output=True, text=True)

if ico_path and ico_path.exists():
    ico_path.unlink()
    print("[BUILD] Cleaned up temporary icon.ico")

if result.returncode == 0:
    print(f"[BUILD] SUCCESS! Executable created at: {script_dir / DIST_DIR / f'{NAME}.exe'}")
else:
    print("[BUILD] FAILED!")
    print(result.stdout)
    print(result.stderr)
    sys.exit(1)
