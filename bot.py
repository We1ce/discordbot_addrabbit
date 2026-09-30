import os
import random
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

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'目前登入身份：{bot.user}')

# === 新增功能：隨機選擇指令 ===
# 使用方式範例: !隨機 珍奶 咖啡 水
@bot.command(name="隨機")
async def random_choice(ctx, *options: str):
    # 檢查使用者有沒有輸入選項
    if len(options) == 0:
        await ctx.send("請至少提供兩個選項，例如：`!隨機 抽 不抽`")
        return
    
    if len(options) == 1:
        await ctx.send(f"只有一個選項：**{options[0]}**，我看你是想被我抽？")
        return

    # 從選項中隨機挑選一個
    chosen = random.choice(options)
    
    # 組合成好看的回覆訊息
    options_text = ", ".join(options)
    await ctx.send(f"**{chosen}**")

# === 核心功能：按 ➕ 表情符號轉發訊息 ===
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
