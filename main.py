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
BURST_COUNT = 4      # số lần spam nhanh mỗi đợt
DELAY = 3            # nghỉ giữa các đợt
COOLDOWN = 2

auto_mode = None
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
            # ===== BURST SPAM =====
            for _ in range(BURST_COUNT):

                embed = discord.Embed(title=f"🔞 {auto_mode.upper()} SPAM")

                if auto_mode == "img":
                    url = await get_image()

                elif auto_mode == "gif":
                    url = await get_gif()

                elif auto_mode == "mix":
                    if random.choice([True, False]):
                        url = await get_image()
                    else:
                        url = await get_gif()

                embed.set_image(url=url)
                await channel.send(embed=embed)

                await asyncio.sleep(0.8)  # delay nhỏ giữa từng tin

            # ===== nghỉ =====
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

    # ===== HELP =====
    if msg == "help":
        embed = discord.Embed(title="📜 Commands", color=0x00ffcc)
        embed.add_field(name="auto img", value="Spam ảnh", inline=False)
        embed.add_field(name="auto gif", value="Spam gif", inline=False)
        embed.add_field(name="auto mix", value="Spam random", inline=False)
        embed.add_field(name="stop", value="Dừng auto", inline=False)
        embed.add_field(name="ping", value="Check độ trễ bot", inline=False)

        await message.channel.send(embed=embed)

    # ===== PING =====
    elif msg == "ping":
        latency = round(client.latency * 1000)
        await message.channel.send(f"🏓 Pong: {latency}ms")

    # ===== AUTO IMG =====
    elif msg == "auto img":
        if auto_mode:
            await message.channel.send("⚠️ Auto đang chạy rồi!")
            return

        auto_mode = "img"
        await message.channel.send("▶️ Spam ảnh đã bật")
        client.loop.create_task(auto_task(message.channel))

    # ===== AUTO GIF =====
    elif msg == "auto gif":
        if auto_mode:
            await message.channel.send("⚠️ Auto đang chạy rồi!")
            return

        auto_mode = "gif"
        await message.channel.send("▶️ Spam gif đã bật")
        client.loop.create_task(auto_task(message.channel))

    # ===== AUTO MIX =====
    elif msg == "auto mix":
        if auto_mode:
            await message.channel.send("⚠️ Auto đang chạy rồi!")
            return

        auto_mode = "mix"
        await message.channel.send("▶️ Spam mix đã bật")
        client.loop.create_task(auto_task(message.channel))

    # ===== STOP =====
    elif msg == "stop":
        auto_mode = None
        await message.channel.send("⏹️ Đã dừng spam")

# ===== RUN =====
if TOKEN is None:
    print("❌ Thiếu TOKEN")
else:
    client.run(TOKEN)
