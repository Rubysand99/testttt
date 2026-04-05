import discord
import aiohttp
import asyncio
import os
import random

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

client = discord.Client(intents=intents)

TOKEN = os.getenv("TOKEN")
ALLOWED_CHANNEL_ID = 1408419176149811252

DELAY = 1.5

auto_running = False
nsfw_mode = False
last_images = {}  # message_id : image_url

# ===== CATEGORY =====
SFW_CATEGORIES = ["waifu", "neko", "smile", "happy"]
NSFW_CATEGORIES = ["waifu", "neko", "trap", "blowjob", "boobs"]

GIF_API = "https://nekos.life/api/v2/img/Random_hentai_gif"

# ===== FETCH =====
async def fetch_json(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as res:
                return await res.json()
    except:
        return None

# ===== GET RANDOM =====
async def get_random():
    if nsfw_mode:
        cat = random.choice(NSFW_CATEGORIES)
        api = f"https://api.waifu.pics/nsfw/{cat}"
    else:
        cat = random.choice(SFW_CATEGORIES)
        api = f"https://api.waifu.pics/sfw/{cat}"

    data = await fetch_json(api)

    if data and "url" in data:
        return data["url"], cat

    return None, None

# ===== GET GIF =====
async def get_gif():
    data = await fetch_json(GIF_API)
    if data and "url" in data:
        return data["url"]
    return None

# ===== FIND ANIME =====
async def find_anime(image_url):
    url = f"https://api.trace.moe/search?url={image_url}"
    data = await fetch_json(url)

    if data and data.get("result"):
        r = data["result"][0]
        return r.get("filename", "Unknown"), round(r.get("similarity", 0)*100, 2)

    return None, None

# ===== SEND =====
async def send_embed(channel, url, title):
    embed = discord.Embed(title=title)
    embed.set_image(url=url)

    msg = await channel.send(embed=embed)

    # lưu lại ảnh để dùng reaction
    last_images[msg.id] = url

    # thêm reaction
    await msg.add_reaction("❤️")
    await msg.add_reaction("🔍")

# ===== AUTO =====
async def auto_task(channel):
    global auto_running

    while auto_running:
        url, cat = await get_random()

        if url:
            await send_embed(channel, url, f"{'🔞' if nsfw_mode else '✨'} {cat}")

        await asyncio.sleep(DELAY)

# ===== READY =====
@client.event
async def on_ready():
    print(f"✅ Bot online: {client.user}")

# ===== MESSAGE =====
@client.event
async def on_message(message):
    global auto_running, nsfw_mode

    if message.author.bot:
        return

    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    msg = message.content.lower()

    # ===== HELP =====
    if msg == "help":
        embed = discord.Embed(title="📜 Commands")

        embed.add_field(name="auto", value="Spam random", inline=False)
        embed.add_field(name="stop", value="Dừng", inline=False)
        embed.add_field(name="nsfw on/off", value="Bật/tắt 18+", inline=False)
        embed.add_field(name="gif", value="GIF anime", inline=False)

        embed.add_field(name="category", value=", ".join(SFW_CATEGORIES + NSFW_CATEGORIES), inline=False)

        embed.set_footer(text="❤️ = lưu | 🔍 = tìm anime")

        await message.channel.send(embed=embed)

    # ===== NSFW =====
    elif msg == "nsfw on":
        nsfw_mode = True
        await message.channel.send("🔞 NSFW ON")

    elif msg == "nsfw off":
        nsfw_mode = False
        await message.channel.send("✨ NSFW OFF")

    # ===== AUTO =====
    elif msg == "auto":
        if auto_running:
            await message.channel.send("⚠️ Đang chạy!")
            return

        auto_running = True
        await message.channel.send("▶️ Auto ON")
        client.loop.create_task(auto_task(message.channel))

    elif msg == "stop":
        auto_running = False
        await message.channel.send("⏹️ STOP")

    # ===== GIF =====
    elif msg == "gif":
        url = await get_gif()
        if url:
            await send_embed(message.channel, url, "GIF")

# ===== REACTION =====
@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    msg_id = reaction.message.id

    if msg_id not in last_images:
        return

    url = last_images[msg_id]

    # ❤️ lưu ảnh
    if str(reaction.emoji) == "❤️":
        try:
            await user.send(f"💾 Saved:\n{url}")
        except:
            pass

    # 🔍 tìm anime
    elif str(reaction.emoji) == "🔍":
        channel = reaction.message.channel
        await channel.send("🔍 Đang tìm...")

        anime, sim = await find_anime(url)

        if anime:
            await channel.send(f"🎬 {anime}\n📊 {sim}%")
        else:
            await channel.send("❌ Không tìm thấy")

# ===== RUN =====
if TOKEN:
    client.run(TOKEN)
else:
    print("❌ Thiếu TOKEN")
