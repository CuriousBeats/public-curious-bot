
import discord
import asyncio
from discord.ext import commands
import ffwebscrape
import sys
import os
import pygsheets

from dotenv import load_dotenv
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot("`",intents=intents)
loop = asyncio.get_event_loop()

async def sigterm_handler(_signo, _stack_frame):
    sys.exit(0)

def returncells(dockey,sheet):
    gc = pygsheets.authorize(service_file='client_secret.json')
    target = gc.open_by_key(dockey).worksheet_by_title(sheet)
    cells = target.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
    return cells

@bot.event
async def on_ready():
     print('We have logged in as {0.user}'.format(bot))


@bot.command()
async def followshelp(ctx):
    await ctx.send("The follows command accepts fanfiction.net, archiveofourown, and wattpad author profile links. Please ensure your link is not to a story."
             "\n\n"
             "``` \nTo submit a fanfiction.net link, please follow the format of:\n\n`follows https://www.fanfiction.net/~curiousbeats \n\n\n "
             "To submit an AO3 link, please follow the format of: \n\n`follows https://archiveofourown.org/users/Curious_Beats\n\n\n"
             "To submit a wattpad link, please follow the format of: \n\n`follows https://www.wattpad.com/user/ctzuki_? ```\n "
             "If you still can't get the bot to work, please head over to the help desk, or ping a member of operations.")


@bot.command()
async def follows(ctx,arg):
    operations = bot.get_channel(892217665744175226)
    junkyard = bot.get_channel(762106442429104160)
    botschannel = bot.get_channel(762106441934307338)
    if "fanfiction.net/" in arg:
        platform = 0
    elif "archiveofourown.org/users/" in arg:
        platform = 1
    elif "wattpad.com/user/" in arg:
        platform = 2
    else:
        await ctx.send("Please submit an author's profile in the format follows [URL]."
                 " This bot supports ff.net, ao3, and wattpad links. For help with this command, please use `followshelp.")
        return False

    if ctx.channel == operations or ctx.channel == junkyard or ctx.channel == botschannel:
        follownum = ffwebscrape.followcount(arg,platform)
        if follownum == False:
            await ctx.send("Either this profile has no followers, or you submitted an invalid link. For help with this command, please use `followshelp.")
        else:
            message = "This author's profile score is {follownum}".format(follownum=follownum)
            await ctx.send(message)
    else:
        await ctx.send("You can\'t use that command in this channel. Please head over to the junkyard to count followers.")

load_dotenv()
TOKEN = os.getenv('CURIOUSBOT_TOKEN')
bot.run(TOKEN)



