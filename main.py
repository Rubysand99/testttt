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

last_images = {}   # message_id : url
gallery = {}       # user_id : [url]
favorites = {}     # user_id : [url]

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
            async with session.get(url) as res:
                return await res.json()
    except:
        return None

# ===== CHARACTER =====
async def get_character(tag):
    rating = "rating:safe" if not nsfw_mode else "rating:explicit"
    url = f"https://danbooru.donmai.us/posts.json?tags={tag}+{rating}&limit=20"

    data = await fetch_json(url)

    if data:
        post = random.choice(data)
        return post.get("file_url")

    return None

# ===== RANDOM =====
async def get_random():
    if nsfw_mode:
        cat = random.choice(NSFW_CATEGORIES)
        api = f"https://api.waifu.pics/nsfw/{cat}"
    else:
        cat = random.choice(SFW_CATEGORIES)
        api = f"https://api.waifu.pics/sfw/{cat}"

    data = await fetch_json(api)

    if data:
        return data.get("url"), cat

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
            await send_embed(channel, url, mode)

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

    user_id = message.author.id
    msg = message.content.lower()

    # ===== LIST =====
    if msg == "list":
        embed = discord.Embed(title="📂 Danh sách")
        embed.add_field(name="👤 Characters", value=", ".join(CHARACTERS.keys()), inline=False)
        embed.add_field(name="🎲 Categories", value=", ".join(SFW_CATEGORIES + NSFW_CATEGORIES), inline=False)
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

    # ===== CHARACTER QUICK =====
    elif msg in CHARACTERS:
        url = await get_character(CHARACTERS[msg])
        if url:
            await send_embed(message.channel, url, msg)

    # ===== GALLERY =====
    elif msg == "gallery":
        if user_id not in gallery or not gallery[user_id]:
            await message.channel.send("📂 Bạn chưa lưu ảnh nào")
            return

        for url in gallery[user_id][-5:]:
            await send_embed(message.channel, url, "📂 Gallery")

    # ===== FAVORITE =====
    elif msg == "fav":
        if user_id not in favorites or not favorites[user_id]:
            await message.channel.send("⭐ Bạn chưa có favorite")
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

    # ❤️ SAVE + FAVORITE
    if str(reaction.emoji) == "❤️":
        gallery.setdefault(user_id, []).append(url)
        favorites.setdefault(user_id, []).append(url)

        try:
            await user.send("💾 Đã lưu & thêm vào favorite!")
        except:
            pass

    # 🔍 FIND
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
