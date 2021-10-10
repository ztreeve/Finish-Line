import discord
import os
import asyncio
import json
#import keep_alive #for replit
from discord.ext.commands.core import command
from dotenv import load_dotenv
from discord.ext import commands

botColor = discord.Color.blue()
statsFile = "stats.json"
docplayer = "You are not registered to this server. try `!newplayer`."
doctime = "You took too long. Try again."

#Bot Setup-------------------------------------------------------
load_dotenv()
TOKEN = os.getenv("TOKEN2")
intents = discord.Intents.default()
intents.members = True  # Subscribe to the privileged members intent.
bot = commands.Bot(command_prefix='&', intents=intents)

#read data/ write data------------------------------------------------------
def read():
    with open(statsFile,"r") as file:
        return json.load(file)
def write(data):
    with open(statsFile, "w") as file:
        json.dump(data, file, indent = 3, sort_keys=True)

#does the player exist? returns 0 if not in bot, returns 1 if in bot 
def playerExists(id, playerId):
    data = read()
    if playerId in data["players"]:
        return 1
    else:
        return 0

#Determines if a map is registered. Can detect all aliases. returns true map name if found. returns "no" if not found.
def findMap(mapName):
    data = read()
    for map in data["maps"]:
        mapAliases = []
        mapAliases.append(map)
        for aliases in data["maps"][map]["aliases"]:
            mapAliases.append(aliases)
        if mapName in mapAliases:
            return map
    return "no"

#turns a X:XX:XX.X time into integer XXXXXX
def timeToInt(time):
    l = len(time)
    if time[-2] == ".":
        if l == 6: timeInt = int(time[0]+time[2:4]+time[5])
        if l == 7: timeInt = int(time[0:2]+time[3:5]+time[6])
        if l == 9: timeInt = int(time[0]+time[2:4]+time[5:7]+time[8])
    else:
        if l == 4: timeInt = int(time[0]+time[2:])*10
        elif l == 5: timeInt = int(time[0:2]+ time[3:])*10
        elif l == 7: timeInt = int(time[0]+time[2:4]+time[5:])*10
        else: timeInt = 0
    return timeInt

def intToTime(timeInt):
    timeStr = str(timeInt)
    time = ""
    
    if timeInt <= 999: time = str(timeInt%1000-timeInt%10)
    elif timeInt <= 9999 and timeInt > 999: time = "{}:{}".format(timeStr[0],timeStr[1:3])
    elif timeInt <= 99999 and timeInt > 9999: time = "{}:{}".format(timeStr[0:2],timeStr[2:4])
    elif timeInt <= 99999 and timeInt > 9999: time = "{}:{}".format(timeStr[0:2],timeStr[2:4])
    elif timeInt <= 999999 and timeInt > 99999: time = "{}:{}:{}".format(timeStr[0],timeStr[1:3],timeStr[3:4])
    
    if timeInt % 10 != 0:
        time = time + ".{}".format(timeInt%10)
    return time

def rankListLocal(id, mapName):
    data = read()
    mapCheck = findMap(mapName)
    guild = bot.get_guild(id)
    statlist = {}
    for player in data["players"]:
        for map in data["players"][player]:
            if map == mapCheck:
                if guild.get_member(int(player)) is not None:
                    name = data["players"][player]["name"]
                    statlist[name] = data["players"][player][map]
    return sorted(statlist.items(), key = lambda kv: kv[1])

def rankListGlobal(mapName):
    data = read()
    mapCheck = findMap(mapName)
    statlist = {}
    for player in data["players"]:
        for map in data["players"][player]:
            if map == mapCheck:
                name = data["players"][player]["name"]
                statlist[name] = data["players"][player][map]
    return sorted(statlist.items(), key = lambda kv: kv[1])

def mapInfo(mapName):
    data = read()
    desc, wr, pic, link = "","","",""
    for item in data["maps"]:
        if mapName == item:
            desc, wr, pic, link = data["maps"][item]["description"], data["maps"][item]["world record"], data["maps"][item]["picture"],data["maps"][item]["link"]
            return [desc, wr, pic, link]
    
#Initialize the player to the bot----------------------------------------------
def newplayer(playerId, name, mention):
    """To initialize a player"""
    playerId = str(playerId)
    data = read()
    data["players"][playerId] = {"name": name, "mention": mention}
    write(data)

