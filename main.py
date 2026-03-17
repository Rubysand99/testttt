import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import aiohttp

intents = discord.Intents.default()
intents.message_content = True

PREFIX_FILE = "prefixes.json"

# ======================
# LOAD / SAVE PREFIX
# ======================
def load_prefixes():
    if not os.path.exists(PREFIX_FILE):
        return {}
    with open(PREFIX_FILE, "r") as f:
        return json.load(f)

def save_prefixes(data):
    with open(PREFIX_FILE, "w") as f:
        json.dump(data, f, indent=4)

prefixes = load_prefixes()

def get_prefix(bot, message):
    return prefixes.get(str(message.guild.id), "!")

bot = commands.Bot(command_prefix=get_prefix, intents=intents)

# ======================
# READY
# ======================
@bot.event
async def on_ready():
    print(f"Đã đăng nhập: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Đã sync {len(synced)} slash commands")
    except Exception as e:
        print(e)

# ======================
# PREFIX COMMAND
# ======================
@bot.command()
@commands.has_permissions(administrator=True)
async def prefix(ctx, new_prefix):
    prefixes[str(ctx.guild.id)] = new_prefix
    save_prefixes(prefixes)
    await ctx.send(f"Đã đổi prefix thành: `{new_prefix}`")

@prefix.error
async def prefix_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Bạn cần quyền admin!")

# ======================
# PING
# ======================
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.tree.command(name="ping", description="Check bot")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

# ======================
# WAIFU / NEKO API
# ======================
async def get_image(endpoint):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.waifu.pics/sfw/{endpoint}") as resp:
            data = await resp.json()
            return data["url"]

# PREFIX COMMANDS
@bot.command()
async def waifu(ctx):
    url = await get_image("waifu")
    embed = discord.Embed(title="Waifu 🥰")
    embed.set_image(url=url)
    await ctx.send(embed=embed)

@bot.command()
async def neko(ctx):
    url = await get_image("neko")
    embed = discord.Embed(title="Neko 🐱")
    embed.set_image(url=url)
    await ctx.send(embed=embed)

# SLASH COMMANDS
@bot.tree.command(name="waifu", description="Random waifu")
async def slash_waifu(interaction: discord.Interaction):
    url = await get_image("waifu")
    embed = discord.Embed(title="Waifu 🥰")
    embed.set_image(url=url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="neko", description="Random neko")
async def slash_neko(interaction: discord.Interaction):
    url = await get_image("neko")
    embed = discord.Embed(title="Neko 🐱")
    embed.set_image(url=url)
    await interaction.response.send_message(embed=embed)

# ======================
bot.run(os.getenv("TOKEN"))
