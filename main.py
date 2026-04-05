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

DELAY = 1.2
COOLDOWN = 2

auto_mode = None
user_cooldowns = {}

WAIFU_CATEGORIES = [
    "waifu", "neko", "trap", "blowjob", "boobs", "hentai"
]

# ===== FETCH =====
async def fetch_json(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as res:
                if res.status != 200:
                    return None
                return await res.json()
    except:
        return None

# ===== IMAGE (ONLY IMAGE) =====
async def get_image():
    for _ in range(3):  # thử lại tối đa 3 lần
        cat = random.choice(WAIFU_CATEGORIES)
        data = await fetch_json(f"https://api.waifu.pics/nsfw/{cat}")

        if data and "url" in data:
            url = data["url"]
            if url.endswith((".jpg", ".png", ".jpeg")):
                return url

    return None

# ===== GIF (ONLY GIF) =====
async def get_gif():
    for _ in range(3):
        data = await fetch_json("https://nekos.life/api/v2/img/Random_hentai_gif")

        if data and "url" in data:
            url = data["url"]
            if url.endswith(".gif"):
                return url

    return None

# ===== AUTO TASK =====
async def auto_task(channel):
    global auto_mode

    while True:
        if not auto_mode:
            break

        try:
            if auto_mode == "img":
                url = await get_image()

            elif auto_mode == "gif":
                url = await get_gif()

            else:
                url = None

            if not url:
                continue

            embed = discord.Embed(title=f"🔞 {auto_mode.upper()}")
            embed.set_image(url=url)

            await channel.send(embed=embed)

            await asyncio.sleep(DELAY)

        except Exception as e:
            print("Auto error:", e)
            await asyncio.sleep(2)

# ===== READY =====
@client.event
async def on_ready():
    print(f"✅ Bot online: {client.user}")

# ===== MESSAGE =====
@client.event
async def on_message(message):
    global auto_mode

    if message.author.bot:
        return

    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    user_id = message.author.id
    now = time.time()

    if user_id in user_cooldowns:
        if now - user_cooldowns[user_id] < COOLDOWN:
            return

    user_cooldowns[user_id] = now

    msg = message.content.lower()

    # ===== HELP =====
    if msg == "help":
        embed = discord.Embed(title="📜 Commands")
        embed.add_field(name="auto img", value="Spam ảnh", inline=False)
        embed.add_field(name="auto gif", value="Spam gif", inline=False)
        embed.add_field(name="stop", value="Dừng", inline=False)
        embed.add_field(name="ping", value="Check ping", inline=False)

        await message.channel.send(embed=embed)

    # ===== PING =====
    elif msg == "ping":
        latency = round(client.latency * 1000)
        await message.channel.send(f"🏓 {latency}ms")

    # ===== AUTO IMG =====
    elif msg == "auto img":
        if auto_mode:
            await message.channel.send("⚠️ Đang chạy rồi!")
            return

        auto_mode = "img"
        await message.channel.send("▶️ Spam ảnh ON")
        client.loop.create_task(auto_task(message.channel))

    # ===== AUTO GIF =====
    elif msg == "auto gif":
        if auto_mode:
            await message.channel.send("⚠️ Đang chạy rồi!")
            return

        auto_mode = "gif"
        await message.channel.send("▶️ Spam gif ON")
        client.loop.create_task(auto_task(message.channel))

    # ===== STOP =====
    elif msg == "stop":
        auto_mode = None
        await message.channel.send("⏹️ STOP")

# ===== RUN =====
if TOKEN is None:
    print("❌ Thiếu TOKEN")
else:
    client.run(TOKEN)
