from PIL import Image, ImageDraw

SP = "../sprites/"

skin = (226, 172, 138, 255)
skin_sh = (190, 134, 104, 255)
gray = (140, 140, 148, 255)
suit = (52, 52, 66, 255)
suit_sh = (38, 38, 50, 255)
shirt = (238, 238, 232, 255)
#tie = (205, 50, 62, 255) rojo, verde, azul y opacidad (de 0 a 255)
tie = (40, 120, 220, 255) #azul
#tie_sh = (150, 30, 42, 255)
tie_sh = (20, 70, 150, 255)
pants = (36, 36, 46, 255)
shoes = (20, 20, 26, 255)
brow = (50, 34, 28, 255)
stache = (96, 62, 44, 255)
mouth = (120, 30, 40, 255)
white = (255, 255, 255, 255)
dark = (18, 12, 16, 255)
belt = (200, 170, 70, 255)

img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# cabeza
d.rectangle((18, 10, 30, 24), fill=skin)
for p in [(18, 10), (30, 10), (18, 24), (30, 24)]:
    d.point(p, fill=(0, 0, 0, 0))
d.rectangle((19, 9, 29, 9), fill=skin)
d.line((20, 11, 24, 10), fill=(255, 215, 190, 255))  # brillo calva
# pelo gris a los lados
d.rectangle((17, 14, 18, 19), fill=gray)
d.rectangle((30, 14, 31, 19), fill=gray)
# orejas
d.point((17, 20), fill=skin_sh)
d.point((31, 20), fill=skin_sh)
# cejas bravas
d.line((20, 14, 23, 15), fill=brow)
d.line((28, 14, 25, 15), fill=brow)
# ojos
d.rectangle((21, 16, 22, 17), fill=white)
d.rectangle((26, 16, 27, 17), fill=white)
d.point((22, 17), fill=dark)
d.point((26, 17), fill=dark)
# nariz
d.point((24, 19), fill=skin_sh)
d.point((24, 20), fill=skin_sh)
# bigote y boca gritando
d.rectangle((21, 21, 27, 21), fill=stache)
d.point((20, 22), fill=stache)
d.point((28, 22), fill=stache)
d.rectangle((23, 23, 25, 23), fill=mouth)
# cuello
d.rectangle((22, 25, 26, 26), fill=skin_sh)

# torso: saco
d.rectangle((14, 26, 33, 38), fill=suit)
d.line((14, 37, 33, 37), fill=suit_sh)
d.rectangle((21, 26, 27, 38), fill=shirt)
d.polygon([(21, 26), (24, 29), (27, 26)], fill=suit)
# corbata
d.rectangle((23, 27, 25, 28), fill=tie_sh)
d.rectangle((23, 29, 25, 35), fill=tie)
d.point((24, 36), fill=tie_sh)
d.polygon([(23, 35), (25, 35), (24, 37)], fill=tie)
d.rectangle((16, 30, 18, 32), fill=belt)
# brazos (uno señalando)
d.rectangle((11, 27, 14, 36), fill=suit)
d.rectangle((33, 27, 36, 36), fill=suit)
d.rectangle((11, 37, 14, 39), fill=skin)
d.rectangle((33, 37, 36, 39), fill=skin)
d.point((12, 40), fill=skin)  # dedo
# cinturón y pantalón
d.rectangle((17, 38, 30, 38), fill=belt)
d.rectangle((17, 39, 30, 44), fill=pants)
d.line((24, 40, 24, 44), fill=(26, 26, 34, 255))
d.rectangle((16, 44, 23, 46), fill=shoes)
d.rectangle((25, 44, 32, 46), fill=shoes)

# contorno
px = img.load()
out = img.copy()
po = out.load()
for y in range(48):
    for x in range(48):
        if px[x, y][3] == 0:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < 48 and 0 <= ny < 48 and px[nx, ny][3] > 0:
                    po[x, y] = dark
                    break
out.save(SP + "boss_48.png")
bg = Image.new("RGBA", (384, 384), (14, 14, 16, 255))
bg.alpha_composite(out.resize((384, 384), Image.NEAREST))
bg.save(SP + "boss_preview.png")
print("ok")
