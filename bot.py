import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'目前登入身份：{bot.user}')

@bot.event
async def on_raw_reaction_add(payload):
    # 1. 忽略機器人自己的反應，以及確保事件發生在伺服器內 (guild_id)
    if payload.member is None or payload.member.bot or payload.guild_id is None:
        return

    channel = bot.get_channel(payload.channel_id)
    if not channel:
        return

    try:
        # 2. 直接抓取使用者剛剛按反應的那一則訊息
        target_message = await channel.fetch_message(payload.message_id)
    except discord.NotFound:
        return

    # 3. 取得點反應的使用者資訊 (伺服器暱稱與頭貼)
    member = payload.member
    display_name = member.nick if member.nick else member.name
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url

    # 4. 在該頻道尋找現有的 Webhook，若沒有則自動建立
    webhooks = await channel.webhooks()
    webhook = discord.utils.get(webhooks, name="AvatarEchoWebhook")
    
    if webhook is None:
        webhook = await channel.create_webhook(name="AvatarEchoWebhook")

    # 5. 使用 Webhook 以使用者的名義發送該訊息的內容
    await webhook.send(
        content=target_message.content,
        username=display_name,
        avatar_url=avatar_url
    )

# 透過環境變數安全讀取 Token
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
