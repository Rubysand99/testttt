import discord
import aiohttp
import asyncio
import os
import random
import time

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

TOKEN = os.getenv("TOKEN")
ALLOWED_CHANNEL_ID = 1408419176149811252

# ===== CONFIG =====
DELAY = 5  # thời gian gửi auto (giây)
COOLDOWN = 3  # cooldown user (giây)

auto_send = False
user_cooldowns = {}

# ===== API LIST =====
WAIFU_CATEGORIES = [
    "waifu", "neko", "trap", "blowjob", "boobs", "hentai"
]

NEKOS_API = "https://nekos.life/api/v2/img/lewd"

# fake video (bạn có thể thay link thật)
VIDEOS = [
    "https://files.catbox.moe/5v7g3h.mp4",
    "https://files.catbox.moe/abc123.mp4"
]

# ===== GET CONTENT =====
async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            return await res.json()

async def get_content():
    choice = random.choice(["image", "gif", "video"])

    # ===== IMAGE (waifu.pics) =====
    if choice == "image":
        cat = random.choice(WAIFU_CATEGORIES)
        data = await fetch_json(f"https://api.waifu.pics/nsfw/{cat}")
        return data["url"]

    # ===== GIF (nekos.life) =====
    elif choice == "gif":
        data = await fetch_json(NEKOS_API)
        return data["url"]

    # ===== VIDEO =====
    else:
        return random.choice(VIDEOS)

# ===== AUTO TASK =====
async def auto_task(channel):
    global auto_send

    while auto_send:
        try:
            content = await get_content()

            embed = discord.Embed(title="🔞 Auto Anime 18+")
            
            if content.endswith(".mp4"):
                await channel.send(content)
            else:
                embed.set_image(url=content)
                await channel.send(embed=embed)

            await asyncio.sleep(DELAY)

        except Exception as e:
            print("Auto error:", e)
            await asyncio.sleep(5)

# ===== READY =====
@client.event
async def on_ready():
    print(f"✅ Bot online: {client.user}")

# ===== MESSAGE =====
@client.event
async def on_message(message):
    global auto_send

    if message.author.bot:
        return

    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    user_id = message.author.id
    now = time.time()

    # ===== COOLDOWN =====
    if user_id in user_cooldowns:
        if now - user_cooldowns[user_id] < COOLDOWN:
            return

    user_cooldowns[user_id] = now

    msg = message.content.lower()

    # ===== RANDOM CONTENT =====
    if msg == "18+":
        content = await get_content()

        embed = discord.Embed(title="🔞 Anime 18+")

        if content.endswith(".mp4"):
            await message.channel.send(content)
        else:
            embed.set_image(url=content)
            await message.channel.send(embed=embed)

    # ===== AUTO ON =====
    elif msg == "auto":
        if auto_send:
            await message.channel.send("⚠️ Đang chạy rồi!")
            return

        auto_send = True
        await message.channel.send("▶️ Auto 18+ đã bật")
        client.loop.create_task(auto_task(message.channel))

    # ===== AUTO OFF =====
    elif msg == "stop":
        auto_send = False
        await message.channel.send("⏹️ Auto đã dừng")

# ===== RUN =====
if TOKEN is None:
    print("❌ Thiếu TOKEN")
else:
    client.run(TOKEN)
