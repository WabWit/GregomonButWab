# CONFIG
DIR = "C:/wtg-testing"
TOKEN = ""
import discord # type: ignore
import random, asyncio, shutil, json, typing, math, time, hints, cleaner
from discord.ext import commands # type: ignore 
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

REPLACES = {}
UPPER = {}
USER_SCORE= {}
ALLOWEDUSERS = []
ALLOWEDROLES = []
QUITLIST = []
IMAGESET = []
REDUCEPROBLIST = []
SUBCOMMANDS ={}
user_attempts = {}
TIME = 0

def load_data():
    global REPLACES, UPPER, QUITLIST, IMAGESET, USER_SCORE, ALLOWEDUSERS, ALLOWEDROLES, REDUCEPROBLIST, SUBCOMMANDS
    with open(f"{DIR}/replaces.json", "r") as file:
        REPLACES = json.load(file)
    with open(f"{DIR}/upper.json", "r") as file:
        UPPER = json.load(file)
    with open(f"{DIR}/quitlist.txt", "r") as file:
        QUITLIST = [line.strip() for line in file]
    with open(f"{DIR}/reduceproblist.txt", "r") as file:
        REDUCEPROBLIST = [line.strip() for line in file]
    with open(f"{DIR}/imagelist.txt", "r") as file:
        IMAGESET = [line.strip() for line in file]
    with open(f"{DIR}/userscore.json", "r") as file:
        USER_SCORE = json.load(file)
    with open(f"{DIR}/allowedusers.txt", "r") as file:
        ALLOWEDUSERS = [line.strip() for line in file]
    with open(f"{DIR}/allowedroles.txt", "r") as file:
        ALLOWEDROLES = [line.strip() for line in file]
    with open(f"{DIR}/subcommands.json", "r") as file:
        SUBCOMMANDS = json.load(file)
load_data()

skiplist = []

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")

    print(f'Time to greg, {bot.user}')


async def sendImage(target, msgCont):
    global image, item, itemAnswerList, totalGuesses, user_attempts, TIME, allAnswerFoundList, skiplist
    totalGuesses = 0

    user_attempts = {}
    allAnswerFoundList = []
    skiplist = []

    item = random.choice(IMAGESET)
    for k in REDUCEPROBLIST:
        if k in item:
            print(item)
            print("Image re-rolled.")
            item = random.choice(IMAGESET)
    TIME = int(time.time())
    print(TIME)
    image = f"{DIR}/imagelist/{item}"
    print(image)
    rimage = shutil.copyfile(f"{DIR}/imagelist/{item}",f"{DIR}/item.png")

    item = cleaner.cleanInput(item)
    item = item.replace("gtceum_","").replace(".png","").replace("_"," ")
    itemAnswerList=item.split()

    file = discord.File(rimage) 

    if target.response.is_done(): 
        await target.followup.send(msgCont, file=file)
    else:
        await target.response.send_message(msgCont, file=file)

@bot.tree.command(name="skip", description="Skips the current image if it's been 5 minutes since it was sent. Requires 2 people to skip.")
async def skip(interaction: discord.Interaction):
    global TIME, user_attempts, item, skiplist
    processed=""
    if TIME+1800 <= int(time.time()):
        await interaction.response.send_message(f"The answer was:\n{cleaner.uppervolt(item.title())}")
        await sendImage(interaction, "")
    elif TIME+300 <= int(time.time()):
        if interaction.user.id not in skiplist:
            try:
                if not user_attempts[str(interaction.user.id)] == 3:
                    await interaction.response.send_message("You have to have used all 3 guesses to /skip.",ephemeral=True)
                else:
                    skiplist.append(interaction.user.id)
                    processed=f"Skip processed. {len(skiplist)}/2.\n"
                    if len(skiplist) == 2:
                        await interaction.response.send_message(f"{processed}The answer was:\n{cleaner.uppervolt(item.title())}")
                        skiplist = []
                        await sendImage(interaction, "")
                    else:
                        await interaction.response.send_message(f"{processed}\n")
            except:
                await interaction.response.send_message("You have to have used all 3 guesses to /skip.",ephemeral=True)
        else:
            await interaction.response.send_message("You've already used /skip for this image! Try again after 30 minutes since the image was sent.", ephemeral=True)
    else:
        await interaction.response.send_message("It hasn't been 10 minutes yet!", ephemeral=True)

