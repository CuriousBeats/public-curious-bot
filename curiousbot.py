
import discord
import asyncio
from discord.ext import commands
from datetime import date
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import ffwebscrape
import signal
import rankupdater
import re
import warnings
import typing
import sys
import os
import pygsheets
import twotwelfth
import fortyfirst
import fiveofirst
import indexupdate
from dotenv import load_dotenv
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot("`",intents=intents)
loop = asyncio.get_event_loop()
run_senact = False
run_weekly = False
scheduler = AsyncIOScheduler()
warnings.filterwarnings('ignore','.*PytzU*.')
warnings.filterwarnings('ignore','.*apscheduler*.')
async def sigterm_handler(_signo, _stack_frame):
    sys.exit(0)

def returncells(dockey,sheet):
    gc = pygsheets.authorize(service_file='client_secret.json')
    target = gc.open_by_key(dockey).worksheet_by_title(sheet)
    cells = target.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
    return cells

senrosterkey = '1Kvsv4fIIyHaArm8UK3xqewlObpLPrltpXTdN8khx19k'
senrostersheet = 'Roster'
weeklysheet = 'Weekly Update'

@bot.event
async def on_ready():
     print('We have logged in as {0.user}'.format(bot))

     scheduler.add_job(runsenact,trigger='cron',hour=12,misfire_grace_time=1000)
     scheduler.add_job(weeklysenact,trigger='cron',day_of_week='mon',hour=12,misfire_grace_time=1000)
     scheduler.start()

@bot.command()
async def index(ctx):
    operations = bot.get_channel(892217665744175226)

    if ctx.channel == operations:
        key = "1sOxx1Q1nCj_5iwJ7ppEyb7_z7dEp7ATNK8qmkyqTO1Y"
        cells = returncells(key, 'Authorlist')
        await indexupdate.run(ctx,bot,cells)
    else:
        await ctx.send('do that in the operations channel, dipshit.')

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


async def runsenact():
    try:
        if sys.argv[1] == "handle_signal":
            signal.signal(signal.SIGTERM, sigterm_handler)

    except:
        pass
    cells = returncells(senrosterkey,senrostersheet)
    senatorlist = []
    for i in range(9,16):
       if cells[i][17] == 'Not Completed':
            hours = float(cells[i][13])
            if hours >= 0:
                hours = round(hours,2)
                if int(repr(hours)[-1]) == 0:
                    hours = int(hours)
                remain = round(3-hours,2)
                if int(repr(remain)[-1]) == 0:
                    remain = int(remain)
                hours = "{hours}/3".format(hours=hours)
                msgstr = "You have {hours} hours logged on your senator this week! You need to log {remain} more hour(s) before the end of the week.".format(hours=hours,remain=remain)
            elif hours < 0:
                msgstr = "You have not clocked out for every time you've clocked into the Senate activity log. Please make sure to clock out."
            senatortag = str(cells[i][10])
            guild_id = 517210947081732109
            for guild in bot.guilds:
                if guild.id == guild_id:
                    global run_senact
                    for member in guild.members:
                        tag = member.name + '#' + member.discriminator
                        if senatortag == tag:
                            if run_senact == False:
                                run_senact = True
                                senatorlist.append(tag)
                                await member.send(msgstr)
                                run_senact = False


async def weeklysenact():
    cells = returncells(senrosterkey,weeklysheet)
    senlist = []
    for i in cells:
        try:
            if i[5] == 'Not Completed' and i[0] != '':
                senlist.append(i[0])

        except IndexError:
            pass
    channel = bot.get_channel(857390021988712458)
    global run_weekly
    if run_weekly == False:
        run_weekly = True
        if senlist != []:
            names = ''
            for x in senlist:
                names += x
                names += '\n'


            message = "**The following senators did not complete their hours last week:**  \n\n {names}".format(names=names)
        elif senlist == []:
            message = "It appears that all senators met their activity requirements last week!"

        await channel.send(message)
        run_weekly = False


regimentalid = 469808708344348694
twotwelfthid = 391380127713591306
twotwelfthrecruit = 391381399480958977
twotwelfthremove =833384596275724308

fortyfirstid = 515718028483100677
fortyfirstrecruit = 717121555963969588
fortyfirstremove =717121555963969588

fiveofirstid = 323305828558045186
fiveofirstremove = 937460104243056721
fiveofirstrecruit = 937459972776792184

