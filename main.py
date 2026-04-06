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
gallery = {}
favorites = {}

# chống trùng
recent_images = []
MAX_CACHE = 20

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
    except Exception as e:
        print("Fetch error:", e)
        return None

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
                recent_images.append(file_url)
                if len(recent_images) > MAX_CACHE:
                    recent_images.pop(0)
                return file_url

    return None

# ===== RANDOM =====
async def get_random():
    for _ in range(5):
        try:
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
                    recent_images.append(url)
                    if len(recent_images) > MAX_CACHE:
                        recent_images.pop(0)
                    return url
        except:
            pass

    return None

# ===== FIND =====
async def find_anime(url):
    api = f"https://api.trace.moe/search?url={url}"
    data = await fetch_json(api)

    if data and data.get("result"):
        r = data["result"][0]
        return r.get("filename"), round(r.get("similarity", 0)*100, 2)

    return None, None

# ===== SEND =====
async def send_embed(channel, url, title):
    if not url:
        return

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
        try:
            url = None

            # CHARACTER
            if mode in CHARACTERS:
                url = await get_character(CHARACTERS[mode])

            # CATEGORY
            elif mode in SFW_CATEGORIES + NSFW_CATEGORIES:
                api = f"https://api.waifu.pics/{'nsfw' if nsfw_mode else 'sfw'}/{mode}"
                data = await fetch_json(api)
                if data:
                    url = data.get("url")

            # RANDOM
            elif mode == "random":
                url = await get_random()

            # fallback
            if not url:
                url = await get_random()

            if not url:
                await asyncio.sleep(1)
                continue

            await send_embed(channel, url, f"{mode.upper()}")

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
    global auto_running, nsfw_mode

    if message.author.bot:
        return

    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    msg = message.content.lower()
    user_id = message.author.id

    # ===== HELP =====
    if msg == "help":
        embed = discord.Embed(title="📜 Commands")
        embed.add_field(name="auto <name>", value="auto roxy / auto neko / auto random", inline=False)
        embed.add_field(name="stop", value="dừng auto", inline=False)
        embed.add_field(name="nsfw on/off", value="bật/tắt 18+", inline=False)
        embed.add_field(name="list", value="xem danh sách", inline=False)
        embed.add_field(name="gallery", value="ảnh đã lưu", inline=False)
        embed.add_field(name="fav", value="ảnh yêu thích", inline=False)
        embed.add_field(name="ping", value="check bot", inline=False)
        await message.channel.send(embed=embed)

    # ===== PING =====
    elif msg == "ping":
        await message.channel.send(f"🏓 {round(client.latency*1000)}ms")

    # ===== LIST =====
    elif msg == "list":
        await message.channel.send(
            f"👤 Characters: {', '.join(CHARACTERS.keys())}\n"
            f"🎲 Categories: {', '.join(SFW_CATEGORIES + NSFW_CATEGORIES)}"
        )

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

    # ===== CHARACTER QUICK =====
    elif msg in CHARACTERS:
        url = await get_character(CHARACTERS[msg])
        if not url:
            url = await get_random()

        await send_embed(message.channel, url, msg)

    # ===== GALLERY =====
    elif msg == "gallery":
        if user_id not in gallery:
            await message.channel.send("📂 Chưa có ảnh")
            return

        for url in gallery[user_id][-5:]:
            await send_embed(message.channel, url, "📂 Gallery")

    # ===== FAVORITE =====
    elif msg == "fav":
        if user_id not in favorites:
            await message.channel.send("⭐ Chưa có favorite")
            return

        for url in favorites[user_id][-5:]:
            await send_embed(message.channel, url, "⭐ Favorite")

# ===== REACTION =====
@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    msg_id = reaction.message.id

    if msg_id not in last_images:
        return

    url = last_images[msg_id]
    user_id = user.id

    if str(reaction.emoji) == "❤️":
        gallery.setdefault(user_id, []).append(url)
        favorites.setdefault(user_id, []).append(url)

    elif str(reaction.emoji) == "🔍":
        await reaction.message.channel.send("🔍 Tìm anime có thể không chính xác!")

# ===== RUN =====
if TOKEN:
    client.run(TOKEN)
else:
    print("❌ Thiếu TOKEN")
