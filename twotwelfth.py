import gc
import discord
import asyncio
import pygsheets

ranks = ["Private", "Private First Class", "Specialist", "Corporal", "Sergeant", "Staff Sergeant",
         "Sergeant First Class", "Master Sergeant", "First Sergeant",
         "Sergeant Major", "Command Sergeant Major", "Warrant Officer", "2nd Lieutenant", "1st Lieutenant", "Captain",
         "Major",
         "Lieutenant Colonel", "Colonel", "Commander",
         "Executive Officer", "Commander Cody"]

activity = ["Active", "Semi-Active", "Inactive", "Legacy", "ROA", "LOA", "Rank Freeze"]

specializations = ["Heavy Ordnance", "ARF", "ARC", "Support", "Heavy", "High Command", "Medic", "HVO Trainer",
                   "Medical Officer", "Medical Lead", "Heavy Officer", "Heavy Lead",
                   "Support Officer", "Support Lead", "ARF Officer", "ARF Lead", "ARC Officer", "ARC Lead",
                   "Regimental Lead", "Regimental Advisor"]

subunits = ["Ghost Company", "GCS", "GCO", "GCXO", "GCC", "2nd Airborne", "2ndACS", "2ndACO", "Bear", "Barlex",
            "Red Squad Trainee", "Red Squad", "Red Squad XO", "Oddball"]

lorenames = ["Commander Cody", "Obi-Wan Kenobi", "Barlex", "Bear", "Parjai", "Oddball", "Goji", "Rod", "Engle", "Killer", "Waxer", "Boil",
             "Reed", "Cale", "Crys", "Gearshift", "Wooley", "Trapper", "Threepwood", "Eyeball", "Longshot", "Peel", "Goldie", "Switchblade"]
airborne = ["Former Barlex/Bear","Former Parjai","2ndAC Distinguished"]
ghost_company = ["Former GCC/GCXO","GC Distinguished","Honorary GC"]
# CHANGE THESE WITH EACH NEW ROSTER!
tagcol = 6
activitycol = 7
rankcol = 2
speccol = 10
promocol = 8
subcol = 11
lorecol = 12
steamcol = 5
loredefault = 'None'
specdefault = 'Trooper'
specremove = 'Vacant'
subdefault = 'None'
rankdefault = 'Vacant'
actdefault = 'Active'
actadd = 'Active'
actremove = 'Vacant'
tagdefault = ''
steamdefault = 'SteamID'
namedefault = '~Name~'
promodefault = ''
recruitremove = ''
notedefault = ''
rankadd = 'Private'
roster_key = '1-_lptys2YH3IYrir5SRaQI0M6CTCfqGkEUYg-G2T4oE'
worksheet_name = 'Roster'
legacy_name = 'Legacy Roster'
# edit remove and recruit value lists


tzdefault = '--'
tzadd = 'EST'


# 212th is dumb, remove above
# CHANGE THESE WITH EACH NEW ROSTER!


def sheet(key,targetsheet):
    gc = pygsheets.authorize(service_file='client_secret.json')
    target = gc.open_by_key(key).worksheet_by_title(targetsheet)
    cells = target.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
    return cells, target


async def checktag(cells, tag, tagcol):
    rowcount = 0
    for i in cells:
        rowcount += 1
        try:
            if i[tagcol - 1] == tag:
                coords = rowcount
                return coords
        except IndexError:
            pass
    try:
        rowcount = coords
        return rowcount
    except:
        return False


async def legacy(rolename,cells,tag,rowcount):
    steamid = cells[rowcount-1][4]
    name = cells[rowcount-1][3]
    legcells,legtarget = sheet(roster_key,legacy_name)
    legrowcount = 5
    if rolename in airborne:
        for i in legcells[5:]:
            legrowcount +=1
            if i[8] == "2ndAC":
                if i[9] == "-":
                    break
    elif rolename in ghost_company:
        legrowcount +=1
        for i in legcells[5:]:
            if i[8] == "Ghost Company":
                ghostrow = legrowcount
                break
        for i in legcells[ghostrow:]:
            legrowcount +=1
            if i[8] == "Ghost Company":
                if i[9] == "-":
                    break
    values = [[rolename,name,tag,steamid]]
    legtarget.update_row(legrowcount,values,col_offset = 9)

