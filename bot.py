#import Libraries
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import gspread

#Spreadsheet setup / defining worksheets
gc = gspread.service_account(filename='creds.json')
spread = gc.open('CustomMapComp')

stierlist = spread.worksheet('TierList')
smaps = spread.worksheet('Maps')
sinput = spread.worksheet('Input')
splayers = spread.worksheet('Players')
smain = spread.worksheet('MainSheet')
stest = spread.worksheet('testing')

#grab bot token from .env file and create bot
load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = commands.Bot(command_prefix = '$')
    

#converts input time to a number so it can be compared
def time_to_int(time):
    if len(time) == 4: 
        time_int = int(time[0]+time[2:])*100
    elif len(time) == 5:
        time_int = int(time[:2]+time[3:])*100
    elif len(time) == 6:
        time_int = int(time[0]+time[2]+time[3]+time[5])*10
    elif len(time) == 7:
        time_int = int(time[0]+time[2:4]+time[5:])
    elif len(time) == 8:
        time_int = int(time[:2]+time[3:5]+time[6:])
    else:
        time_int = False
    return time_int

#finds rank of previously input run
def find_rank(cmap, player):
    rowPlayer = sinput.findall(player, None, 6)
    for row in rowPlayer:
        if cmap == sinput.cell(row.row, row.col + 1).value:
            mapposition = arg_exists(smaps, cmap, 6).row + 10
            rank = sinput.cell(row.row, mapposition).value
            return rank
    return False

#finds next free row in sheet (default collumn A)
def next_free_row(sheet, cols_to_sample=1):
    cols = sheet.range(1,1,sheet.row_count, cols_to_sample)
    return max([cell.row for cell in cols if cell.value]) + 1

#Checks if an argument exists within a sheet (by collumn)
def arg_exists(sheet, arg, col = None):
    cells = sheet.findall(arg,None,col)
    if len(cells) > 0:
        return sheet.find(arg, None, col)
    else:
        return False
######################################################################################################################################
@bot.command()
async def hi(ctx):
    """Say hi to FinishLine!"""
    pass
    await ctx.channel.send('Hi, {}!'.format(ctx.message.author.mention))

#Register a new player
@bot.command()
async def newplayer(ctx):
    """registers yourself to the database."""
    
    player = str(ctx.message.author.name)
    mention_player = ctx.message.author.mention

    cell = arg_exists(splayers, player)
    if cell == False:
        splayers.update('A'+str(next_free_row(splayers)), player)
        await ctx.channel.send(mention_player+' has been registered')
    else:
        await ctx.channel.send(mention_player+' is allready in the database.')

#Unregister a player
@bot.command()
async def removeplayer(ctx):
    """Un-registers yourself from the database"""

    player = str(ctx.message.author.name)
    mention_player = ctx.message.author.mention
    cell = arg_exists(splayers, player, 1)
    if cell == False:
        await ctx.channel.send(mention_player+' is not in the database.')
    else:
        spread.values_clear('Players!A'+str(cell.row))
        await ctx.channel.send(mention_player+' has been removed from the database')

#Displays all registered Players
@bot.command()
async def players(ctx):
    """displays a list of all registered players."""

    displayplayerlist = ""
    playerlist = splayers.col_values(1)
    for i in range(len(playerlist)-1):
        displayplayerlist += str(playerlist[i+1]) + '\n'
    playerdisplay = discord.Embed(
        title = '------Registered Players------',
        color = discord.Color.green()
    )
    playerdisplay.add_field(
        name = 'Players:',
        value = displayplayerlist,
        inline = True
    )
    
    await ctx.channel.send(embed = playerdisplay)

#displays the list of current maps
@bot.command()
async def maps(ctx):
    """Shows list of all registered maps"""
    displaymaplist = ""
    maplist = smaps.col_values(6)
    for i in range(len(maplist)):
        displaymaplist += str(maplist[i]) + '\n'
    mapdisplay = discord.Embed(
        title = '------Custom Maps------',
        color = discord.Color.blue()
    )
    mapdisplay.add_field(
        name = 'Maps:',
        value = displaymaplist,
        inline = True
    )
    await ctx.channel.send(embed = mapdisplay)

#displays info for a map
@bot.command()
async def mapinfo(ctx, map_name):
    """Displays info on a specific map"""
    pass
    map_cell = arg_exists(smaps, map_name, 6)
    #checks that map is registered
    if map_cell == False:
        await ctx.channel.send(map_name+' is not a registered map.')
    else:
        map_col = (map_cell.row)*4 - 4
        namelist, timelist = '\u200b','\u200b'
        for i in range(5):
            player = smain.cell(i+4, map_col + 2).value
            if player == None:
                break
            namelist += '{}. {}\n'.format(i+1, player)
            timelist += '{}\n'.format(smain.cell(i+4, map_col + 3).value)
        display_map_info = discord.Embed(
            title = '-----{}-----\n'.format(map_name),
            color = discord.Color.green()
        )
        display_map_info.set_thumbnail(url = str(smaps.cell(map_cell.row, 10).value))
        display_map_info.add_field(
            name = 'Description',
            value = '*{}*'.format(str(smaps.cell(map_cell.row, 7).value)),
            inline = False
        )
        display_map_info.add_field(name = '\u200b', value = "_**Top Times:**_", inline = False)
        display_map_info.add_field(
            name = 'Name:',
            value = namelist,
            inline = True
        )
        display_map_info.add_field(
            name = 'Time:',
            value = timelist,
            inline = True
        )
        display_map_info.add_field(name = 'World Record',value = str(smaps.cell(map_cell.row,9).value), inline = False)
        display_map_info.add_field(name = 'Link:', value = str(smaps.cell(map_cell.row,8).value), inline = False)
        
        await ctx.channel.send(embed = display_map_info)

