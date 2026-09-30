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

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
