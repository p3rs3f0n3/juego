from PIL import Image, ImageDraw

skin = (141, 88, 58, 255)
skin_sh = (112, 66, 42, 255)
hair = (38, 26, 24, 255)
hair_hl = (72, 50, 44, 255)
frame = (28, 28, 40, 255)
lens = (160, 215, 235, 255)
lips = (160, 70, 75, 255)
cardi = (30, 140, 150, 255)
cardi_sh = (22, 105, 115, 255)
shirt = (240, 240, 235, 255)
pants = (44, 50, 82, 255)
shoes = (32, 26, 32, 255)
badge = (230, 190, 60, 255)
outline = (18, 12, 16, 255)

img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# Afro (grande y redondo)
d.ellipse((12, 1, 36, 24), fill=hair)
d.ellipse((10, 6, 20, 18), fill=hair)
d.ellipse((28, 6, 38, 18), fill=hair)
# brillos del pelo
for p in [(18, 4), (20, 3), (24, 2), (28, 3), (30, 5), (15, 8), (33, 8), (22, 5), (26, 4)]:
    d.point(p, fill=hair_hl)

# Cara
d.ellipse((18, 11, 30, 26), fill=skin)
# flequillo
d.rectangle((19, 10, 29, 12), fill=hair)
for p in [(19, 13), (29, 13), (18, 14), (30, 14)]:
    d.point(p, fill=hair)
d.point((21, 12), fill=hair_hl)
d.point((26, 12), fill=hair_hl)

# Gafas
d.rectangle((19, 16, 23, 19), outline=frame, fill=lens)
d.rectangle((25, 16, 29, 19), outline=frame, fill=lens)
d.point((24, 17), fill=frame)
# Ojos
d.point((21, 18), fill=outline)
d.point((27, 18), fill=outline)
d.point((22, 17), fill=(255, 255, 255, 255))
d.point((28, 17), fill=(255, 255, 255, 255))
# Nariz y sonrisa
d.point((24, 21), fill=skin_sh)
d.point((22, 23), fill=lips)
d.point((26, 23), fill=lips)
d.line((23, 24, 25, 24), fill=lips)
# mejillas
d.point((20, 21), fill=(170, 100, 80, 255))
d.point((28, 21), fill=(170, 100, 80, 255))

# Cuello
d.rectangle((22, 26, 26, 28), fill=skin_sh)

# Torso: cárdigan + camisa
d.rectangle((16, 28, 32, 38), fill=cardi)
d.rectangle((21, 28, 27, 38), fill=shirt)
d.line((21, 28, 21, 38), fill=cardi_sh)
d.line((27, 28, 27, 38), fill=cardi_sh)
d.point((24, 29), fill=skin_sh)
# Brazos
d.rectangle((13, 29, 16, 37), fill=cardi)
d.rectangle((32, 29, 35, 37), fill=cardi)
d.line((13, 36, 16, 36), fill=cardi_sh)
d.line((32, 36, 35, 36), fill=cardi_sh)
# Manos
d.rectangle((13, 37, 16, 39), fill=skin)
d.rectangle((32, 37, 35, 39), fill=skin)
# Carnet de TI con cordón
d.line((22, 29, 23, 31), fill=badge)
d.line((26, 29, 25, 31), fill=badge)
d.rectangle((23, 32, 25, 35), fill=badge)
d.point((24, 33), fill=outline)

# Pantalón y zapatos
d.rectangle((18, 38, 30, 44), fill=pants)
d.line((24, 40, 24, 44), fill=(30, 34, 60, 255))
d.rectangle((17, 44, 23, 46), fill=shoes)
d.rectangle((25, 44, 31, 46), fill=shoes)

# Contorno oscuro de 1px
px = img.load()
out = img.copy()
po = out.load()
for y in range(48):
    for x in range(48):
        if px[x, y][3] == 0:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < 48 and 0 <= ny < 48 and px[nx, ny][3] > 0:
                    po[x, y] = outline
                    break

out.save("../sprites/avatar_48.png")
big = out.resize((480, 480), Image.NEAREST)
big.save("../sprites/avatar_480.png")

# versión con fondo oscuro tipo galería
bg = Image.new("RGBA", (480, 480), (14, 14, 16, 255))
bg.alpha_composite(big)
bg.save("../sprites/avatar_480_fondo.png")
print("ok")
