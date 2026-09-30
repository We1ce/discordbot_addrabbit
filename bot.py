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

# === 功能 1：串子回覆 ===
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

# === 功能 2 & 3： ===
@bot.event
async def on_message(message):
    # 忽略機器人自己說的話，避免無限迴圈
    if message.author.bot:
        return

    content = message.content.strip()

    # 功能 A：隨機抽籤 (例如輸入: "隨機 抽 不抽")
    if content.startswith("隨機 "):
        # 把 "隨機 " 後面的文字切開成選項清單
        options_str = content[3:].strip()
        options = [opt.strip() for opt in options_str.split() if opt.strip()]
        
        if len(options) > 0:
            chosen = random.choice(options)
            await message.channel.send(f"**{chosen}**")
        return  # 處理完隨機就直接結束，不往下跑運勢

    # 功能 B：運勢查詢 (例如輸入: "小明運勢" 或 "今天晚餐的運勢")
    target_name = None
    if content.endswith("的運勢"):
        target_name = content[:-3]
    elif content.endswith("運勢"):
        target_name = content[:-2]

    if target_name:
        fortunes = ["大吉", "中吉", "小吉", "吉", "末吉", "凶", "大凶"]
        result = random.choice(fortunes)
        
        # 依照你的要求格式回覆：@使用者 訊息內容：運勢結果
        await message.channel.send(f"{message.author.mention} {content}：**{result}**")
        return

if __name__ == "__main__":
    keep_alive()
    TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(TOKEN)
