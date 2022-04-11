import discord
import asyncio

async def run(ctx,bot,cells):
    cells = cells[:200]
    taglist = []
    guild_id = 762106441489973278
    missing = []
    guild_taglist = []
    cells = [c for c in cells if c != []]
    for i in cells:
        taglist.append(i[2])
    taglist = [t for t in taglist if t != '']
    taglist = [t for t in taglist if t != 'ignore']

    for guild in bot.guilds:
        if guild.id == guild_id:
            for member in guild.members:
                tag = member.name + "#" + member.discriminator
                guild_taglist.append(tag)
            for author_tag in taglist:
                if author_tag not in guild_taglist:
                    missing.append(author_tag)
            if missing != []:
                await ctx.send('These authors are no longer in the discord:')
                for i in missing:
                    await ctx.send(i)
            else:
                await ctx.send('All authors are in the discord!')