#adds a newrun (time) to file for specific player/map
@bot.command(pass_context=True, aliases = ["nr"])
async def newrun(ctx, *, mapTitle = None):
    """Input a new time"""
    if mapTitle is None:
        await ctx.channel.send("No map was given. try `$newrun MAPNAME`")
    mapName,id,playerId = mapTitle.lower(),str(ctx.guild.id),str(ctx.author.id)
    def check(msg):
        return msg.channel == ctx.channel and msg.author == ctx.author
    if playerExists(id, playerId) == 0:
        newplayer(playerId, ctx.author.name, ctx.author.mention)
    if playerExists(id, playerId) == 1:
        mapCheck = findMap(mapName)
        if mapCheck == "no":
            await ctx.channel.send("{} was not found. Try `$maps` for a list of maps and their aliases".format(mapName))
        else:
            mapName = mapCheck
            message = await ctx.channel.send("input time for {}".format(mapName))
            try:
                timeInput = await bot.wait_for('message', check = check, timeout = 30.0)
            except asyncio.TimeoutError:
                await ctx.channel.send(doctime)
            else:
                time = str(timeInput.content)
                timeInt = timeToInt(time)
                data = read()
                data["players"][playerId][mapName] = timeInt
                write(data)
                await ctx.channel.delete_messages([discord.Object(id=timeInput.id)])
                await ctx.channel.delete_messages([discord.Object(id=message.id)])
                await ctx.channel.send("{} achieved a time of {} on {}".format(ctx.author.mention, time, mapName))

#creates a stat board for a specififed player. If no player is given it works on self.
@bot.command()
async def stats(ctx, playerName = None):
    """personal times and ranks for each map input"""
    if playerName is None:
        id = str(ctx.guild.id)
        playerName = str(ctx.author.name)
        playerId = str(ctx.author.id)
    else:
        await ctx.channel.send("Currently unable to search for other's stats. If you want your own stats do `$stats` with no name")
    if playerExists(id, playerId) == 0:
        newplayer(playerId, ctx.author.name, ctx.author.mention)
    if playerExists(id, playerId) == 1:
        data = read()
        maplist = "\u200b"
        timelist = "\u200b"
        ranklist = "\u200b"
        for mapName in data["players"][playerId]:
            if mapName == "name" or mapName == "mention":
                continue
            maplist += "{}\n".format(mapName.title())
            time = intToTime(data["players"][playerId][mapName])
            timelist += "{}\n".format(time)
            rankDataL = rankListLocal(ctx.guild.id, mapName)
            rankDataG = rankListGlobal(mapName)
            rankL, rankG, n, x = "","", 0, 0
            for item in rankDataL:
                n += 1
                if intToTime(item[1]) == time:
                    rankL = n
                    break
            for item in rankDataG:
                x += 1
                if intToTime(item[1]) == time:
                    rankG = x
                    break
            ranklist += "{} / {}\n".format(rankL, rankG)
        em = discord.Embed(title = "{}'s amazing stats!".format(data["players"][playerId]["name"]), color = discord.Color.blue())
        em.add_field(name = "Map:", value = maplist, inline = True)
        em.add_field(name = "Time:", value = timelist, inline = True)
        em.add_field(name = "Rank (Local/Global)", value = ranklist, inline = True)
        await ctx.channel.send(embed = em)     

#logs information on a new map
@bot.command()
async def newmap(ctx, *, mapTitle):
    """Adds a new map"""
    mapName = mapTitle.lower()
    if ctx.message.author.id == 269607941252841482:
        def check(msg):
            return msg.channel == ctx.channel and msg.author == ctx.author
        
        await ctx.channel.send("What's the workshop link for {}?".format(mapName))
        try:
            link = await bot.wait_for('message', check = check, timeout = 30.0)
        except asyncio.TimeoutError:
            await ctx.channel.send(doctime)
        else:
            await ctx.channel.send("What's the world record?")
            try:
                wr = await bot.wait_for('message', check = check, timeout = 30.0)
            except asyncio.TimeoutError:
                await ctx.channel.send(doctime)
            else:
                await ctx.channel.send("Send the link to a picture to represent the map")
                try:
                    picture = await bot.wait_for('message', check = check, timeout = 30.0)
                except asyncio.TimeoutError:
                    await ctx.channel.send(doctime)
                else:
                    await ctx.channel.send("Type out a brief description of the map")
                    try:
                        desc = await bot.wait_for('message', check = check, timeout = 30.0)
                    except asyncio.TimeoutError:
                        await ctx.channel.sned(doctime)
                    else:
                        data = read()
                        data["maps"][str(mapName)] = {"link":str(link.content), "world record":str(wr.content), "picture":str(picture.content), "description":str(desc.content), "aliases":[]}
                        write(data)
                        await ctx.channel.send("{} has been added to file".format(mapName)) 
    else:
        await ctx.channel.send("You do not have permission to use this command")

