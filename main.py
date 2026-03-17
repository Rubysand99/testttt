import discord
from discord.ext import commands
import requests

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = "YOUR_BOT_TOKEN"

# Lưu trạng thái NSFW (theo server)
nsfw_enabled = {}

# ===== LẤY ẢNH =====
def get_image(endpoint):
    url = f"https://api.waifu.pics/{endpoint}"
    res = requests.get(url).json()
    return res["url"]

# ===== READY =====
@bot.event
async def on_ready():
    print(f"✅ Bot online: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {len(synced)}")
    except Exception as e:
        print(e)

# ===== NSFW TOGGLE =====
@bot.tree.command(name="nsfw", description="Bật/tắt NSFW")
async def nsfw(interaction: discord.Interaction, mode: str):
    if mode not in ["on", "off"]:
        await interaction.response.send_message("Dùng: on / off", ephemeral=True)
        return

    nsfw_enabled[interaction.guild.id] = (mode == "on")
    await interaction.response.send_message(f"🔞 NSFW: {mode}")

# ===== WAIFU =====
@bot.tree.command(name="waifu", description="Ảnh waifu")
async def waifu(interaction: discord.Interaction):
    img = get_image("sfw/waifu")
    embed = discord.Embed(title="🌸 Waifu")
    embed.set_image(url=img)
    await interaction.response.send_message(embed=embed)

# ===== NEKO =====
@bot.tree.command(name="neko", description="Ảnh neko")
async def neko(interaction: discord.Interaction):
    img = get_image("sfw/neko")
    embed = discord.Embed(title="🐱 Neko")
    embed.set_image(url=img)
    await interaction.response.send_message(embed=embed)

# ===== TRAP =====
@bot.tree.command(name="trap", description="Ảnh trap")
async def trap(interaction: discord.Interaction):
    img = get_image("sfw/trap")
    embed = discord.Embed(title="🎭 Trap")
    embed.set_image(url=img)
    await interaction.response.send_message(embed=embed)

# ===== NSFW WAIFU =====
@bot.tree.command(name="waifu18", description="Ảnh waifu 18+")
async def waifu18(interaction: discord.Interaction):
    if not nsfw_enabled.get(interaction.guild.id, False):
        await interaction.response.send_message("❌ NSFW chưa bật!", ephemeral=True)
        return

    img = get_image("nsfw/waifu")
    embed = discord.Embed(title="🔞 Waifu 18+")
    embed.set_image(url=img)
    await interaction.response.send_message(embed=embed)

# ===== RUN =====
bot.run(TOKEN)