@bot.tree.command(name="info", description="Help and changelogs.")
async def info(interaction: discord.Interaction, sub: typing.Optional[str]):
    if sub==None:
        embed=discord.Embed(title="Available Subcommands", description=str(list(SUBCOMMANDS.keys())))
    else:
        try:
            embed=discord.Embed(title=sub.title(), description=SUBCOMMANDS[sub])
        except:
            await interaction.response.send_message("Invalid subcommand.", ephemeral=True)
            return
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="quit", description="**Admin Only.** Kills the bot.")
async def quit_bot(ctx: discord.Interaction):
    print(ctx.user.roles)
    print(ctx.user.id)
    if (str(ctx.user.id) in ALLOWEDUSERS) or (discord.utils.find(lambda r: str(r.id) in ALLOWEDROLES, ctx.user.roles)):
        await ctx.response.send_message("o7")
        await quit()
    else:
        await ctx.response.send_message(random.choice(QUITLIST))

async def processMessage(source, content_lower, user_id):
    global totalGuesses, answerFoundList, user_attempts, allAnswerFoundList, item
    response_method = source.followup.send
    responseList = cleaner.cleanInput(content_lower).split()
    answerFoundList = []
    answerWrong = 0
    totalGuesses+=1
    for word in responseList:
        if word in itemAnswerList:
            answerFoundList.append(word)
        else:
            answerWrong = 1

    itemAnswerList.sort()
    answerFoundList.sort()

    if answerFoundList == itemAnswerList and answerWrong != 1:
        await sendImage(source, f"'{cleaner.uppervolt(item.title())}' is correct!\nMoving onto the next image...")
        if user_id not in USER_SCORE:
           USER_SCORE[user_id] = 0
        USER_SCORE[user_id]+=1
        with open(f"{DIR}/userscore.json", "w") as file:
            json.dump(USER_SCORE, file)
        user_attempts = {}
    else:
        if user_id not in user_attempts:
            user_attempts[user_id] = 0
        hint=""
        user_attempts[user_id] += 1
        guessLeft=""
        if user_attempts[user_id] == 2:
            guessLeft="You have one guess left.\n"
        if user_attempts[user_id] == 3:
            guessLeft="You've run out of guesses.\n"
        for i in answerFoundList:
            allAnswerFoundList.append(i)
        if totalGuesses == 10:
            possible_hints = []
            randomWord = True
            # Checks to see if there is an available hint for item
            HintFromChecker = hints.HintChecker(item)
            if HintFromChecker[0] == "false":
                randomWord = True
                possible_hints = [x for x in itemAnswerList if x not in allAnswerFoundList]
            else:
                randomWord = False
                possible_hints = HintFromChecker
            print(allAnswerFoundList)
            print(possible_hints)
            if not possible_hints:
                hint = "\n10 incorrect Guesses, huh? Heres a hint.\nAll of the words in the item name have been found already."
            else:
                if randomWord:            
                    hint = f"\n10 incorrect Guesses, huh? Heres a hint.\nOne of the words in the item name is: {random.choice(possible_hints)}"
                else:
                    hint = f"\n10 incorrect Guesses, huh? Heres a hint.\nIt is associated with: {random.choice(possible_hints)}"
        if not answerFoundList:
            await response_method(f"Nope! {guessLeft}{hint}")
        else:
            await response_method(f"Not Quite! {guessLeft}Correct words: {answerFoundList}{hint}")

    await asyncio.to_thread(print, user_attempts)

@bot.tree.command(name="image", description="**Admin Only.** Sends a new image.")
async def image(interaction: discord.Interaction):
    if (str(interaction.user.id) in ALLOWEDUSERS) or (discord.utils.find(lambda r: str(r.id) in ALLOWEDROLES, interaction.user.roles)):
        await interaction.response.defer()
        await sendImage(interaction, "")
    else:
        await interaction.response.send_message("Permission denied.", ephemeral=True)
    return

@bot.tree.command(name="answer", description="Lets you answer")
async def answer_1(interaction: discord.Interaction, answer: str,):
    await answer_r(interaction, answer)

@bot.tree.command(name="a", description="Lets you answer")
async def answer_2(interaction: discord.Interaction, answer: str,):
    await answer_r(interaction, answer)

