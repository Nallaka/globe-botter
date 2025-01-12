from riotwatcher import LolWatcher, ApiError, RiotWatcher
from riotwatcher import _apis
import json
import discord
from discord.ext import commands
from discord import app_commands
from data_broker import register_player, update_players, progress_all, progress_call, globetrotter_progress

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
async def frelijord(ctx):
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
async def adminregister(ctx, discordname, riotid):
    register_player(discordname, riotid)
    await ctx.channel.send(f"League Account {riotid} registered successfully. Linked to {discordname} on Discord")

@bot.command()
async def updateall(ctx):
    update_players()
    await ctx.channel.send("All registered players updated successfully.")

@bot.command()
async def progressall(ctx):
    update_players()
    await ctx.channel.send(progress_all())

@bot.command()
async def progresscall(ctx):

    if not ctx.author.voice:
        await ctx.send("You are not in a voice channel!")
        return

    channel = ctx.author.voice.channel
    players = []

    for member in channel.members:
        players.append(str(member))

    if players:
        await ctx.send(f"Users in {channel.name}: {', '.join(players)}")
        update_players()
        await ctx.channel.send(progress_call(players))
    else:
        await ctx.send("No one is in this voice channel.")



@bot.command()
async def globetrotterprogressall(ctx):
    await ctx.send(globetrotter_progress())

bot.run(bot_token)