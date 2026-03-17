import discord
import requests
import os

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

TOKEN = os.getenv("TOKEN")

# ✅ Kênh được phép dùng bot
ALLOWED_CHANNEL_ID = 1408419176149811252

# Lưu trạng thái NSFW
nsfw_enabled = {}

# ===== LẤY ẢNH =====
def get_image(endpoint):
    url = f"https://api.waifu.pics/{endpoint}"
    res = requests.get(url).json()
    return res["url"]

# ===== READY =====
@client.event
async def on_ready():
    print(f"✅ Bot online: {client.user}")

# ===== XỬ LÝ TIN NHẮN =====
@client.event
async def on_message(message):
    if message.author.bot:
        return

    # ❌ Không đúng kênh → bỏ qua
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    msg = message.content.lower()

    # ===== NSFW =====
    if msg == "nsfw on":
        nsfw_enabled[message.guild.id] = True
        await message.channel.send("🔞 NSFW: ON")

    elif msg == "nsfw off":
        nsfw_enabled[message.guild.id] = False
        await message.channel.send("🔞 NSFW: OFF")

    # ===== WAIFU =====
    elif msg == "waifu":
        img = get_image("sfw/waifu")
        embed = discord.Embed(title="🌸 Waifu")
        embed.set_image(url=img)
        await message.channel.send(embed=embed)

    # ===== NEKO =====
    elif msg == "neko":
        img = get_image("sfw/neko")
        embed = discord.Embed(title="🐱 Neko")
        embed.set_image(url=img)
        await message.channel.send(embed=embed)

    # ===== TRAP =====
    elif msg == "trap":
        img = get_image("sfw/trap")
        embed = discord.Embed(title="🎭 Trap")
        embed.set_image(url=img)
        await message.channel.send(embed=embed)

    # ===== WAIFU 18+ =====
    elif msg == "waifu18":
        if not nsfw_enabled.get(message.guild.id, False):
            await message.channel.send("❌ NSFW chưa bật!")
            return

        if not message.channel.is_nsfw():
            await message.channel.send("⚠️ Phải dùng trong kênh NSFW!")
            return

        img = get_image("nsfw/waifu")
        embed = discord.Embed(title="🔞 Waifu 18+")
        embed.set_image(url=img)
        await message.channel.send(embed=embed)

# ===== RUN =====
if TOKEN is None:
    print("❌ Không tìm thấy TOKEN!")
else:
    client.run(TOKEN)