#Input Data
@bot.command()
async def newrun(ctx, map_name, time):
    """adds a new time, format: $newrun <map> <time>"""

    player = str(ctx.message.author.name)
    playercell = arg_exists(splayers, player, 1)
    cmapcell = arg_exists(smaps, map_name, 1)
    inputrow = next_free_row(sinput)
    if playercell == False:
        await ctx.channel.send(player+' is not registered. To register, type $newplayer')
    elif cmapcell == False:
        await ctx.channel.send(map_name+' is not in the database.\nTry $maps to make sure you spelt it correctly')
    else:
        player_in_cells = sinput.findall(player,None,1)
        cmap_in_cells = sinput.findall(map_name,None,2)
        combo = False
        for P in player_in_cells:
            for M in cmap_in_cells:
                if P.row == M.row:
                    combo = True
                    if time_to_int(time) < time_to_int(str(sinput.acell('C'+str(P.row)).value)):
                        previous = str(sinput.acell('C'+str(P.row)).value)
                        sinput.update('A'+str(P.row)+':C'+str(P.row), [[player, map_name, time]])
                        sinput.update('E{}'.format(str(P.row)), time_to_int(time))
                        print(time_to_int(time))
                        rank = str(find_rank(map_name, player))
                        await ctx.channel.send(player+' achieved a time of '+time+' on '+map_name+' (Rank '+rank+' ). Previous time was '+previous)
                    elif time_to_int(time) == time_to_int(str(sinput.acell('C'+str(P.row)).value)):
                        await ctx.channel.send('Input time same as previous input time')
                    else:
                        await ctx.channel.send('Input time is higher than previous time of '+str(sinput.acell('C'+str(P.row)).value))
        if combo == False:
            sinput.update('A'+str(inputrow)+':C'+str(inputrow), [[player, map_name, time]])
            sinput.update('E{}'.format(str(inputrow)), time_to_int(time))
            print(time_to_int(time))
            rank = str(find_rank(map_name, player))
            await ctx.channel.send(player+' achieved a time of '+time+' on '+map_name+' (Rank '+rank+' ).')

#player statistics
@bot.command()
async def stats(ctx,*, player = None):
    """Shows all maps/times/ranks for a specific player. If no player is given it works on self"""

    if player == None:
        player = str(ctx.message.author.name)
    playerexists = arg_exists(splayers, player)
    if playerexists == False:
        await ctx.channel.send(player+' is not a registered player. Check Capitalization')
    else:
        #playertier= splayers.cell(playerexists.row,playerexists.col+1).value
        player_in_rows = sinput.findall(player, None, 6)
        mapdisplay = ""
        timedisplay = ""
        rankdisplay = ""
        for cell in player_in_rows:
            mapvalue = sinput.cell(cell.row, cell.col+1).value
            mapdisplay += str(mapvalue) + '\n'
            timedisplay += str(sinput.cell(cell.row, cell.col+2).value) + '\n'
            rankcol = arg_exists(smaps, mapvalue, 6).row + 10
            rankdisplay += str(sinput.cell(cell.row, rankcol).value) + '\n'
        
    playerdisplay = discord.Embed(
        title = player, #+ ' (' + playertier + ')',
        color = discord.Color.gold()
    )
    playerdisplay.add_field(
        name = 'Map',
        value = mapdisplay,
        inline = True
    )
    playerdisplay.add_field(
        name = 'Time',
        value = timedisplay,
        inline = True
    )
    playerdisplay.add_field(
        name = 'Rank',
        value = rankdisplay,
        inline = True
    )
    await ctx.channel.send(embed = playerdisplay)

#add a new map to next free row in 'Maps'
@bot.command()
async def newmap(ctx,*, map_name):
    """ADMIN - adds a new map"""
    
    #if user is Reeve
    if ctx.message.author.id == 269607941252841482:
        #Checks that map does not allready exist
        if arg_exists(smaps, map_name) == False:
            smaps.update('A'+str(next_free_row(smaps)), map_name)
            await ctx.channel.send(map_name+' has been added to the list of Custom Maps')
        else:
            await ctx.channel.send(map_name+' is allready in the database.')
    else:
        await ctx.channel.send("Sorry, {}, but you don't have permission to do that!".format(ctx.message.author.mention))
    
@bot.command()
async def removemap(ctx, map_name):
    """ADMIN - removes a map"""

    if ctx.message.author.id == 269607941252841482:
        cell = arg_exists(smaps, map_name, 1)
        if cell == False:
            await ctx.channel.send(map_name+' is not in the database.')
        else:
            spread.values_clear('Maps!A{}:E{}'.format(cell.row, cell.row))
            await ctx.channel.send(map_name+' has been removed from the database')
    else:
        await ctx.channel.send("sorry, {}, but you don't have permission to do that!".format(ctx.message.author.mention))



@bot.command()
async def myname(ctx):

    await ctx.channel.send(str(ctx.message.author.name))
@bot.command()
async def spreadsheet(ctx):
    """gives link to the spreadsheet"""
    await ctx.channel.send("You can find the spreadsheet here\nhttps://docs.google.com/spreadsheets/d/1ifvTBqWHzWxF1L9GZguKsev-7aRPIeoGAV-8QBlg-Sc/edit#gid=1689348750")
bot.run(TOKEN)
