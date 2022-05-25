import random
from PIL import Image, ImageDraw
import os

prevScore = 999*999*999*999*999*999*999*999*999*999*999*999*999*999*999*999*999*999*999*999
score = 10001
gen = 0
iteration = 1

base = Image.open(input(">>> ") + ".png")

Acolours = []
for y in range(base.height):
    for x in range(base.width):
        BaseCol = base.getpixel((x, y))

        if str(BaseCol[0]) + "." + str(BaseCol[1]) + "." + str(BaseCol[2]) in Acolours: continue
        Acolours.append(str(BaseCol[0]) + "." + str(BaseCol[1]) + "." + str(BaseCol[2]))

for file in os.listdir("image_temp"): os.remove("image_temp/" + file)

img = Image.new("RGB", (base.width, base.height), "white")
img.save("image_temp/canvas.png")

while score > 10000:
    objects = []
    gen += 1
    for i in range(iteration):
        object = {}
        object["id"] = i

        x = random.randint(0, base.width)
        y = random.randint(0, base.height)
        scaleX = random.randint(-500, 500)
        scaleY = random.randint(-500, 500)
        rgb = random.randint(0, len(Acolours)-1)
        r = int(Acolours[rgb].split(".")[0])
        g = int(Acolours[rgb].split(".")[1])
        b = int(Acolours[rgb].split(".")[2])
        a = random.randint(0, 255)

        img = Image.open("image_temp/canvas.png")
        draw=ImageDraw.Draw(img, "RGBA")
        draw.rectangle([(x, y), (x+scaleX, y+scaleY)], fill=(r, g, b, a))
        img.save("image_temp/" + str(i) + ".png")

        img = img.resize((round(img.width/4), round(img.height/4)))

        score = 0
        basetemp = base.resize((round(base.width/4), round(base.height/4)))
        for yy in range(img.height):
            for xx in range(img.width):
                BaseCol = basetemp.getpixel((xx, yy))
                CompCol = img.getpixel((xx, yy))

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
        print("["+"#"*(round((i+1)/iteration*50))+" "*(50-(round((i+1)/iteration*50)))+"] "+str(i+1)+"/" + str(iteration) + " // GEN "+str(gen), end="\r")

    sortObj = []
    for y in range(len(objects)):
        for x in range(len(objects)):
            if x == 0: minimum = x
            else:
                if objects[x]['score'] < objects[minimum]['score']: minimum = x
        sortObj.append(objects.pop(minimum))
    objects = sortObj

    print("["+"#"*50+"] "+str(iteration)+"/" + str(iteration) + " // GEN "+str(gen)+" // BEST SCORE: "+str(objects[0]['score']), end="\r")

    comp = Image.open("image_temp/" + str(objects[0]['id']) + ".png")

    score = 0
    s = -1
    for y in range(comp.height):
        s += 1
        if s == 4: s = 0
        for x in range(comp.width):
            BaseCol = base.getpixel((x, y))
            CompCol = comp.getpixel((x, y))

            for col in range(3):
                if BaseCol[col] - CompCol[col] < 0: score += -(BaseCol[col] - CompCol[col])
                else: score += BaseCol[col] - CompCol[col]

    if score < prevScore:
        print("")
        comp.save("image_temp/canvas.png")
        comp = Image.open("image_temp/canvas.png")
        prevScore = score
    else:
        print("["+"#"*50+"] "+str(iteration)+"/" + str(iteration) + " // GEN "+str(gen)+" // FAILED GEN: COULD NOT IMPROVE UPON PEVIOUS GEN")
        iteration += 1