import random, os, math, time, asyncio, json
from PIL import Image

def menu():
    while True:
        os.system("CLS")
        settings = json.load(open("settings.json"))
        select = input("MENU\n\n0 \\ Exit\n1 \\ Start\n2 \\ Settings\n>>> ")
        if select == "0": return
        elif select == "1": imageAI(settings)
        elif select == "2": settin(settings)
        else: input("no lol\n")


def settin(settings):
    while True:
        json.dump(settings, open("settings.json", "w"))
        os.system("CLS")
        select = input("SETTINGS\n\nSettings are auto-saved as they are changed!\n0 \\ Back\n1 \\ Set Accuracy\n2 \\ Set Chunk Size\n3 \\ Set Gen Style\n4 \\ \"Cheats\"\n>>> ")
        if select == "0": return
        elif select == "1":
            while True:
                try: settings["accuracy"] = int(input("Enter a number to set the accuracy to.\nReccomended is 25 for a decent image, reccomended min is 10, reccomended max is 50\nLower is more accurate, higher is less accurate\n>>> ")); settings["accuracy"] = settings["accuracy"] if settings["accuracy"] > 0 else 25; break
                except: pass
        elif select == "2":
            while True:
                try:
                    settings["chunkSize"] = int(input("Enter a number to set the chunk size to.\nReccomended is 15 for a decent image, reccomended min is 5, there is no max, go wild!\n>>> "))
                    settings["chunkSize"] = settings["chunkSize"] if settings["chunkSize"] > 0 else 25
                    settings["cheatyShit"]['autoSmooth'] = settings["cheatyShit"]['autoSmooth'] if settings["cheatyShit"]['autoSmooth'] > settings["chunkSize"] else settings["chunkSize"]; break
                except: pass
        elif select == "3":
            while True:
                os.system("CLS")
                choice = int(input("Choose a generation type:\n0 \\ Back\n1 \\ \"DEC\" decimal\n2 \\ \"HEX\" hexadecimal\n>>> "))
                if choice == 0: break
                elif choice == 1: settings["genType"] = "DEC"
                elif choice == 2: settings["genType"] = "HEX"
                else: input("no lol\n")
        elif select == "4":
            while True:
                os.system("CLS")
                select = input("CHEATS\n\n0 \\ Back\n1 \\ Set Auto Smooth\n>>> ")
                if select == "0": return
                elif select == "1":
                    while True:
                        try:
                            settings["cheatyShit"]['autoSmooth'] = int(input("Enter a number to set the auto smooth to.\n>>> "))
                            settings["cheatyShit"]['autoSmooth'] = settings["cheatyShit"]['autoSmooth'] if settings["cheatyShit"]['autoSmooth'] > 0 else 1
                            settings["cheatyShit"]['autoSmooth'] = settings["cheatyShit"]['autoSmooth'] if settings["cheatyShit"]['autoSmooth'] > settings["chunkSize"] else settings["chunkSize"]; break
                        except: pass

def imageAI(settings):
    gen = 1
    file = input("Choose a .png image to replicate.\n>>> ")
    try: base = Image.open(file+".png")
    except: input("That image isn't real, stupid fuck.\n"); return
    full = Image.new("RGB", (base.width, base.height), "white")
    full.save("{}.AI.png".format(file))

    try: os.mkdir("temp")
    except: pass
    try: os.mkdir("chunks")
    except: pass
    for file1 in os.listdir("chunks"): os.remove("chunks/" + file1)
    for file1 in os.listdir("temp"): os.remove("temp/" + file1)

    CSizeX = round(base.width/settings['chunkSize'])
    CSizeY = round(base.height/settings['chunkSize'])
    for y in range(CSizeY):
        for x in range(CSizeX):
            xx = math.floor(base.width/CSizeX)+(math.floor(base.width/CSizeX)*x) if x != CSizeX-1 else base.width
            yy = math.floor(base.height/CSizeY)+(math.floor(base.height/CSizeY)*y) if y != CSizeY-1 else base.height
            position = (math.floor(base.width/CSizeX)*x, math.floor(base.height/CSizeY)*y, xx, yy)
            chunk = base.crop(position)
            chunk.save("chunks/{}_{}.png".format(str(x), str(y)))
            if x == 0 and y == 0: dimensions = (chunk.width, chunk.height)

    startTimeOverall = time.time()
    asyncio.get_event_loop().run_until_complete(main(base, gen, full, file, dimensions, settings, CSizeX, CSizeY))

    ms = int(round(time.time()-startTimeOverall, 2)*100)
    seconds = 0; minutes = 0; hours = 0; days = 0
    while ms >= 100: ms -= 100; seconds += 1
    while seconds >= 60: seconds -= 60; minutes += 1
    while minutes >= 60: minutes -= 60; hours += 1
    while hours >= 24: hours -= 24; days += 1
    input("\n\nFinished in {}d, {}h, {}:{}.{}\nPress enter to exit.\n".format(days, hours, minutes, seconds, ms))

