import discord
import os
import asyncio
import json
from discord.ext.commands.core import command
from dotenv import load_dotenv
from discord.ext import commands

statsFile = "stats.json"
docinit = "This server needs to be initialized first! use the `init` command!"

#Bot Setup-------------------------------------------------------
load_dotenv()
TOKEN = os.getenv("TOKEN2")
bot = commands.Bot(command_prefix = "!")

#read data/ write data------------------------------------------------------
def read():
    with open(statsFile,"r") as file:
        return json.load(file)
def write(data):
    with open(statsFile, "w") as file:
        json.dump(data, file, indent = 3, sort_keys=True)


#Is the guild allready initialized?-----------------------------
def guildExists(id):
    data = read()
    if id in data["guilds"]:
        return True
    else:
        return False

#does the player exist? returns 0 if not in bot, returns 1 if in bot but not server, returns 2 if allready in server.
def playerExists(id, playerId):
    data = read()
    if playerId in data["guilds"][id]["players"]:
        return 2
    elif playerId in data["players"]:
        return 1
    else:
        return 0

#Initialize the server to the bot---------------------------------------------
@bot.command()
async def init(ctx):
    id = str(ctx.guild.id)
    name = str(ctx.guild.name)

    if guildExists(id):
        await ctx.channel.send("This server has allready been initialized!")
    else:
        data = read()
        data["guilds"][id] = {"name":name, "players":[]}
        write(data)
        await ctx.channel.send("You can now start inputing data for this server")

#Initialize the player to the bot----------------------------------------------
@bot.command()
async def newplayer(ctx):
    id = str(ctx.guild.id)
    playerId = str(ctx.author.id)
    if guildExists(id) == False:
        await ctx.channel.send(docinit)
    else:
        check = playerExists(id, playerId)
        if check == 2:
            await ctx.channel.send("You've allready been registered in this server!")
        elif check == 1:
            data = read()
            data["guilds"][id]["players"].append(playerId)
            write(data)
            await ctx.channel.send("You are now registered in this server as "+str(ctx.author.name))
        elif check == 0:
            data = read()
            data["players"][playerId] = {"name": ctx.author.name}
            data["guilds"][id]["players"].append(playerId)
            write(data)
            await ctx.channel.send("You are now registered as "+str(ctx.author.name))

#adds a new map to the server
bot.run(TOKEN)