from PIL import Image, ImageDraw

SP = "../sprites/"

# Paleta con rampas: luz arriba-izquierda (tono cálido), sombra abajo-derecha (tono violeta)
skin = (238, 188, 154, 255)
skin_sh = (200, 140, 136, 255)
blush = (236, 128, 140, 255)
hair = (110, 58, 42, 255)
hair_sh = (66, 34, 50, 255)
hair_hi = (164, 96, 62, 255)
blouse = (222, 86, 112, 255)
blouse_sh = (156, 54, 100, 255)
blouse_hi = (246, 140, 140, 255)
skirt = (52, 58, 104, 255)
skirt_sh = (36, 36, 80, 255)
shoes = (120, 36, 64, 255)
lips = (192, 58, 86, 255)
white = (255, 255, 255, 255)
eye = (46, 28, 40, 255)
earring = (246, 204, 92, 255)

img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# pelo largo detrás (va primero para que la cara quede encima)
d.rectangle((16, 9, 32, 31), fill=hair)
d.rectangle((30, 12, 32, 31), fill=hair_sh)
d.rectangle((16, 30, 17, 31), fill=hair_sh)
d.point((16, 9), fill=(0, 0, 0, 0))
d.point((32, 9), fill=(0, 0, 0, 0))
# cabeza
d.rectangle((18, 11, 30, 24), fill=skin)
d.point((18, 24), fill=hair)
d.point((30, 24), fill=hair_sh)
d.rectangle((30, 14, 30, 23), fill=skin_sh)
# flequillo y coronilla
d.rectangle((17, 7, 31, 11), fill=hair)
d.rectangle((19, 6, 29, 6), fill=hair)
d.rectangle((18, 12, 22, 12), fill=hair)
d.rectangle((25, 12, 30, 13), fill=hair)
d.line((19, 8, 23, 7), fill=hair_hi)
d.line((18, 10, 19, 9), fill=hair_hi)
d.rectangle((28, 8, 31, 11), fill=hair_sh)
# ojos grandes con pestañas
d.rectangle((20, 16, 21, 18), fill=eye)
d.rectangle((27, 16, 28, 18), fill=eye)
d.point((20, 16), fill=white)  # brillo del ojo
d.point((27, 16), fill=white)
d.point((19, 15), fill=eye)  # pestañas
d.point((29, 15), fill=eye)
# mejillas, nariz y sonrisa
d.point((19, 20), fill=blush)
d.point((29, 20), fill=blush)
d.point((24, 20), fill=skin_sh)
d.line((23, 22, 25, 22), fill=lips)
d.point((22, 21), fill=lips)
d.point((26, 21), fill=lips)
# aretes
d.point((17, 20), fill=earring)
d.point((31, 20), fill=earring)
# cuello
d.rectangle((22, 25, 26, 26), fill=skin_sh)

# blusa con cintura
d.rectangle((16, 27, 31, 33), fill=blouse)
d.rectangle((18, 34, 29, 36), fill=blouse)
d.rectangle((28, 28, 31, 33), fill=blouse_sh)
d.rectangle((27, 34, 29, 36), fill=blouse_sh)
d.line((17, 27, 20, 27), fill=blouse_hi)
d.point((17, 28), fill=blouse_hi)
d.polygon([(22, 27), (24, 29), (26, 27)], fill=skin)  # escote en V
# brazos y manos
d.rectangle((13, 28, 15, 35), fill=blouse)
d.rectangle((32, 28, 34, 35), fill=blouse_sh)
d.point((13, 28), fill=blouse_hi)
d.rectangle((13, 36, 15, 37), fill=skin)
d.rectangle((32, 36, 34, 37), fill=skin_sh)
# falda acampanada
d.polygon([(18, 37), (29, 37), (31, 42), (16, 42)], fill=skirt)
d.polygon([(26, 37), (29, 37), (31, 42), (27, 42)], fill=skirt_sh)
# piernas y zapatos
d.rectangle((19, 43, 21, 44), fill=skin)
d.rectangle((26, 43, 28, 44), fill=skin_sh)
d.rectangle((18, 45, 22, 46), fill=shoes)
d.rectangle((25, 45, 29, 46), fill=shoes)


def outline_of(c):
    # contorno de color: el vecino oscurecido y corrido hacia el violeta, nunca negro puro
    r, g, b, _ = c
    return (int(r * 0.30) + 8, int(g * 0.22) + 4, int(b * 0.32) + 18, 255)


px = img.load()
out = img.copy()
po = out.load()
for y in range(48):
    for x in range(48):
        if px[x, y][3] == 0:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < 48 and 0 <= ny < 48 and px[nx, ny][3] > 0:
                    po[x, y] = outline_of(px[nx, ny])
                    break
out.save(SP + "companera_48.png")
bg = Image.new("RGBA", (384, 384), (14, 14, 16, 255))
bg.alpha_composite(out.resize((384, 384), Image.NEAREST))
bg.save(SP + "companera_preview.png")
print("ok")
