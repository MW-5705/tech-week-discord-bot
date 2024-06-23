import discord
from discord.ext import commands 
import pymongo 

#connecting to database
myclient= pymongo.MongoClient("mongodb://localhost:27017/")
db=myclient["makeathon"]
collection= db["team_names"]


class ChangenameCommand(commands.Cog):
    def __init__(self,client):
        self.client=client

    @commands.Cog.listener()
    async def on_ready(self):
        print("ChangenameCommand is running")
    

    #command to change the channel name
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def rename_team(ctx,old_team_name:str ,*,new_name:str):
    
       #find the channel by name
       teamtext=discord.utils.get(ctx.guild.channels, name=old_team_name)
       teamvoice=discord.utils.get(ctx.guild.voice_channels, name=old_team_name)
       #Checking if channel exists
       if teamtext and teamvoice:
           #updating the database
           query= {"team_name": old_team_name}
           newvalue= {"$set":{"team_name":new_name}}
           collection.update_one(query,newvalue)
           for x in collection.find():
               print(x)

           #change the channels name
           await teamtext.edit(name=new_name)
           await teamvoice.edit(name=new_name)
           await ctx.send(f'team name changed from {old_team_name} to {new_name}')
       else:
           await ctx.send("team not found")



 