async def member_update(before, after, client, timestamp):
    if len(before.roles) < len(after.roles):

        Role = next(role for role in after.roles if role not in before.roles)

    elif len(after.roles) < len(before.roles):

        Role = next(role for role in before.roles if role not in after.roles)

    # looks really bad but this is actually more efficient. Only checks the roster if we care about the role
    if Role.name in ranks or Role.name in specializations or Role.name in subunits or Role.name in activity or Role.name in lorenames or Role.name in airborne or Role.name in ghost_company:

        cells, target = sheet(roster_key,worksheet_name)
        tag = await client.fetch_user(before.id)
        tag = str(tag)

        rolename = Role.name
        rowcount = await checktag(cells, tag, tagcol)
        if rowcount == False:
            return 1

        # for when roles are added
        if len(before.roles) < len(after.roles):
            if rolename in subunits and rolename in lorenames and rolename != cells[rowcount-1][subcol-1] and rolename != cells[rowcount-1][lorecol-1]:
                target.update_value((rowcount,subcol),rolename)
                target.update_value((rowcount,lorecol),rolename)
            elif rolename in ranks and rolename != cells[rowcount-1][rankcol-1]:
                target.update_value((rowcount, rankcol), rolename)
                target.update_value((rowcount, promocol), timestamp)
            elif rolename in specializations and rolename != cells[rowcount-1][speccol-1]:
                target.update_value((rowcount, speccol), rolename)
            elif rolename in activity and rolename != cells[rowcount-1][activitycol-1]:
                target.update_value((rowcount, activitycol), rolename)
            elif rolename in subunits and rolename != cells[rowcount-1][subcol-1]:
                target.update_value((rowcount, subcol), rolename)
            elif rolename in lorenames and rolename != cells[rowcount-1][lorecol-1]:
                target.update_value((rowcount,lorecol), rolename)
            elif rolename in airborne or rolename in ghost_company:
                await legacy(rolename,cells,tag,rowcount)

        # for when roles are removed
        elif len(after.roles) < len(before.roles):
            if rolename in subunits and rolename in lorenames and rolename == cells[rowcount-1][subcol-1] and rolename == cells[rowcount-1][lorecol-1]:
                target.update_value((rowcount,subcol),subdefault)
                target.update_value((rowcount,lorecol),loredefault)
            elif rolename in ranks and rolename == cells[rowcount-1][rankcol-1]:
                target.update_value((rowcount, rankcol), rankdefault)
            elif rolename in specializations and rolename == cells[rowcount-1][speccol-1]:
                target.update_value((rowcount, speccol), specdefault)
            elif rolename in subunits and rolename == cells[rowcount-1][subcol-1]:
                target.update_value((rowcount, subcol), subdefault)
            elif rolename in activity and rolename == cells[rowcount-1][activitycol-1]:
                target.update_value((rowcount, activitycol), actdefault)
            elif rolename in lorenames and rolename == cells[rowcount-1][lorecol-1]:
                target.update_value((rowcount, lorecol), loredefault)


async def remove(arg):
    cells, target = sheet(roster_key,worksheet_name)
    tag = str(arg)

    rowcount = await checktag(cells, tag, tagcol)
    if rowcount == False:
        return False

    # CHANGE
    value_list = [
        [None, rankdefault, None, namedefault, steamdefault, tagdefault, actremove, promodefault, recruitremove,
         specremove, subdefault, loredefault, tzdefault, None, None, None, None,'~', None]]
    # CHANGE
    target.update_row(rowcount, value_list)


async def recruit(arg1, arg2, nickname, timestamp):
    cells, target = sheet(roster_key,worksheet_name)
    tag = str(arg1)
    steamid = str(arg2)

    rowcount = await checktag(cells, rankdefault, rankcol)
    if rowcount == False:
        return False
    actdefault = '=IFERROR(IFS($J{row} = "Jedi","Active",$J{row} <> "Jedi",IFS($B{row}="Private",IFS($C{row}>=21,"Inactive",$C{row}>=11,"Semi-Active",$C{row}>=0,"Active"),$B{row}="Private First Class",IFS($C{row}>=21,"Inactive",$C{row}>=11,"Semi-Active",$C{row}>=0,"Active"),$B{row}="Specialist",IFS($C{row}>=21,"Inactive",$C{row}>=11,"Semi-Active",$C{row}>=0,"Active"),$B{row}="Corporal",IFS($C{row}>=21,"Inactive",$C{row}>=11,"Semi-Active",$C{row}>=0,"Active"),$B{row}="Sergeant",IFS($C{row}>=61,"Inactive",$C{row}>=31,"Semi-Active",$C{row}>=0,"Active"),$B{row}="Staff Sergeant",IFS($C{row}>=61,"Inactive",$C{row}>=31,"Semi-Active",$C{row}>=0,"Active"),$B{row}="Sergeant First Class",IFS($C{row}>=61,"Inactive",$C{row}>=31,"Semi-Active",$C{row}>=0,"Active"),$B{row}="Master Sergeant",IFS($C{row}>=61,"Inactive",$C{row}>=31,"Semi-Active",$C{row}>=0,"Active"),$B{row}="First Sergeant",IFS($C{row}>=61,"Inactive",$C{row}>=31,"Semi-Active",$C{row}>=0,"Active"),$B{row}="Sergeant Major",IFS($C{row}>=61,"Inactive",$C{row}>=31,"Semi-Active",$C{row}>=0,"Active"),$B{row}="Command Sergeant Major",IFS($C{row}>=61,"Inactive",$C{row}>=31,"Semi-Active",$C{row}>=0,"Active"))),"Vacant")'.format(row=rowcount)
    actadd = actdefault

    # CHANGE
    value_list = [[None, rankadd, None, nickname, steamid, tag, actadd, timestamp, timestamp, specdefault, subdefault,
                   loredefault, tzadd, None, None, None, None, notedefault, None]]
    # CHANGE
    target.update_row(rowcount, value_list)



