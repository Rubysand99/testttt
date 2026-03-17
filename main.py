import discord
import requests
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

TOKEN = os.getenv("TOKEN")

ALLOWED_CHANNEL_ID = 1408419176149811252

# trạng thái auto gửi ảnh
auto_send = False

# ===== LẤY ẢNH =====
def get_image():
    url = "https://api.waifu.pics/nsfw/waifu"
    res = requests.get(url).json()
    return res["url"]

# ===== READY =====
@client.event
async def on_ready():
    print(f"✅ Bot online: {client.user}")

# ===== AUTO TASK =====
async def auto_image(channel):
    global auto_send
    while auto_send:
        try:
            img = get_image()
            embed = discord.Embed(title="🔞 Auto Waifu")
            embed.set_image(url=img)
            await channel.send(embed=embed)
            await asyncio.sleep(3)  # 👉 delay (đừng để 1s)
        except Exception as e:
            print(e)
            break

# ===== MESSAGE =====
@client.event
async def on_message(message):
    global auto_send

    if message.author.bot:
        return

    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    msg = message.content.lower()

    # ===== LỆNH ẢNH =====
    if msg == "waifu":
        img = get_image()
        embed = discord.Embed(title="🔞 Waifu")
        embed.set_image(url=img)
        await message.channel.send(embed=embed)

    elif msg == "neko":
        img = get_image()
        embed = discord.Embed(title="🔞 Neko")
        embed.set_image(url=img)
        await message.channel.send(embed=embed)

    elif msg == "trap":
        img = get_image()
        embed = discord.Embed(title="🔞 Trap")
        embed.set_image(url=img)
        await message.channel.send(embed=embed)

    # ===== AUTO ON =====
    elif msg == "auto":
        if auto_send:
            await message.channel.send("⚠️ Đang chạy rồi!")
            return

        auto_send = True
        await message.channel.send("▶️ Bắt đầu auto gửi ảnh...")
        client.loop.create_task(auto_image(message.channel))

    # ===== AUTO OFF =====
    elif msg == "stop":
        auto_send = False
        await message.channel.send("⏹️ Đã dừng auto")

# ===== RUN =====
if TOKEN is None:
    print("❌ Không tìm thấy TOKEN!")
else:
    client.run(TOKEN)
