import os
from discord.ext import commands
from pymongo import MongoClient
from discord import Embed
from discord.utils import get
from dotenv import load_dotenv
from cogs.connection import cluster

# Load environment variables from .env file
load_dotenv()



class Register(commands.Cog):
    def __init__(self, client):
        self.client = client
        # mongo_url = os.getenv("MONGO_URL")
        # self.cluster = MongoClient(mongo_url)
        self.db = cluster["Discord_bot"]
        self.collection = self.db["Participants"]
        self.departments = {
            # "⚙️": "Backend",
            # "🕸️": "Frontend",
            "🖥️": "tech",
            # "🔒": "Web3",
            # "💰": "marketing",
            "🖼️": "design",
            "✍️": "presentation",
        }

    @commands.Cog.listener()
    async def on_ready(self):
        print("register.py is ready!")

    @commands.command(name='register')
    async def register(self, ctx):
        discord_id = ctx.author.id

        # Check if the user is already registered
        if self.collection.find_one({"discordid": discord_id}):
            await ctx.author.send("You are already registered!")
            return

        # Create an embed message with department choices
        embed = Embed(title="Department Registration", description="Choose your Primary department by reacting to this message:")
        for emoji, department in self.departments.items():
            embed.add_field(name=department, value=emoji, inline=False)

        registration_message = await ctx.author.send(embed=embed)

        # Add reactions to the embed message
        for emoji in self.departments.keys():
            await registration_message.add_reaction(emoji)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in self.departments.keys()

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, check=check)
        except TimeoutError:
            await ctx.author.send("You took too long to respond. Please try again.")
            return

        department1 = self.departments[str(reaction.emoji)]
        department2 = department1
        # Embed message for secondary department
        while (department1 == department2):
            embed = Embed(title="Department Registration", description="Choose your Secondary department by reacting to this message:")
            for emoji, department in self.departments.items():
                embed.add_field(name=department, value=emoji, inline=False)

            registration_message = await ctx.author.send(embed=embed)

            # Add reactions to the embed message
            for emoji in self.departments.keys():
                await registration_message.add_reaction(emoji)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in self.departments.keys()

            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, check=check)
            except TimeoutError:
                await ctx.author.send("You took too long to respond. Please try again.")
                return

            department2 = self.departments[str(reaction.emoji)]

        # Insert the user into the database
        user_data = {"discordid": discord_id, "department": [department1, department2], "name" : ctx.author.name}
        try:
            self.collection.insert_one(user_data)
            await ctx.author.send(f"You are successfully registered with {department1} as Primary and {department2} as Secondary department")
        except Exception as e:
            await ctx.author.send("An error occurred while registering. Please try again later.")
            print(f"Error inserting data into MongoDB: {e}")

async def setup(client):
    await client.add_cog(Register(client))