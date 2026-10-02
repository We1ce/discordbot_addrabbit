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

# === 功能 1：表情符號轉發訊息（支援一般頻道與論壇貼文） ===
@bot.event
async def on_raw_reaction_add(payload):
    if payload.member is None or payload.member.bot or payload.guild_id is None:
        return

    TARGET_EMOJI = "➕"
    if payload.emoji.name != TARGET_EMOJI:
        return

    # 1. 取得頻道物件
    channel = bot.get_channel(payload.channel_id)
    if not channel:
        return

    try:
        # 2. 抓取被按反應的原始訊息（支援論壇貼文/討論串）
        target_message = await channel.fetch_message(payload.message_id)
    except discord.NotFound:
        return

    # 3. 取得點反應的使用者資訊 (伺服器暱稱與頭貼)
    member = payload.member
    display_name = member.nick if member.nick else member.name
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url

    # 4. 判斷如果是在論壇貼文或討論串 (Thread)，Webhook 必須建立在「父頻道 (Parent Channel)」上
    target_channel = channel
    if isinstance(channel, discord.Thread):
        target_channel = channel.parent  # 論壇頻道本身

    # 5. 在正確的頻道尋找現有的 Webhook，若沒有則自動建立
    webhooks = await target_channel.webhooks()
    webhook = discord.utils.get(webhooks, name="AvatarEchoWebhook")
    
    if webhook is None:
        webhook = await target_channel.create_webhook(name="AvatarEchoWebhook")

    # 6. 發送訊息
    # 如果是在論壇貼文裡按的，我們利用 thread=channel 讓 webhook 把訊息發在該貼文串內
    if isinstance(channel, discord.Thread):
        await webhook.send(
            content=target_message.content,
            username=display_name,
            avatar_url=avatar_url,
            thread=channel
        )
    else:
        # 一般文字頻道
        await webhook.send(
            content=target_message.content,
            username=display_name,
            avatar_url=avatar_url
        )

# === 功能 2 & 3：訊息監聽（支援繁體與簡體） ===
@bot.event
async def on_message(message):
    # 忽略機器人自己說的話，避免無限迴圈
    if message.author.bot:
        return

    content = message.content.strip()

    # ----------------------------------------------------
    # 功能 A：隨機抽籤 (支援繁中、簡中)
    # ----------------------------------------------------
    if content.startswith("隨機 ") or content.startswith("随机 "):
        # 取得空格後面的選項內容
        options_str = content[3:].strip()
        options = [opt.strip() for opt in options_str.split() if opt.strip()]
        
        if len(options) > 0:
            chosen = random.choice(options)
            await message.channel.send(f"**{chosen}**")
        return  # 處理完隨機就直接結束，不往下跑運勢

    # ----------------------------------------------------
    # 功能 B：運勢查詢 (支援繁中、簡中)
    # ----------------------------------------------------
    target_name = None
    
    if content.endswith("的運勢"):
        target_name = content[:-3]
    elif content.endswith("運勢"):
        target_name = content[:-2]
    elif content.endswith("的运势"):
        target_name = content[:-4]
    elif content.endswith("运势"):
        target_name = content[:-3]

    if target_name:
        fortunes = ["大吉", "中吉", "小吉", "吉", "末吉", "凶", "大凶"]
        result = random.choice(fortunes)
        
        # 回覆格式：@使用者 訊息內容：運勢結果
        await message.channel.send(f"{message.author.mention} {content}：**{result}**")
        return

if __name__ == "__main__":
    keep_alive()
    TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(TOKEN)
