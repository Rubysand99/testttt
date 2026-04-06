import discord
import aiohttp
import asyncio
import os
import random
import json

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

# ===== FILE =====
def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

gallery = load_json("gallery.json")
favorites = load_json("favorites.json")
recent_images = load_json("cache.json").get("recent", [])

MAX_CACHE = 50

# ===== CHARACTER =====
CHARACTERS = {
    "roxy": "roxy_migurdia",
    "sylphy": "sylphiette",
    "rem": "rem_(re:zero)",
    "emilia": "emilia_(re:zero)",
    "zero_two": "zero_two_(darling_in_the_franxx)",
    "mikasa": "mikasa_ackerman"
}

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

# ===== SAVE CACHE =====
def update_cache(url):
    recent_images.append(url)
    if len(recent_images) > MAX_CACHE:
        recent_images.pop(0)
    save_json("cache.json", {"recent": recent_images})

# ===== CHARACTER =====
async def get_character(tag):
    rating = "rating:safe" if not nsfw_mode else "rating:explicit"

    for _ in range(5):
        url = f"https://danbooru.donmai.us/posts.json?tags={tag}+{rating}&limit=20"
        data = await fetch_json(url)

        if data:
            post = random.choice(data)
            file_url = post.get("file_url")

            if file_url and file_url not in recent_images:
                update_cache(file_url)
                return file_url, post.get("tag_string")

    return None, None

# ===== RANDOM =====
async def get_random():
    for _ in range(5):
        if nsfw_mode:
            api = random.choice([
                "https://api.waifu.pics/nsfw/waifu",
                "https://api.waifu.pics/nsfw/neko"
            ])
        else:
            api = random.choice([
                "https://api.waifu.pics/sfw/waifu",
                "https://api.waifu.pics/sfw/neko"
            ])

        data = await fetch_json(api)

        if data and "url" in data:
            url = data["url"]

            if url not in recent_images:
                update_cache(url)
                return url, None

    return None, None

# ===== FIND =====
async def find_anime(url):
    api = f"https://api.trace.moe/search?url={url}"
    data = await fetch_json(api)

    if data and data.get("result"):
        r = data["result"][0]
        return r.get("filename"), round(r.get("similarity", 0)*100, 2)

    return None, None

# ===== SEND =====
async def send_embed(channel, url, title, tags=None):
    embed = discord.Embed(title=title)
    embed.set_image(url=url)

    if tags:
        embed.set_footer(text=f"Tags: {tags[:100]}")

    msg = await channel.send(embed=embed)

    last_images[msg.id] = url

    await msg.add_reaction("❤️")
    await msg.add_reaction("🔍")

# ===== AUTO =====
async def auto_task(channel, mode):
    global auto_running

    while auto_running:
        url, tags = None, None

        if mode in CHARACTERS:
            url, tags = await get_character(CHARACTERS[mode])

        elif mode == "random":
            url, tags = await get_random()

        if not url:
            url, tags = await get_random()

        if url:
            await send_embed(channel, url, mode, tags)

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

    user_id = str(message.author.id)
    msg = message.content.lower()

    if msg == "help":
        await message.channel.send("help | ping | auto <name> | stop | nsfw on/off | gallery | fav | list")

    elif msg == "ping":
        await message.channel.send(f"🏓 {round(client.latency*1000)}ms")

    elif msg == "list":
        await message.channel.send(f"{', '.join(CHARACTERS.keys())}")

    elif msg == "nsfw on":
        nsfw_mode = True
        await message.channel.send("NSFW ON")

    elif msg == "nsfw off":
        nsfw_mode = False
        await message.channel.send("NSFW OFF")

    elif msg.startswith("auto "):
        if auto_running:
            await message.channel.send("Đang chạy")
            return

        mode = msg.split(" ")[1]
        auto_running = True
        await message.channel.send(f"Auto {mode} ON")

        client.loop.create_task(auto_task(message.channel, mode))

    elif msg == "stop":
        auto_running = False

    elif msg in CHARACTERS:
        url, tags = await get_character(CHARACTERS[msg])
        if not url:
            url, tags = await get_random()

        await send_embed(message.channel, url, msg, tags)

    elif msg == "gallery":
        for url in gallery.get(user_id, [])[-5:]:
            await send_embed(message.channel, url, "Gallery")

    elif msg == "fav":
        for url in favorites.get(user_id, [])[-5:]:
            await send_embed(message.channel, url, "Favorite")

# ===== REACTION =====
@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    msg_id = reaction.message.id

    if msg_id not in last_images:
        return

    url = last_images[msg_id]
    user_id = str(user.id)

    if str(reaction.emoji) == "❤️":
        gallery.setdefault(user_id, []).append(url)
        favorites.setdefault(user_id, []).append(url)

        save_json("gallery.json", gallery)
        save_json("favorites.json", favorites)

    elif str(reaction.emoji) == "🔍":
        anime, sim = await find_anime(url)

        if anime:
            await reaction.message.channel.send(f"{anime} ({sim}%)")
        else:
            await reaction.message.channel.send("Không tìm thấy")

# ===== RUN =====
if TOKEN:
    client.run(TOKEN)
