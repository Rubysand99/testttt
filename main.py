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
last_images = {}

# ===== CHARACTER LIST =====
CHARACTERS = {
    "roxy": "roxy_migurdia",
    "sylphy": "sylphiette",
    "rem": "rem_(re:zero)",
    "emilia": "emilia_(re:zero)",
    "zero_two": "zero_two_(darling_in_the_franxx)",
    "mikasa": "mikasa_ackerman"
}

# ===== CATEGORY =====
SFW_CATEGORIES = ["waifu", "neko", "smile"]
NSFW_CATEGORIES = ["waifu", "neko", "trap", "boobs"]

# ===== FETCH =====
async def fetch_json(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as res:
                return await res.json()
    except:
        return None

# ===== GET CHARACTER =====
async def get_character(tag):
    rating = "rating:safe" if not nsfw_mode else "rating:explicit"
    url = f"https://danbooru.donmai.us/posts.json?tags={tag}+{rating}&limit=20"

    data = await fetch_json(url)

    if data:
        post = random.choice(data)
        return post.get("file_url")

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

# ===== FIND ANIME =====
async def find_anime(image_url):
    url = f"https://api.trace.moe/search?url={image_url}"
    data = await fetch_json(url)

    if data and data.get("result"):
        r = data["result"][0]
        return r.get("filename", "Unknown"), round(r.get("similarity", 0)*100, 2)

    return None, None

# ===== SEND EMBED =====
async def send_embed(channel, url, title):
    embed = discord.Embed(title=title)
    embed.set_image(url=url)

    msg = await channel.send(embed=embed)

    last_images[msg.id] = url

    await msg.add_reaction("❤️")
    await msg.add_reaction("🔍")

# ===== AUTO =====
async def auto_task(channel, mode):
    global auto_running

    while auto_running:
        url = None

        if mode in CHARACTERS:
            url = await get_character(CHARACTERS[mode])

        elif mode in SFW_CATEGORIES + NSFW_CATEGORIES:
            api = f"https://api.waifu.pics/{'nsfw' if nsfw_mode else 'sfw'}/{mode}"
            data = await fetch_json(api)
            if data:
                url = data.get("url")

        elif mode == "random":
            url, _ = await get_random()

        if url:
            await send_embed(channel, url, f"{mode.upper()}")

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
        embed.add_field(name="auto <name>", value="Auto theo category/character", inline=False)
        embed.add_field(name="stop", value="Dừng auto", inline=False)
        embed.add_field(name="nsfw on/off", value="Bật/tắt 18+", inline=False)
        embed.add_field(name="list", value="Xem danh sách", inline=False)
        embed.add_field(name="find", value="Tìm anime", inline=False)
        await message.channel.send(embed=embed)

    # ===== LIST =====
    elif msg == "list":
        embed = discord.Embed(title="📂 Danh sách")

        embed.add_field(
            name="👤 Characters",
            value=", ".join(CHARACTERS.keys()),
            inline=False
        )

        embed.add_field(
            name="🎲 Categories",
            value=", ".join(SFW_CATEGORIES + NSFW_CATEGORIES),
            inline=False
        )

        await message.channel.send(embed=embed)

    # ===== NSFW =====
    elif msg == "nsfw on":
        nsfw_mode = True
        await message.channel.send("🔞 NSFW ON")

    elif msg == "nsfw off":
        nsfw_mode = False
        await message.channel.send("✨ NSFW OFF")

    # ===== AUTO =====
    elif msg.startswith("auto "):
        if auto_running:
            await message.channel.send("⚠️ Đang chạy!")
            return

        mode = msg.split(" ")[1]

        auto_running = True
        await message.channel.send(f"▶️ Auto {mode} ON")

        client.loop.create_task(auto_task(message.channel, mode))

    elif msg == "stop":
        auto_running = False
        await message.channel.send("⏹️ STOP")

    # ===== FIND =====
    elif msg == "find":
        if not last_images:
            await message.channel.send("❌ Chưa có ảnh")
            return

        url = list(last_images.values())[-1]

        await message.channel.send("🔍 Đang tìm...")

        anime, sim = await find_anime(url)

        if anime:
            await message.channel.send(f"🎬 {anime}\n📊 {sim}%")
        else:
            await message.channel.send("❌ Không tìm thấy")

    # ===== CHARACTER QUICK =====
    elif msg in CHARACTERS:
        url = await get_character(CHARACTERS[msg])
        if url:
            await send_embed(message.channel, url, msg)

# ===== REACTION =====
@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    msg_id = reaction.message.id

    if msg_id not in last_images:
        return

    url = last_images[msg_id]

    if str(reaction.emoji) == "❤️":
        try:
            await user.send(f"💾 Saved:\n{url}")
        except:
            pass

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
