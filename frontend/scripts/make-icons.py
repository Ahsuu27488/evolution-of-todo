"""Generate Chronos app icons from the orrery mark (components/layout/brand-logo.tsx).

Run from frontend/:  python scripts/make-icons.py
Writes: app/favicon.ico, app/apple-icon.png, public/icon-192.png, public/icon-512.png,
public/badge-96.png (monochrome, for Android
notification badges). The SVG favicon (app/icon.svg) is hand-written.
"""

from pathlib import Path

from PIL import Image, ImageDraw

INK = (14, 20, 36, 255)  # --custom-background (dark)
STARLIGHT = (233, 236, 245)  # --custom-foreground (dark)
GOLD = (242, 184, 75, 255)  # --custom-primary (dark)
SS = 4  # supersampling factor

ROOT = Path(__file__).resolve().parent.parent


def draw_mark(size: int, *, background: bool, mono: bool = False, padding: float = 0.14) -> Image.Image:
    """The mark on a 32-unit grid: tilted orbit, gold core, one moon."""
    big = size * SS
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if background:
        d.rounded_rectangle((0, 0, big - 1, big - 1), radius=int(big * 0.23), fill=INK)

    inner = big * (1 - 2 * padding)
    off = big * padding
    u = inner / 32  # one grid unit

    def pt(x: float, y: float) -> tuple[float, float]:
        return off + x * u, off + y * u

    # Orbit: ellipse rx=13 ry=5.5 rotated -24deg, drawn on its own layer then rotated
    orbit = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    od = ImageDraw.Draw(orbit)
    cx, cy = pt(16, 16)
    rx, ry = 13 * u, 5.5 * u
    stroke = max(1, round(1.6 * u))
    ring_color = (255, 255, 255, 255) if mono else (*STARLIGHT, 130)
    od.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=ring_color, width=stroke)
    orbit = orbit.rotate(24, resample=Image.BICUBIC, center=(cx, cy))
    img.alpha_composite(orbit)

    d = ImageDraw.Draw(img)
    core_r = 5.4 * u
    d.ellipse((cx - core_r, cy - core_r, cx + core_r, cy + core_r), fill=(255, 255, 255, 255) if mono else GOLD)
    mx, my = pt(27.2, 10.8)
    moon_r = 2.0 * u
    d.ellipse((mx - moon_r, my - moon_r, mx + moon_r, my + moon_r), fill=(255, 255, 255, 255) if mono else (*STARLIGHT, 255))

    return img.resize((size, size), Image.LANCZOS)


def main() -> None:
    public = ROOT / "public"
    draw_mark(192, background=True).save(public / "icon-192.png")
    draw_mark(512, background=True).save(public / "icon-512.png")
    draw_mark(180, background=True, padding=0.16).save(ROOT / "app" / "apple-icon.png")
    draw_mark(96, background=False, mono=True, padding=0.06).save(public / "badge-96.png")
    ico = draw_mark(256, background=True)
    ico.save(ROOT / "app" / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    print("icons written")


if __name__ == "__main__":
    main()