async def answer_r(interaction, user_input):
    global user_attempts
    await interaction.response.defer(ephemeral=False)
    user_id = str(interaction.user.id)
    content_lower = user_input.lower()

    if user_attempts.get(user_id, 0) < 3:
        if len(content_lower) > 75:
            await interaction.followup.send("Guess is longer than max length of 75 characters.")
        else:
            await processMessage(interaction, content_lower, user_id)
    else:
        await interaction.followup.send("You've used all your guesses!")

@bot.tree.command(name="reset", description="**Admin Only.** Reset guesses for user.")
async def resetGuesses(ctx: discord.Interaction):
    global user_attempts
    if (str(ctx.user.id) in ALLOWEDUSERS) or (discord.utils.find(lambda r: str(r.id) in ALLOWEDROLES, ctx.user.roles)):
        user_attempts.pop(str(ctx.user.id), None)
        await ctx.response.send_message(f"{ctx.user.mention}, Guesses reset.", ephemeral=True)
    else:
        await ctx.response.send_message("Permission denied.", ephemeral=True)
        return

@bot.tree.command(name="reveal", description="**Admin Only.** Reveals the name of the latest image")
async def reveal(interaction: discord.Interaction):
    if (str(interaction.user.id) in ALLOWEDUSERS) or (discord.utils.find(lambda r: str(r.id) in ALLOWEDROLES, interaction.user.roles)):
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send(f"The answer was:\n{cleaner.uppervolt(item.title())}")
        await sendImage(interaction, "")
    else:
        await interaction.response.send_message("Permission denied.", ephemeral=True)
    return

@bot.tree.command(name="reload", description="**Admin Only.** Reloads important dictionaries and lists.")
async def reload(interaction: discord.Interaction):
    if (str(interaction.user.id) in ALLOWEDUSERS) or (discord.utils.find(lambda r: str(r.id) in ALLOWEDROLES, interaction.user.roles)):
        load_data()
        await interaction.response.send_message(f"Dictionaries and lists reloaded!")
    else:
        await interaction.response.send_message("Permission denied.", ephemeral=True)
    return

@bot.tree.command(name="score", description="Shows the top scores, can select pages.")
async def scorepg(interaction: discord.Interaction, page: typing.Optional[int]):
    global USER_SCORE, klist, vlist
    if not page:
        page = 1
    if page > int(math.ceil((len(USER_SCORE)/10))) or page < 1:
        await interaction.response.send_message(f"Invalid page! Must be between 1 and {int(math.ceil((len(USER_SCORE)/10)))}.")
    else:
        user_id = str(interaction.user.id)
        if user_id not in USER_SCORE:
               USER_SCORE[user_id] = 0
        with open(f"{DIR}/userscore.json", "w") as file:
            json.dump(USER_SCORE, file)
        klist = []
        vlist = []
        sorted_user_score = sorted(USER_SCORE.items(), key=lambda x: x[1], reverse=True)
        for k, v in sorted_user_score:
            klist.append(k)
            vlist.append(v)

        descbuilder = ""
        for i in range(10):
            pos2=i+(10*(page-1))
            try:
                descbuilder=descbuilder+(f"{str(pos2+1)}. <@{int(klist[pos2])}>: {vlist[pos2]}\n")
            except: pass

        embed = discord.Embed(title=f"Page {page} of {int(math.ceil((len(USER_SCORE)/10)))}", description=descbuilder)
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userscore", description="Shows a specific user's score.")
async def userscore(interaction: discord.Interaction, user: typing.Optional[discord.User]):
    global klist, vlist
    
    if user == None:
        user = interaction.user
    user_id = str(user.id)
    if user_id not in USER_SCORE:
           USER_SCORE[user_id] = 0
    with open(f"{DIR}/userscore.json", "w") as file:
        json.dump(USER_SCORE, file)
    klist = []
    vlist = []
    sorted_user_score = sorted(USER_SCORE.items(), key=lambda x: x[1], reverse=True)
    for k, v in sorted_user_score:
        klist.append(k)
        vlist.append(v)

    descbuilder = ""
    pos=klist.index(user_id)
    for i in range(10):
        pos2 = pos+i-5
        if pos2<0: pass
        else:
            try:
                descbuilder=descbuilder+(f"{str(pos2+1)}. <@{int(klist[pos2])}>: {vlist[pos2]}\n")
            except: pass
        i+=1
    embed = discord.Embed(title=f"{user.name}'s score", color=0x222222, description=descbuilder)

    await interaction.response.send_message(embed=embed)
    
bot.run(TOKEN)
