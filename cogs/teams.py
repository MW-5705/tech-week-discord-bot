import discord
from discord.ext import commands
from cogs.connection import client
import random

db = client["Discord_bot"]
participation_collection = db["Participants"]
participation_ptr = participation_collection.find({}, {"_id":0})
participation_data = []
added_participants = []
index = 0

for i in participation_ptr:
    participation_data.append(i)
# for i in participation_data:
#     print(i)
    
def  categorise_participants(participants):
    departments = {"tech": [], "design":[], "content":[], "marketing":[]}
    for i in participants:
        if i.get('department') in departments.keys():
            departments[i["department"]].append(i["discordid"])
    for i in departments:
        if (len(departments[i]) != 0):
            random.shuffle(departments[i])
    return departments

def get_member(department, departments):
    if (len(departments[department]) != 0):
        member = departments[department].pop()
        # added_participants.append(member)
        return member
    return False

def teams_base(team_num, departments):
    teams = []
    for i in range(team_num):
        team_id = f"Team-{i+1}"
        team = {"team_id":team_id, "members" :[]}
        for key in departments:
            member = get_member(department=key,departments=departments)
            if (member):
                team["members"].append(member)
                added_participants.append(member)
            else:
                pass
        teams.append(team)
    return teams
                         
def make_four(teams, departments):
    for i in teams:
        while (len(i["members"]) < 4):
            for key in departments:
                member = get_member(department=key, departments=departments)
                if (member):
                    added_participants.append(member)
                    i["members"].append(member)
                    break

def add_left_members_2(teams,department, departments):
    if len(teams) == 1:
        member = get_member(department=department, departments=departments)
        teams[-1]["members"].append(member)
    else:   
        global index
        if index == 0:
            member = get_member(department=department, departments=departments)
            teams[index]["members"].append(member)
            added_participants.append(member)
            index = 1
        else:
            member = get_member(department=department, departments=departments)
            teams[index]["members"].append(member)
            added_participants.append(member)
            index = 0

def add_left_members(teams, department ,  departments):
    member = get_member(department=department, departments=departments)
    teams[-1]["members"].append(member)
    added_participants.append(member)

def form_teams():
    departments = categorise_participants(participants=participation_data)
    registration = len(participation_data)
    team_num = registration // 4
    teams = teams_base(team_num=team_num, departments=departments)
    make_four(teams=teams, departments= departments)
    random.shuffle(teams)
    team_added = []
    for department in departments:
        if len(teams) < len(participation_data)%4:
            while len(departments[department]) != 0:
                add_left_members_2(teams = teams, department = department, departments=departments)
        else:
             while len(departments[department]) != 0:
                add_left_members(teams = teams, department = department, departments=departments)
                team_added.append(teams.pop())

    teams.extend(team_added)
    return teams

class Teams(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Teams online")
        
    @commands.command(name="create_teams", help="Creates teams with even distribution of participants from all departments.")
    # @commands.has_role("ExBo")
    async def create_teams(self, ctx, team_size: int = 4):
        teams = form_teams()
        
        # Output teams in Discord channel
        for team in teams:
            names = []
            for mem in team["members"]:
                member = ctx.guild.get_member(mem)
                names.append(member.name)
            members = ', '.join(names)
            await ctx.author.send(f"Team ID: {team['team_id']}\nMembers: {members}")
        
        teams_data = db["Teams"]
        teams_old = teams_data.find({},{"_id":0})
        teams_old_list = []
        for i in teams_old:
            teams_old_list.append(i)
        if (len(teams_old_list) == 0):
            teams_data.insert_many(teams)
        else:
            count = 0
            for i in teams:
                for j in teams_old_list:
                    if j["members"] == i["members"]:
                        count +=1
                if (count == 0):
                    teams_data.insert_one(i)
                else:
                    pass
    @commands.command()
    async def show(self, ctx):
        for i in participation_data:
            print(i)


async def setup(client):
    await client.add_cog(Teams(client))