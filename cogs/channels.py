import discord
from discord.ext import commands
from cogs.connection import client

class Channels(commands.Cog):
    def __init__(self,client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Channels online")
    
    @commands.command()
    @commands.has_role("ExBo")
    async def channel(self, ctx):
        guild = ctx.guild
        db = client["Discord_bot"]
        collection = db["Teams"]
        teams_data = collection.find({},{"_id":0})
        teams_list = []
        for team in teams_data:
            teams_list.append(team)
        for team in teams_list:
            members = []
            for i in team["members"]:
                members.append(i)
            overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages = False)}
            for i in members:
                member = guild.get_member(i)
                overwrites[member] = discord.PermissionOverwrite(read_messages = True)
            await guild.create_text_channel(name = team["team_id"], overwrites = overwrites)
            await guild.create_voice_channel(name = team["team_id"], overwrites = overwrites)
        await ctx.send("Channels created")

async def setup(client):
    await client.add_cog(Channels(client))