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

DELAY = 1.5
COOLDOWN = 3

auto_mode = None  # img / gif / mix
user_cooldowns = {}

WAIFU_CATEGORIES = [
    "waifu", "neko", "trap", "blowjob", "boobs", "hentai"
]

NEKOS_API = "https://nekos.life/api/v2/img/lewd"

# ===== FETCH =====
async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            return await res.json()

# ===== IMAGE =====
async def get_image():
    cat = random.choice(WAIFU_CATEGORIES)
    data = await fetch_json(f"https://api.waifu.pics/nsfw/{cat}")
    return data["url"]

# ===== GIF =====
async def get_gif():
    data = await fetch_json(NEKOS_API)
    return data["url"]

# ===== AUTO TASK =====
async def auto_task(channel):
    global auto_mode

    while auto_mode:
        try:
            embed = discord.Embed(title=f"🔞 Auto {auto_mode.upper()}")

            # ===== IMG =====
            if auto_mode == "img":
                url = await get_image()
                embed.set_image(url=url)

            # ===== GIF =====
            elif auto_mode == "gif":
                url = await get_gif()
                embed.set_image(url=url)

            # ===== MIX =====
            elif auto_mode == "mix":
                if random.choice([True, False]):
                    url = await get_image()
                else:
                    url = await get_gif()

                embed.set_image(url=url)

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
    global auto_mode

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

    # ===== AUTO IMG =====
    if msg == "auto img":
        if auto_mode:
            await message.channel.send("⚠️ Auto đang chạy rồi!")
            return

        auto_mode = "img"
        await message.channel.send("▶️ Auto ảnh đã bật")
        client.loop.create_task(auto_task(message.channel))

    # ===== AUTO GIF =====
    elif msg == "auto gif":
        if auto_mode:
            await message.channel.send("⚠️ Auto đang chạy rồi!")
            return

        auto_mode = "gif"
        await message.channel.send("▶️ Auto gif đã bật")
        client.loop.create_task(auto_task(message.channel))

    # ===== AUTO MIX =====
    elif msg == "auto mix":
        if auto_mode:
            await message.channel.send("⚠️ Auto đang chạy rồi!")
            return

        auto_mode = "mix"
        await message.channel.send("▶️ Auto mix đã bật")
        client.loop.create_task(auto_task(message.channel))

    # ===== STOP =====
    elif msg == "stop":
        auto_mode = None
        await message.channel.send("⏹️ Đã dừng auto")

# ===== RUN =====
if TOKEN is None:
    print("❌ Thiếu TOKEN")
else:
    client.run(TOKEN)
