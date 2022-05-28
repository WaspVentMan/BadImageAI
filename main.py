import random, os, math, time, asyncio
from PIL import Image

blocks = ("▏", "▎", "▍", "▌", "▋", "▊", "▉", "█")

prevScore = math.inf
score = math.inf
gen = 1
iteration = 50
itChoice = ""
while itChoice not in ['y', 'n']: itChoice = input("Do you want to change the minimum iterations per generation? Default is {} (y/n)\n>>> ".format(str(iteration))).lower()
if itChoice == "y":
    while True:
        try: iteration = int(input("Enter a number (reccomended minimum is 50)\n>>> ")); iteration = iteration if iteration > 0 else 50; break
        except: pass

file = input("Choose an image to replicate.\n>>> ")
base = Image.open(file + ".png")

try: os.mkdir("temp")
except: pass
try: os.mkdir("progress")
except: pass
for file in os.listdir("progress"): os.remove("progress/" + file)

Acolours = []
for y in range(base.height):
    for x in range(base.width):
        BaseCol = base.getpixel((x, y))

        if str(BaseCol[0]) + "." + str(BaseCol[1]) + "." + str(BaseCol[2]) in Acolours: continue
        Acolours.append(str(BaseCol[0]) + "." + str(BaseCol[1]) + "." + str(BaseCol[2]))

for file in os.listdir("temp"): os.remove("temp/" + file)

img = Image.new("RGB", (base.width, base.height), "white") .save("temp/canvas.png")

async def test(i, base, Acolours, gen, startTime):
    global blocks
    object = {"id": i}
    score = 0

    maxScale = base.width if base.width > base.height else base.height
    maxScale = maxScale-(round(gen/5)) if maxScale-(round(gen/5)) > 25 else 25
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
    img.save("temp/" + str(i) + ".png")

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

    object["rgb"] = rgb
    object["score"] = score

    rgb = Acolours[rgb].split(".")[0] + ";" + Acolours[rgb].split(".")[1] + ";" + Acolours[rgb].split(".")[2]
    bar = "[" + "\033[38;2;" + rgb + "m"
    bi=round(i*(400/iteration))
    for b in range(50):
        b=b*8
        if b > bi:
            if b-8 > bi: bar += " "
            else: bar += blocks[bi-(b-8)]
        else: bar += blocks[7]
    bar += "\033[0m] {}/{} // GEN {} // TIME: {}s".format(str(i+1), str(iteration), str(gen), str(round(time.time()-startTime, 2)))
    print(bar + " "*(int(os.get_terminal_size()[0])-len(bar)), end="\r")

    return object

async def main(base, iteration, Acolours, score, prevScore, gen):
    startTime = time.time()
    while score > base.width*base.height*10:
        objects = []

        for i in range(iteration): objects.append(await test(i, base, Acolours, gen, startTime))

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
        for y in range(comp.height):
            for x in range(comp.width):
                BaseCol = base.getpixel((x, y))
                CompCol = comp.getpixel((x, y))

                for col in range(3):
                    if BaseCol[col] - CompCol[col] < 0: score += -(BaseCol[col] - CompCol[col])
                    else: score += BaseCol[col] - CompCol[col]

        if score < prevScore:
            rgb = Acolours[objects[0]['rgb']].split(".")[0] + ";" + Acolours[objects[0]['rgb']].split(".")[1] + ";" + Acolours[objects[0]['rgb']].split(".")[2]
            bar = "["+"\033[38;2;" + rgb + "m" + "█"*50+"\033[0m] "+str(iteration)+"/" + str(iteration) + " // GEN "+str(gen)+" // SCORE: "+str(score)+" // TIME: "+str(round(time.time()-startTime, 2))+"s"
            print("{}{}".format(bar, " "*(int(os.get_terminal_size()[0])-len(bar))))
            comp.save("temp/canvas.png")
            comp.save("progress/{}.png".format(str(gen)))
            gen += 1
            prevScore = score
            startTime = time.time()
    for file in os.listdir("temp"): os.remove("temp/" + file)
    comp.save("{}.AI.{}.png".format(file, str(gen)))

loop = asyncio.get_event_loop()
loop.run_until_complete(main(base, iteration, Acolours, score, prevScore, gen))