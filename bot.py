import os

# 這樣它會去雲端主機的安全設定裡讀取 Token
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)