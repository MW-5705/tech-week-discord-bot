import discord
from discord.ext import commands, tasks
from itertools import cycle
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Intents setup
intents = discord.Intents.all()
intents.members = True
intents.presences = True
intents.messages = True

# Bot setup with command prefix and intents
client = commands.Bot(command_prefix="!", intents=intents)
bot_status = cycle(["Status One", "Status Two", "Status Three"])

# Background task to change bot status
@tasks.loop(seconds=5)
async def change_status():
    await client.change_presence(activity=discord.Game(next(bot_status)))

# Event when bot is ready
@client.event
async def on_ready():
    print("Bot is connected to Discord")
    change_status.start()

# Function to load all cogs
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await client.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded extension: {filename}")
            except Exception as e:
                print(f"Failed to load extension {filename}: {type(e).__name__} - {e}")


# Main coroutine to start the bot
async def main():
    async with client:
        await load_cogs()
        await client.start(os.getenv("DISCORD_TOKEN"))  # Retrieve token from environment variable

# Run the main coroutine
if __name__ == "__main__":
    asyncio.run(main())
