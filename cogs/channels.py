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
        print("chala to sahi")
        guild = ctx.guild
        db = client["Discord_bot"]
        collection = db["Teams"]
        collection_channels = db["Channels"]
        teams_data = collection.find({},{"_id":0})
        teams_list = []
        teams_channels = []
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
            team_id = team["team_id"]
            text_channel = await guild.create_text_channel(name = f"{team_id}_text", overwrites = overwrites)
            voice_channel = await guild.create_voice_channel(name = f"{team_id}_voice", overwrites = overwrites)
            
            print(type(text_channel))
            print(type(voice_channel))
            channel = {"team_id" : team_id, "text_channel": text_channel.id, "voice_channel" : voice_channel.id}
            collection_channels.insert_one(channel)
        await ctx.send("Channels created")
   
   
        
        

async def setup(client):
    await client.add_cog(Channels(client))