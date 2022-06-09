import random, os, math, time, asyncio
from PIL import Image

blocks = ("▏", "▎", "▍", "▌", "▋", "▊", "▉", "█")

gen = 1
iteration = 50
accuracy = 25
itChoice = ""
while itChoice not in ['y', 'n']: itChoice = input("Do you want to change the minimum iterations per generation? Default is {} (y/n)\n>>> ".format(str(iteration))).lower()
if itChoice == "y":
    while True:
        try: iteration = int(input("Enter a number (reccomended minimum is 50)\n>>> ")); iteration = iteration if iteration > 0 else 50; break
        except: pass

itChoice = ""
while itChoice not in ['y', 'n']: itChoice = input("Do you want to change the accuracy to succeed? Default is {} (y/n)\n>>> ".format(str(accuracy))).lower()
if itChoice == "y":
    while True:
        try: accuracy = int(input("Enter a number (reccomended min is 10, reccomended max is 50, lower is more accurate, higher is less accurate)\n>>> ")); accuracy = accuracy if accuracy > 0 else 25; break
        except: pass

file = input("Choose an image to replicate.\n>>> ")
base = Image.open(file + ".png")
full = Image.new("RGB", (base.width, base.height), "white")
full.save("{}.AI.png".format(file))

try: os.mkdir("temp")
except: pass
try: os.mkdir("chunks")
except: pass
for file1 in os.listdir("chunks"): os.remove("chunks/" + file1)
for file1 in os.listdir("temp"): os.remove("temp/" + file1)

CSizeX = round(base.width/15)
CSizeY = round(base.height/15)
if CSizeX > 100: CSizeX = 100
if CSizeY > 100: CSizeY = 100
for y in range(CSizeY):
    for x in range(CSizeX):
        xx = math.floor(base.width/CSizeX)+(math.floor(base.width/CSizeX)*x) if x != CSizeX-1 else base.width
        yy = math.floor(base.height/CSizeY)+(math.floor(base.height/CSizeY)*y) if y != CSizeY-1 else base.height
        position = (math.floor(base.width/CSizeX)*x, math.floor(base.height/CSizeY)*y, xx, yy)
        chunk = base.crop(position)
        chunk.save("chunks/{}_{}.png".format(str(x), str(y)))
        if x == 0 and y == 0: dimensions = (chunk.width, chunk.height)

async def test(i, base, Acolours, gen):
    global blocks
    object = {"id": i}
    score = 0

    maxScale = base.width if base.width > base.height else base.height
    scaleX = random.randint(1, maxScale)
    scaleY = random.randint(1, maxScale)
    x = random.randint(0-scaleX, base.width)
    y = random.randint(0-scaleY, base.height)
    rgb = random.randint(0, len(Acolours)-1)
    r = int(Acolours[rgb].split(".")[0])
    g = int(Acolours[rgb].split(".")[1])
    b = int(Acolours[rgb].split(".")[2])
    a = random.randint(128-gen if gen > 127 else 0, 255)
    rot = random.randint(0, 360)

    img = Image.open("temp/canvas.png")
    rect = Image.new("RGBA", (scaleX, scaleY), (r, g, b, a)).rotate(rot, expand=True)
    Image.Image.paste(img, rect, (x, y), rect)
    while True:
        try: img.save("temp/" + str(i) + ".png"); break
        except: pass

    score = 0
    for yy in range(img.height):
        for xx in range(img.width):
            try:
                BaseCol = base.getpixel((xx, yy))
                CompCol = img.getpixel((xx, yy))

                for col in range(3):
                    if BaseCol[col] - CompCol[col] < 0: score += -(BaseCol[col] - CompCol[col])
                    else: score += BaseCol[col] - CompCol[col]
            except: pass

    object["score"] = score

    return object

async def main(base, iteration, gen, full, file, dimensions):
    global CSizeX, CSizeY
    startTime = time.time()
    for cy in range(CSizeY):
        for cx in range(CSizeX):
            base = Image.open("chunks/{}_{}.png".format(str(cx), str(cy)))
            Acolours = []
            for y in range(base.height):
                for x in range(base.width):
                    BaseCol = base.getpixel((x, y))

                    if str(BaseCol[0]) + "." + str(BaseCol[1]) + "." + str(BaseCol[2]) in Acolours: pass
                    else: Acolours.append(str(BaseCol[0]) + "." + str(BaseCol[1]) + "." + str(BaseCol[2]))
            while True:
                try: base.resize((1, 1)).resize((base.width, base.height)).save("temp/canvas.png"); break
                except: pass
            prevScore = math.inf
            score = math.inf
            goal = base.width*base.height*accuracy
            while score > goal:
                objects = []

                for i in range(iteration):
                    objects.append(await test(i, base, Acolours, gen))

                sortObj = []
                for y in range(len(objects)):
                    for x in range(len(objects)):
                        if x == 0: minimum = x
                        else:
                            if objects[x]['score'] < objects[minimum]['score']: minimum = x
                    sortObj.append(objects.pop(minimum))
                objects = sortObj

                comp = Image.open("temp/" + str(objects[0]['id']) + ".png")

                score = 0
                for y in range(base.height):
                    for x in range(base.width):
                        BaseCol = base.getpixel((x, y))
                        CompCol = comp.getpixel((x, y))

                        for col in range(3):
                            if BaseCol[col] - CompCol[col] < 0: score += -(BaseCol[col] - CompCol[col])
                            else: score += BaseCol[col] - CompCol[col]

                print("GEN "+str(hex(gen))[2:]+" // SCORE: "+"-"*len(str(prevScore))+" // TIME: "+str(round(time.time()-startTime, 2))+"s   ", end="\r")
                if score < prevScore:
                    print("GEN "+str(hex(gen))[2:]+" // SCORE: "+str(score)+" // TIME: "+str(round(time.time()-startTime, 2))+"s   ")
                    position = (math.floor(dimensions[0])*cx, math.floor(dimensions[1])*cy)
                    full.paste(comp, position)
                    while True:
                        try:
                            full.save("{}.AI.png".format(file))
                            comp.save("temp/canvas.png")
                            break
                        except: pass
                    gen += 1
                    prevScore = score
                    startTime = time.time()
            position = (math.floor(dimensions[0])*cx, math.floor(dimensions[1])*cy)
            full.paste(comp, position)
            while True:
                try:
                    full.save("{}.AI.png".format(file))
                    comp.save("chunks/{}_{}.png".format(str(cx), str(cy)))
                    break
                except: pass
    for file1 in os.listdir("temp"): os.remove("temp/" + file1)
    for file1 in os.listdir("chunks"): os.remove("chunks/" + file1)

startTimeOverall = time.time()
asyncio.get_event_loop().run_until_complete(main(base, iteration, gen, full, file, dimensions))

ms = int(round(time.time()-startTimeOverall, 2)*100)
seconds = 0; minutes = 0; hours = 0; days = 0
while ms >= 100: ms -= 100; seconds += 1
while seconds >= 60: seconds -= 60; minutes += 1
while minutes >= 60: minutes -= 60; hours += 1
while hours >= 24: hours -= 24; days += 1
input("Finished in {}d {}h {}m {}s {}ms\nPress enter to exit.\n".format(days, hours, minutes, seconds, ms))