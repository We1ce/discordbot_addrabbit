import os
from threading import Thread
from flask import Flask
import discord
from discord.ext import commands

# 1. 網頁伺服器
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# 2. Discord Bot 設定
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
intents.voice_states = True  # 【重要】必須開啟語音狀態 Intent

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'目前登入身份：{bot.user}')

# === 語音功能指令 ===

# 指令 1: !join (加入語音)
@bot.command(name="join")
async def join(ctx):
    try:
        # 檢查使用者是否在語音頻道中
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            if ctx.voice_client is not None:
                await ctx.voice_client.move_to(channel)
            else:
                await channel.connect()
            await ctx.send(f'已成功加入語音頻道：{channel.name}')
        else:
            await ctx.send('請先進入一個語音頻道，我才能進去陪你！')
    except Exception as e:
        # 如果發生錯誤，把詳細錯誤訊息直接印在 Discord 頻道裡
        await ctx.send(f'發生錯誤了：```{e}```')

# 指令 2: !leave (離開語音)
@bot.command(name="leave")
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('已離開語音頻道。')
    else:
        await ctx.send('我目前不在任何語音頻道中。')

# === 原本的表情符號轉發功能 ===
@bot.event
async def on_raw_reaction_add(payload):
    if payload.member is None or payload.member.bot or payload.guild_id is None:
        return

    TARGET_EMOJI = "➕"
    if payload.emoji.name != TARGET_EMOJI:
        return

    channel = bot.get_channel(payload.channel_id)
    if not channel:
        return

    try:
        target_message = await channel.fetch_message(payload.message_id)
    except discord.NotFound:
        return

    member = payload.member
    display_name = member.nick if member.nick else member.name
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url

    webhooks = await channel.webhooks()
    webhook = discord.utils.get(webhooks, name="AvatarEchoWebhook")
    
    if webhook is None:
        webhook = await channel.create_webhook(name="AvatarEchoWebhook")

    await webhook.send(
        content=target_message.content,
        username=display_name,
        avatar_url=avatar_url
    )

if __name__ == "__main__":
    keep_alive()
    TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(TOKEN)