async def test(base, Acolours, gen, prevScore):
    global blocks
    object = {}
    score = 0

    img = Image.open("temp/canvas.png")

    maxScale = base.width if base.width > base.height else base.height
    scaleX = random.randint(1, maxScale)
    scaleY = random.randint(1, maxScale)
    x = random.randint(0-scaleX, base.width)
    y = random.randint(0-scaleY, base.height)
    rgb = random.randint(0, len(Acolours)-1)
    r = int(Acolours[rgb].split(".")[0])
    g = int(Acolours[rgb].split(".")[1])
    b = int(Acolours[rgb].split(".")[2])
    a = random.randint(0, 255)
    rot = random.randint(0, 360)

    rect = Image.new("RGBA", (scaleX, scaleY), (r, g, b, a)).rotate(rot, expand=True)
    Image.Image.paste(img, rect, (x, y), rect)
    while True:
        try: img.save("temp/temp.png"); break
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

async def main(base, gen, full, file, dimensions, settings, CSizeX, CSizeY):
    os.system("CLS")
    avg = 0
    avgcount= 0
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
                try: base.resize((settings['cheatyShit']['autoSmooth'], settings['cheatyShit']['autoSmooth'])).resize((base.width, base.height), resample=Image.BICUBIC).save("temp/canvas.png"); break
                except: pass
            prevScore = math.inf
            score = math.inf
            goal = base.width*base.height*settings['accuracy']
            
            while score > goal:
                objects = []

                objects.append(await test(base, Acolours, gen, prevScore))

                sortObj = []
                for y in range(len(objects)):
                    for x in range(len(objects)):
                        if x == 0: minimum = x
                        else:
                            if objects[x]['score'] < objects[minimum]['score']: minimum = x
                    sortObj.append(objects.pop(minimum))
                objects = sortObj

                comp = Image.open("temp/temp.png")

                score = 0
                count = 0
                for y in range(base.height):
                    for x in range(base.width):
                        BaseCol = base.getpixel((x, y))
                        CompCol = comp.getpixel((x, y))

                        count += 1

                        for col in range(3):
                            if BaseCol[col] - CompCol[col] < 0: score += -(BaseCol[col] - CompCol[col])
                            else: score += BaseCol[col] - CompCol[col]

                rg = [round(255-(255/(count*100)*score)), round(255/(count*100)*score)]
                if rg[0] > 255: rg[0] = 255
                if rg[0] < 0: rg[0] = 0
                if rg[1] > 255: rg[1] = 255
                if rg[1] < 0: rg[1] = 0

                if score < prevScore:
                    avg = ((avg*avgcount)+(time.time()-startTime))/(avgcount+1)
                    avgcount += 1
                    print( # Needs "/033A"s equivelent to 1 less than the number of lines printed
                        "\033A\033A\033A\033A\033A"+
                          "NAME  | "+file+
                        "\nGEN   | "+(str(hex(gen))[2:] if settings['genType'] == "HEX" else str(gen))+
                        "\nSCORE | \033[48;2;"+str(rg[1])+";"+str(rg[0])+";0m"+str(score)+"\033[0m -> "+str(goal)+"    "+
                        "\nCHUNK | "+str(cx+1)+", "+str(cy+1)+
                        "\nTIME  | "+str(round(time.time()-startTime, 5))+"s    "+
                        "\nAVG   | "+str(round(avg, 5))+"s    "
                        , end="\r")
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

menu()