@bot.event
async def on_member_update(before, after):

    if len(before.roles) < len(after.roles) or len(after.roles) < len(before.roles):
        timestamp = date.today()
        timestamp = timestamp.strftime("%m/%d/%Y")
        guild_id = before.guild.id
        if guild_id == twotwelfthid or guild_id == regimentalid:
            await twotwelfth.member_update(before,after,bot,timestamp)
        elif guild_id == fortyfirstid:
            await fortyfirst.member_update(before,after,bot,timestamp)
        elif guild_id == fiveofirstid:
            await fiveofirst.member_update(before,after,bot,timestamp)



@bot.command()
async def remove(ctx, member : typing.Union[discord.Member, str]):
    guild_id = ctx.guild.id
    discordreg = '^.{2,32}#[0-9]{4}$'
    try:
        if isinstance(member, str) == False:
            arg = await bot.fetch_user(member.id)
        else:
            arg = member
    except:
        await ctx.send("There is an error with the DiscordID. Try again.")
        return

    match = re.match(discordreg,str(arg))
    channelerror = 'Sorry, but you can\'t do that in this channel. If you believe this to be a mistake speak to your intel director.'
    removed = '{remove} has been removed from the roster.'
    if match:

        if guild_id == twotwelfthid or guild_id == regimentalid:
            if ctx.channel.id == twotwelfthremove:
                await twotwelfth.remove(arg)
                await ctx.send(removed.format(remove=arg))

            else:
                await ctx.send(channelerror)

        elif guild_id == fortyfirstid:
            if ctx.channel.id == fortyfirstremove:
                await fortyfirst.remove(arg)

            else:
                await ctx.send(channelerror)


        elif guild_id == fiveofirstid:
            if ctx.channel.id == fiveofirstremove:
                await fiveofirst.remove(arg)
                await ctx.send(removed.format(remove=arg))

            else:
                await ctx.send(channelerror)


    else:
        await ctx.send('Please submit a discord tag to the command in the format `remove Jova#2259. If there is a space in the tag, put it in quotation marks in the format' 
                       ' remove \"Curious Beats#2276\" \(Note, you can also ping the added member instead of giving their tag.\)')

@bot.command()
async def recruit(ctx, Member: typing.Union[discord.Member, str], arg2):
    try:
        if isinstance(Member, str) == False:
            arg1 = str(await bot.fetch_user(Member.id))
        else:
            arg1 = str(Member)
    except:
        await ctx.send("There is an error with the DiscordID. Try again.")
        return
    discordreg = '^.{3,32}#[0-9]{4}$'
    steamreg = '^STEAM_[0-5]{1}:[0-1]{1}:[0-9]{8,9}$'

    match1 = re.match(discordreg, str(arg1))
    match2 = re.match(steamreg, arg2)

    if match1 and match2:
        channelerror = 'Sorry, but you can\'t do that in this channel. If you believe this to be a mistake speak to your intel director.'
        recruited = '{recruit} has been added to the roster.'
        guild_id = ctx.guild.id
        name, discrim = arg1.split('#')
        calledmember = discord.utils.get(ctx.guild.members, name=name, discriminator=discrim)
        timestamp = date.today()
        timestamp = timestamp.strftime("%m/%d/%Y")
        nickname = calledmember.display_name
        if guild_id == twotwelfthid or guild_id == regimentalid:
            if ctx.channel.id == twotwelfthrecruit:
                await twotwelfth.recruit(arg1,arg2,nickname,timestamp)
                await ctx.send(recruited.format(recruit=arg1))
            else:
                await ctx.send(channelerror)

        elif guild_id == fortyfirstid:
            if ctx.channel.id == fortyfirstremove:
                await fortyfirst.recruit(arg1,arg2,nickname,timestamp)

            else:
                await ctx.send(channelerror)

        elif guild_id == fiveofirstid:
            if ctx.channel.id == fiveofirstrecruit:
                await fiveofirst.recruit(arg1,arg2,nickname,timestamp)
                await ctx.send(recruited.format(recruit=arg1))

            else:
                await ctx.send(channelerror)

    else:
        await ctx.send('Please submit a discord tag and STEAMID to the command in the format `recruit Jova#2259 STEAM_0:1:79667671. If there is a space in the tag, put it in quotation marks in the format' 
                       ' recruit \"Curious Beats#2276\" STEAM_0:1:79667671 \(Note, you can also ping the added member instead of giving their tag.\)')

@bot.command()
async def rankupdate(ctx):
    if ctx.channel.id == 892217665744175226:
        key = "1sOxx1Q1nCj_5iwJ7ppEyb7_z7dEp7ATNK8qmkyqTO1Y"
        cells = returncells(key,'Authorlist')
        await rankupdater.start(ctx,bot,cells)

load_dotenv()
TOKEN = os.getenv('CURIOUSBOT_TOKEN')
bot.run(TOKEN)



