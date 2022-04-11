import discord
import asyncio

def rankcolumn(cells):
    counter = -1
    for i in cells[0]:
        counter += 1
        if i == "Author rank":
            return counter

async def matcher(tag, currentrole, ranklist, taglist):
    count = 0
    for i in taglist:
        if tag == i:
            if currentrole != ranklist[count]:
                return ranklist[count]
            else:
                return False
        elif count < 200:
            count += 1
        else:
            print('Rank Update Error')
            return False

async def start(ctx,bot,cells):
    rankcol = rankcolumn(cells)
    guild_id = 762106441489973278
    taglist = []
    ranklist = []
    authorranklist = ["Emerald Author {35000+}", "Prestige Author {15000+}", "Diamond Author {8000+}",
                      "Ruby Author {3000+}", "Gold Author {1500+}", "Silver Author {800+}", "Onyx Author {200+}",
                      "Bronze Author {0+}"]
    count = 0
    cells = cells[:200]
    cells = [c for c in cells if c != []]

    for i in cells:
        taglist.append(i[2])
        if count > 1:
            ranklist.append(i[rankcol])
        else:
            count += 1
    ranklist = [r for r in ranklist if r in authorranklist]
    taglist = [t for t in taglist if t != '']
    c = -1

    for guild in bot.guilds:
        if guild.id == guild_id:
            for member in guild.members:
                tag = member.name + "#" + member.discriminator
                if tag in taglist:
                    c += 1
                    nickname = member.display_name
                    for role in member.roles:
                        if role.name in authorranklist:
                            found = True
                            oldrole = role
                            break
                    if found == True:
                        found = False
                        newrolename = await matcher(tag, oldrole.name, ranklist, taglist)

                        if newrolename == False:
                            pass
                        else:
                            newrole = discord.utils.get(bot.get_guild(guild_id).roles, name=newrolename)
                            await member.add_roles(newrole)
                            await member.remove_roles(oldrole)
                            await ctx.send('Updated {name} from {old} to {new}!'.format(name=nickname, old=oldrole.name,new=newrolename))
                            del oldrole
                    else:
                        newrolename = await matcher(tag,'', ranklist, taglist)
                        if newrolename == False:
                            pass
                        else:
                            newrole = discord.utils.get(bot.get_guild(guild_id).roles, name=newrolename)
                            await member.add_roles(newrole)
                            await member.remove_roles(oldrole)
                            await ctx.send('Added {name} to {new}!'.format(name=nickname, new=newrolename))