#displays embed list of all maps currently in file
@bot.command(aliases = ["maplist"])
async def maps(ctx):
    """all maps and their aliases"""
    data = read()
    mapList = ""
    aliasList = ""
    for workshopMap in data["maps"]:
        mapList = mapList + workshopMap + "\n"
        n = 0
        for mapAlias in data["maps"][workshopMap]["aliases"]:
            n+=1
            if n > 1:
                aliasList += ", "
            aliasList = aliasList + mapAlias
        aliasList = aliasList + "\n"
    mapdisplay = discord.Embed(title = 'Workshop Maps!', color = botColor)
    mapdisplay.add_field(name = 'Maps:',value = mapList,inline = True)
    mapdisplay.add_field(name = 'Aliases:', value = aliasList, inline = True)
    await ctx.channel.send(embed = mapdisplay)

#creates a new alias for a map
@bot.command()
async def newalias(ctx, *, mapTitle):
    """Adds new alias to map (contact Reeve)"""
    mapName = mapTitle.lower()
    if ctx.message.author.id == 269607941252841482:
        check = findMap(mapName)
        if check == "no":
            await ctx.channel.send("{} cannot be found".format(mapName))
        else:
            mapName = check
            def check(msg):
                return msg.channel == ctx.channel and msg.author == ctx.author
            await ctx.channel.send("Input an alias for {}".format(mapName))
            try:
                alias = await bot.wait_for('message', check = check, timeout = 30.0)
            except asyncio.TimeoutError:
                await ctx.channel.send(doctime)
            else:
                data = read()
                data["maps"][mapName]["aliases"].append(str(alias.content).lower())
                write(data)
                data = read()
                aliases = ""
                n = 0
                for name in data["maps"][mapName]["aliases"]:
                    n+=1
                    if n > 1:
                        aliases += ", "
                    aliases = aliases + name
                await ctx.channel.send("{} can now be referred to as {}".format(mapName, aliases))
    else:
        await ctx.channel.send("You do not have permission to use this command")

@bot.command(aliases = ["mapinfo"])
async def leaderboard(ctx, *,mapTitle):
    """Local Map info and top times"""
    mapName = mapTitle.lower()
    data = read()
    guild = bot.get_guild(ctx.guild.id)

    mapCheck = findMap(mapName)
    if mapCheck == "no":
        await ctx.channel.send("{} was not found.".format(mapName))
    else:
        mapName = mapCheck
        sortedlist = rankListLocal(ctx.guild.id, mapName)
        embedlist, embedlist2 = '\u200b','\u200b'
        n = 0
        for item in sortedlist:
            n += 1
            if n <= 10:
                embedlist += "{}. {} -{}\n".format(n,intToTime(item[1]), item[0])
            elif n <= 20:
                embedlist2 += "{}. {} -{}\n".format(n,intToTime(item[1]), item[0])
            else:
                break
        info = mapInfo(mapName) #desc, wr, pic, link
        em = discord.Embed(title = "**{}** Server Top 20".format(mapName.title()), color = discord.Color.blue())
        em.set_thumbnail(url = info[2])
        em.add_field(name = "Workshop link", value = info[3], inline = False)
        em.add_field(name = "1-10", value = embedlist, inline = True)
        if len(sortedlist) > 10:
            em.add_field(name = "11-20", value = embedlist2, inline = True)

        await ctx.channel.send(embed = em)

@bot.command()
async def globalboard(ctx, *,mapTitle):
    """global map info and top times"""
    mapName = mapTitle.lower()
    data = read()
    guild = bot.get_guild(ctx.guild.id)

    mapCheck = findMap(mapName)
    if mapCheck == "no":
        await ctx.channel.send("{} was not found.".format(mapName))
    else:
        mapName = mapCheck
        sortedlist = rankListGlobal(mapName)
        embedlist, embedlist2 = '\u200b', '\u200b'
        n = 0
        for item in sortedlist:
            n += 1
            if n <= 10:
                embedlist += "{}. {} -{}\n".format(n,intToTime(item[1]), item[0])
            elif n <= 20:
                embedlist2 += "{}. {} -{}\n".format(n,intToTime(item[1]), item[0])
            else:
                break
        info = mapInfo(mapName) #desc, wr, pic, link
        em = discord.Embed(title = "{} Global Top 20".format(mapName.title()), color = discord.Color.blue())
        em.set_thumbnail(url = info[2])
        em.add_field(name = "Workshop link", value = info[3], inline = False)
        em.add_field(name = "1-10", value = embedlist, inline = True)
        if len(sortedlist) > 10:
            em.add_field(name = "11-20", value = embedlist2, inline = True)

        await ctx.channel.send(embed = em) 

@bot.command()
async def redo(ctx):
    """resets data system (perms req)"""
    if ctx.message.author.id == 269607941252841482:
        data = {"players":{}, "maps":{}}
        write(data)
        await ctx.channel.send("file has been reset")
    else:
        await ctx.channel.send("You do not have permission to use this command")



#keep_alive.keep_alive()
bot.run(TOKEN)