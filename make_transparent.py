from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).parent
SRC, OUT = HERE / "avatars_raw", HERE / "avatars"
OUT.mkdir(exist_ok=True)

for f in sorted(SRC.glob("*.png")) + sorted(SRC.glob("*.jpg")):
    im = Image.open(f).convert("RGBA")
    w, h = im.size
    # Flood-fill the white background from all four corners; white inside the figure stays.
    for xy in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        ImageDraw.floodfill(im, xy, (255, 255, 255, 0), thresh=40)
    im.save(OUT / (f.stem.upper() + ".png"))
    print("saved", f.stem.upper() + ".png")