import discord
import os
from discord.ext.commands.core import command
from dotenv import load_dotenv
from discord.ext import commands
import gspread


#Bot Setup
load_dotenv()
TOKEN = os.getenv("TOKEN2")
bot = commands.Bot(command_prefix = "$$")


bot.run(TOKEN)
