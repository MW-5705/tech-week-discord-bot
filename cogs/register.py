import os
from discord.ext import commands
from pymongo import MongoClient
from discord import Embed
from discord.utils import get
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Register(commands.Cog):
    def __init__(self, client):
        self.client = client
        mongo_url = os.getenv("MONGO_URL")
        self.cluster = MongoClient(mongo_url)
        self.db = self.cluster["Discord"]
        self.collection = self.db["Participants"]
        self.departments = {
            "⚙️": "Backend",
            "🕸️": "Frontend",
            "🖥️": "IoT",
            "🔒": "Web3",
            "⛓️": "Blockchain",
            "🖼️": "UI/UX Design",
            "🤖": "AI/ML",
        }

    @commands.Cog.listener()
    async def on_ready(self):
        print("register.py is ready!")

    @commands.command(name='register')
    async def register(self, ctx):
        discord_id = ctx.author.id

        # Check if the user is already registered
        if self.collection.find_one({"discordid": discord_id}):
            await ctx.send("You are already registered!")
            return

        # Create an embed message with department choices
        embed = Embed(title="Department Registration", description="Choose your department by reacting to this message:")
        for emoji, department in self.departments.items():
            embed.add_field(name=department, value=emoji, inline=False)

        registration_message = await ctx.send(embed=embed)

        # Add reactions to the embed message
        for emoji in self.departments.keys():
            await registration_message.add_reaction(emoji)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in self.departments.keys()

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, check=check)
        except TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")
            return

        department = self.departments[str(reaction.emoji)]

        # Insert the user into the database
        user_data = {"discordid": discord_id, "department": department}
        try:
            self.collection.insert_one(user_data)
            await ctx.send(f"You are registered in the {department} department")
        except Exception as e:
            await ctx.send("An error occurred while registering. Please try again later.")
            print(f"Error inserting data into MongoDB: {e}")

async def setup(client):
    await client.add_cog(Register(client))
