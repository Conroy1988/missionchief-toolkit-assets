"""Export the approved Blackout Command artwork at Chromium icon sizes."""
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[1]
source = Image.open(root / 'extension/branding/blackout-command.png').convert('RGBA')
out = root / 'extension/icons'
out.mkdir(exist_ok=True)
for size in (16, 32, 48, 128):
    inner = round(size * .75) if size == 128 else size
    scaled = source.resize((inner, inner), Image.Resampling.LANCZOS)
    canvas = Image.new('RGBA', (size, size))
    canvas.alpha_composite(scaled, ((size-inner)//2, (size-inner)//2))
    canvas.save(out / f'icon-{size}.png')
