from pathlib import Path

from riotwatcher import LolWatcher, ApiError, RiotWatcher
from riotwatcher import _apis
import json
import discord
from discord.ext import commands
from discord import app_commands
import os
from data_broker import register_player, update_players, progress_all, progress_call, globetrotter_progress, \
    progress_player, optimal_region, optimal_region_call

with open("keys.json", "r") as keys:
    api_keys = json.load(keys)

api_key = api_keys["riot_api"]
region = "americas"

lol_watcher = LolWatcher(api_key)
riot_watcher = RiotWatcher(api_key)

bot_token = api_keys["bot_token"]

description = "Bot to track MPAS Globetrotter achievements"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='?', description=description, intents=intents)
#tree = app_commands.CommandTree(bot)


@bot.event
async def on_ready():
    print(lol_watcher.lol_status_v4.platform_data("na1"))
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.hybrid_command()
async def print_challenges(ctx):
    regions = ""
    for region_id in range(303501, 303514):
        challenge_config = lol_watcher.challenges.challenge_config("na1", region_id)
        challenge_name = challenge_config["localizedNames"]["en_US"]["name"]
        region_name = challenge_config["localizedNames"]["en_US"]["description"].replace("As a premade 5, win games with 5 champions from ", "").replace("the ", "")
        regions = regions + region_name + ": " + challenge_name +  "\n"
    print(regions)
    await ctx.send(regions)

@bot.hybrid_command()
async def bandlecity(ctx):
    await ctx.channel.send(file=discord.File('./regions/bandlecity.png'))

@bot.hybrid_command()
async def bilgewater(ctx):
    await ctx.channel.send(file=discord.File('./regions/bilgewater.png'))

@bot.hybrid_command()
async def demacia(ctx):
    await ctx.channel.send(file=discord.File('./regions/demacia.png'))

@bot.hybrid_command()
async def freljord(ctx):
    await ctx.channel.send(file=discord.File('./regions/wide_nunu.gif'))
    await ctx.channel.send(file=discord.File('./regions/frelijord.png'))

@bot.hybrid_command()
async def ionia(ctx):
    await ctx.channel.send(file=discord.File('./regions/ionia.png'))

@bot.hybrid_command()
async def ixtal(ctx):
    await ctx.channel.send(file=discord.File('./regions/ixtal.png'))

@bot.hybrid_command()
async def noxus(ctx):
    await ctx.channel.send(file=discord.File('./regions/noxus.png'))

@bot.hybrid_command()
async def piltover(ctx):
    await ctx.channel.send(file=discord.File('./regions/piltover.png'))

@bot.hybrid_command()
async def shadowisles(ctx):
    await ctx.channel.send(file=discord.File('./regions/shadowisles.png'))

@bot.hybrid_command()
async def shurima(ctx):
    await ctx.channel.send(file=discord.File('./regions/shurima_sunday.gif'))
    await ctx.channel.send(file=discord.File('./regions/shurima.png'))


@bot.hybrid_command()
async def targon(ctx):
    await ctx.channel.send(file=discord.File('./regions/targon.png'))

@bot.hybrid_command()
async def void(ctx):
    await ctx.channel.send(file=discord.File('./regions/void.png'))

@bot.hybrid_command()
async def zaun(ctx):
    await ctx.channel.send(file=discord.File('./regions/zaun.png'))

@bot.command()
async def selfregister(ctx, riotid):
    register_player(ctx.message.author.name, riotid)
    await ctx.channel.send(f"League Account {riotid} registered successfully. Linked to {ctx.message.author.name} on Discord")

@bot.command()
async def adminregister(ctx, user: discord.User, riotid):
    register_player(user.name, riotid)
    await ctx.channel.send(f"League Account {riotid} registered successfully. Linked to {user.name} on Discord")

@bot.command()
async def updateall(ctx):
    update_players()
    await ctx.channel.send("All registered players updated successfully.")

@bot.command()
async def progressall(ctx):
    update_players()
    message1, message2 = progress_all()

    await ctx.channel.send(embed=message1)
    await ctx.channel.send(embed=message2)

@bot.command()
async def progresscall(ctx, exclude="", *args: discord.User):

    if not ctx.author.voice:
        await ctx.send("You are not in a voice channel!")
        return

    channel = ctx.author.voice.channel
    players = []

    for member in channel.members:
        players.append(str(member))

    if exclude == "exclude":
        for player_to_exclude in args:
            print(player_to_exclude)

            players.remove(player_to_exclude.name)

    if players:
        await ctx.send(f"Users in {channel.name}: {', '.join(players)}")
        update_players()
        message1, message2 = progress_call(players)

        await ctx.channel.send(embed=message1)
        #await ctx.channel.send(embed=message2)
    else:
        await ctx.send("No one is in this voice channel.")

@bot.command()
async def globetrotterprogressall(ctx):
    await ctx.send(embed=globetrotter_progress())

@bot.command()
async def ladder(ctx):
    await ctx.send(embed=globetrotter_progress())

@bot.command()
async def playerprogress(ctx, user: discord.User):
    update_players()
    message1, message2 = progress_player(user.name)

    await ctx.channel.send(embed=message1)
    #await ctx.channel.send(embed=message2)

@bot.command()
async def selfprogress(ctx):
    update_players()
    message1, message2 = progress_player(ctx.author.name)

    await ctx.channel.send(embed=message1)

@bot.command()
async def optimal(ctx):
    await ctx.channel.send(embed=optimal_region())

@bot.command()
async def optimalcall(ctx, exclude="", *args: discord.User):
    if not ctx.author.voice:
        await ctx.send("You are not in a voice channel!")
        return

    channel = ctx.author.voice.channel
    players = []

    for member in channel.members:
        players.append(str(member))

    if exclude == "exclude":
        for player_to_exclude in args:
            print(player_to_exclude)

            players.remove(player_to_exclude.name)

    if players:
        await ctx.send(f"Users in {channel.name}: {', '.join(players)}")
        update_players()

        await ctx.channel.send(embed=optimal_region_call(players))
    else:
        await ctx.send("No one is in this voice channel.")

@bot.command()
async def exclude(ctx, user:discord.Member=None):
    if user == None: # if no user is passed..
        user = ctx.author # ..make the command author the user
    if user.name == "nallaka":
        message = "Denied!"
        embed = discord.Embed(title=message)
        embed.add_field(name="DENIED:", value="I apologize, but user \"nallaka\" is not eligible for exclusion due to resistance to \"racism\".\nPlease try a different user." )
        await ctx.channel.send(embed=embed)
        return
    message = "Exclusion!"
    embed = discord.Embed(title=message)
    embed.add_field(name="Excluded:", value="Excluded once again, racism triumphs!")
    await user.send(embed=embed)

@bot.command()
async def fixit(ctx):
    embed = discord.Embed(title="Fix It")
    embed.add_field(name="What a great suggestion! You should implement it!", value="https://github.com/Nallaka/globe-botter")

    await ctx.channel.send(embed=embed)

def inplace_change(filename, old_string, new_string):
    # Safely read the input filename using 'with'
    with open(filename) as f:
        s = f.read()
        if old_string not in s:
            print('"{old_string}" not found in {filename}.'.format(**locals()))
            return

    # Safely write the changed content, if found in the file
    with open(filename, 'w') as f:
        print('Changing "{old_string}" to "{new_string}" in {filename}'.format(**locals()))
        s = s.replace(old_string, new_string)
        f.write(s)

@bot.command()
async def fixfile(ctx):
    with open("./players.json", 'rb+') as fh:
        fh.seek(-2, os.SEEK_END)
        fh.truncate()

bot.run(bot_token)