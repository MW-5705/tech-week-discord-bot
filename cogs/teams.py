import discord
from discord.ext import commands
from cogs.connection import cluster
from math import floor
import random

db = cluster["Discord_bot"]
participants_collection = db["Participants"]

order = {0:"tech", 1:"tech", 2:"design", 3:"presentation"}
added_participants = []
def categorize_participants(participation_data, preference):
    departments = {"tech":[], "design":[], "presentation":[]}
    for i in participation_data:
        departments[i["department"][preference]].append(i["discordid"])
    for i in departments:
        random.shuffle(departments[i])
    return departments

def get_member(department, departments, participation_data):
    if len(departments[department])!=0:
                member = departments[department].pop()
                for j in participation_data:
                    if j["discordid"] == member:
                        added_participants.append(j)
                        participation_data.remove(j)
                        break
                member_dict = {"discordid" : member, "department": department}
                return member_dict
    return False

def teams_base(team_num,departments, partcipation_data):
    teams = []
    for i in range(team_num):
        team = {"team_id" : f"Team-{i+1}", "members":[]}
        for i in order:
            member_dict = get_member(department=order[i],departments=departments, participation_data=partcipation_data)
            if (member_dict):
                team["members"].append(member_dict)
            else:
                pass
            
        teams.append(team)
    return teams

def remove_complete_teams(teams, teams_complete):
    team = 0
    while team < len(teams):
        if (len(teams[team]["members"]) == 4):
           teams_complete.append(teams[team])
           teams.remove(teams[team])
           
        else:
            team += 1

def complete_teams(teams, departments_2, participation_data):
    for i in teams:
        count = 0
        for j in i["members"]:
            if (j["department"] == order[count]): #can add condition for checking length over here
                count += 1
                checker = i["members"].index(j) + 1
                if (checker == len(i["members"]) and len(i["members"]) !=4):
                    while count < 4:
                        # if len(departments_2[order[count]]) != 0:
                        #     member = departments_2[order[count]].pop()
                        #     for data in participation_data:
                        #         if (data["discordid"] == member):
                        #             added_participants.append(data)
                        #             participation_data.remove(data)
                        #             break
                        member_dict = get_member(department=order[count], departments=departments_2, participation_data=participation_data)
                        if (member_dict):
                            index = i["members"].index(j)              
                            i["members"].append( member_dict)
                            if count < 4:
                                count+=1
                        else:
                            count+=1
                    break
                    
                # new.append(j)
            else:
                member_dict = get_member(department=order[count], departments=departments_2,participation_data=participation_data)
                if (member_dict):
                    index = i["members"].index(j)              
                    i["members"].insert(index, member_dict)
                    count+=1  
    



def form_teams(participation_data):
    
    teams_complete = []
    registrations = len(participation_data)
    team_num = registrations//4
    departments = categorize_participants(participation_data=participation_data, preference=0) # participanta divided on the basis of primary departments
    teams = teams_base(team_num=team_num, departments=departments, partcipation_data=participation_data)# team formation started/ basis of teams is order dictionary
    remove_complete_teams(teams=teams, teams_complete=teams_complete)# removing complete_teams
    departments_2 = categorize_participants(participation_data=participation_data, preference=1)# creating dictionary with secondary departments
    complete_teams(teams=teams, departments_2=departments_2, participation_data=participation_data)# completing all teams with remaining participants and their
    for team in teams:
        teams_complete.append(team)
    
    print(participation_data)
    print("hoii")
    if len(participation_data) == 3 or len(participation_data) == 4:
        team_final = {"team_id":f"Team-{len(teams_complete)+1}", "members":[]}
        for i in participation_data:
            team_final['members'].append({"discordid":i["discordid"], "department":i["department"][0]})
        teams_complete.append(team_final)
    elif len(participation_data) == 2:
        team_index = random.randint(0, len(teams_complete)-1)
        while len(teams_complete[team_index]["members"]) < 4:
            team_index = random.randint(0, len(teams_complete)-1)
            
        member_new = teams_complete[team_index]["members"].pop(0)
        team_final = {"team_id":f"Team-{len(teams_complete)+1}", "members":[member_new]}
        for i in participation_data:
            team_final['members'].append({"discordid":i["discordid"], "department":i["department"][0]})
        teams_complete.append(team_final)

    elif len(participation_data) == 1:
        team_index_0 = 0
        team_index_1 = 0
        while (team_index_0 == team_index_1):
            team_index_0 = random.randint(0, len(teams_complete)-1)
            team_index_1 = random.randint(0, len(teams_complete)-1)
        member_new_0 = teams_complete[team_index_0]["members"].pop(0)
        member_new_1 = teams_complete[team_index_1]["members"].pop(0)
        team_final = {"team_id":f"Team-{len(teams_complete)+1}", "members":[member_new_0, member_new_1]}
        for i in participation_data:
            team_final['members'].append({"discordid":i["discordid"], "department":i["department"][0]})
        teams_complete.append(team_final)


    else:
        print("check for proper making plisssss")
    for i in teams_complete:
        print(i)
    return teams_complete

class Teams(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Teams online")
        
    @commands.command(name="create_teams", help="Creates teams with even distribution of participants from all departments.")
    @commands.has_role("ExBo")
    async def create_teams(self, ctx, team_size: int = 4):
        print("works")
        participants_ptr = participants_collection.find({},{"_id":0, "name":0})
        print(participants_ptr)
        # for i in participants_ptr:
        #     print(i)
        participation_data = []
        for i in participants_ptr:
            participation_data.append(i)
            # print(i)
        print((participation_data))
        teams = form_teams(participation_data=participation_data)
        # print(teams)
    
        
        # Output teams in Discord channel
        for team in teams:
            names = []
            for mem in team["members"]:
                member = ctx.guild.get_member(mem["discordid"])
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
        # for i in participation_data:
        #     print(i)
        print("success")

async def setup(client):
    await client.add_cog(Teams(client))