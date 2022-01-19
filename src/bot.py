import datetime
import json
import logging
import os
import sys

import interactions
from interactions.context import CommandContext

from database import JSONDatabase
from utils import get_maps, input_to_timedelta

FILE = 'finish-line.log'
file_handler = logging.FileHandler(FILE)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

logging.basicConfig(level=logging.INFO,
                    handlers=[file_handler, console_handler],
                    format="%(asctime)s %(levelname)s: [%(funcName)s] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")

logging.info(f"Initialized logging, now writing to [{FILE}].")

if not os.path.exists(os.path.dirname(__file__) + '/../config.json'):
    logging.error(
        'Token file not found. Place your Discord token ID in a file called `config.json`.', file=sys.stderr)
    sys.exit(1)

with open(os.path.dirname(__file__) + '/../config.json', 'r') as f:
    config = json.load(f)
    logging.info("Initializing Bot")
    bot = interactions.Client(token=config["token"])


@bot.command(
    name="newrun",
    description="Record a new run.",
    options=[interactions.Option(
        type=interactions.OptionType.STRING,
        name="map",
        description="Rocket League Map.",
        required=True,
        choices=list(map(lambda x: interactions.Choice(
            name=x, value=x), get_maps().keys()))
    ), interactions.Option(
        type=interactions.OptionType.STRING,
        name="time",
        description="HH:MM:SS or XX:XX:XX.X",
        required=True,
    )]
)
async def record(ctx: CommandContext, map, time):
    logging.info(
        f"Command accessed by {ctx.member.user.id} : {ctx.member.user.username}.")
    await ctx.defer()

    player = JSONDatabase(ctx.member, ctx.guild_id)

    time_of_run = input_to_timedelta(time)

    if not time_of_run:
        await ctx.send("Incorrect time format, try `hour:min:sec`.")
        return

    if time_of_run.total_seconds() > 86399:
        await ctx.send("Runs more than a day are too slow.")
        return
    if time_of_run.total_seconds() < 1:
        await ctx.send("Your run was too fast!")
        return

    if player.add_record(map, time_of_run.total_seconds()):
        await ctx.send(f"<@!{ctx.member.user.id}>, Congrats on your `{time_of_run}` run on `{map}`!")
    else:
        await ctx.send(f"<@!{ctx.member.user.id}>, You got a time `{time_of_run}` run on `{map}`. Try and beat your record of `{datetime.timedelta(seconds=player.records[map])}`.")


@bot.command(
    name="deleterun",
    description="Clear a run.",
    options=[interactions.Option(
        type=interactions.OptionType.STRING,
        name="map",
        description="Rocket League Map.",
        required=True,
        choices=list(map(lambda x: interactions.Choice(
            name=x, value=x), get_maps().keys()))
    )]
)
async def clear_record(ctx: CommandContext, map):
    logging.info(
        f"Command accessed by {ctx.member.user.id} : {ctx.member.user.username}.")
    await ctx.defer()

    player = JSONDatabase(ctx.member, ctx.guild_id)

    if player.delete_record(map):
        await ctx.send(f"<@!{ctx.member.user.id}>, successfully cleared run on `{map}`.")
    else:
        await ctx.send(f"<@!{ctx.member.user.id}>, no run exists on `{map}`.")


@bot.command(
    name="leaderboard",
    description="View current server rankings.",
    options=[interactions.Option(
        type=interactions.OptionType.STRING,
        name="map",
        description="Rocket League Map.",
        required=True,
        choices=list(map(lambda x: interactions.Choice(
            name=x, value=x), get_maps().keys()))
    ), interactions.Option(
        type=interactions.OptionType.STRING,
        name="scope",
        description="View local/global leaderboard.",
        required=True,
        choices=[interactions.Choice(name='Local', value='Local'), interactions.Choice(
            name='Global', value='Global')]
    )]
)
async def leaderboard(ctx: CommandContext, map, scope):
    logging.info(
        f"Command accessed by {ctx.member.user.id} : {ctx.member.user.username}.")
    await ctx.defer()

    player = JSONDatabase(ctx.member, ctx.guild_id)

    if scope == 'Local':
        leaderboard = player.leaderboard(map, local=True)
    else:
        leaderboard = player.leaderboard(map, local=False)

    if not leaderboard:
        await ctx.send(f'No recorded scores for {map}')
        return

    # Thumbnail seems to be really broken
    embed = interactions.Embed(
        title=f"{scope} Top 20: {map}", color=0x1a47ff,
        # thumbnail=interactions.EmbedImageStruct(url=get_maps()[map]['picture']),
        fields=[
            # interactions.EmbedField(name="Workshop Link", value=get_maps()[map]['link'], inline=True),
            interactions.EmbedField(name="Leaderboard:", value='\n'.join(
                [f'{leaderboard.index(x) + 1}. {x[0]} - {datetime.timedelta(seconds=x[1])}' for x in leaderboard[:20]]), inline=False)
        ])
    await ctx.send(embeds=[embed])


@bot.command(
    name="stats",
    description="View previously recorded runs.",
)
async def stats(ctx: CommandContext):
    logging.info(
        f"Command accessed by {ctx.member.user.id} : {ctx.member.user.username}.")
    await ctx.defer()

    player = JSONDatabase(ctx.member, ctx.guild_id)

    stats = []
    for map in player.records.keys():
        personal_record = datetime.timedelta(seconds=player.records[map])

        local_leaderboard = player.leaderboard(map, local=True)
        local_rank = [x[0] for x in local_leaderboard].index(
            ctx.member.user.username) + 1

        global_leaderboard = player.leaderboard(map, local=False)
        global_rank = [x[0] for x in global_leaderboard].index(
            ctx.member.user.username) + 1
        stats.append([map, personal_record, local_rank, global_rank])

    map = '\n'.join([x[0] for x in stats])
    time = '\n'.join([str(x[1]) for x in stats])
    ranking = '\n'.join([f'{x[2]}/{x[3]}' for x in stats])

    if not stats:
        await ctx.send(f'No stats for {ctx.member.user.username}')
        return
    embed = interactions.Embed(
        title=f"{player.name}'s amazing stats!", color=0x1a47ff,
        fields=[interactions.EmbedField(name="Map:", value=map, inline=True),
                interactions.EmbedField(name="Time:", value=time, inline=True),
                interactions.EmbedField(
                    name="Rank (Local/Global)", value=ranking, inline=True)
                ])

    await ctx.send(embeds=embed)

logging.info("Starting bot.")
bot.start()
