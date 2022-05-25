import time
import random
from PIL import Image, ImageDraw
import os
from math import floor

prevScore = 999*999*999*999*999*999*999*999*999*999*999*999*999*999*999*999*999*999*999*999
score = 10001
gen = 0

shapes = os.listdir("shapes")

base = Image.open("base.png")

for file in os.listdir("image_temp"): os.remove("image_temp/" + file)

img = Image.new("RGB", (base.width, base.height), "white")
img.save("image_temp/canvas.png")

while score > 10000:
    objects = []
    gen += 1
    for i in range(50):
        object = {}
        object["id"] = i

        x = random.randint(0, base.width)
        y = random.randint(0, base.height)
        scaleX = random.randint(-500, 500)
        scaleY = random.randint(-500, 500)
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        a = random.randint(0, 255)

        img = Image.open("image_temp/canvas.png")
        draw=ImageDraw.Draw(img, "RGBA")
        draw.rectangle([(x, y), (x+scaleX, y+scaleY)], fill=(r, g, b, a))
        img.save("image_temp/" + str(i) + ".png")

        score = 0
        s = -1
        for y in range(floor(round(img.height))):
            s += 1
            if s == 4: s = 0
            for x in range(floor(round(img.width/4))):
                BaseCol = base.getpixel(((x*4)+s, y))
                CompCol = img.getpixel(((x*4)+s, y))

                for col in range(3):
                    if BaseCol[col] - CompCol[col] < 0: score += -(BaseCol[col] - CompCol[col])
                    else: score += BaseCol[col] - CompCol[col]

        object["score"] = score
        object["x"] = x
        object["y"] = y
        object["scaleX"] = scaleX
        object["scaleY"] = scaleY
        object["r"] = r
        object["g"] = g
        object["b"] = b
        object["a"] = a

        objects.append(object)
        print("["+"#"*(i+1)+" "*(50-(i+1))+"] "+str(i+1)+"/50 // GEN "+str(gen), end="\r")

    sortObj = []
    for y in range(len(objects)):
        for x in range(len(objects)):
            if x == 0: minimum = x
            else:
                if objects[x]['score'] < objects[minimum]['score']: minimum = x
        sortObj.append(objects.pop(minimum))
    objects = sortObj

    if objects[0]['score'] > prevScore:
        print("["+"#"*(i+1)+" "*(50-(i+1))+"] "+str(i+1)+"/50 // GEN "+str(gen)+" // FAILED GEN: COULD NOT IMPROVE UPON PEVIOUS GEN")
        continue

    print("["+"#"*(i+1)+" "*(50-(i+1))+"] "+str(i+1)+"/50 // GEN "+str(gen)+" // BEST SCORE: "+str(objects[0]['score']))

    comp = Image.open("image_temp/" + str(objects[0]['id']) + ".png")
    comp.save("image_temp/canvas.png")
    comp = Image.open("image_temp/canvas.png")

    score = 0
    s = -1
    for y in range(floor(round(img.height))):
        s += 1
        if s == 4: s = 0
        for x in range(floor(round(img.width/4))):
            BaseCol = base.getpixel(((x*4)+s, y))
            CompCol = img.getpixel(((x*4)+s, y))

            for col in range(3):
                if BaseCol[col] - CompCol[col] < 0: score += -(BaseCol[col] - CompCol[col])
                else: score += BaseCol[col] - CompCol[col]
    prevScore = score