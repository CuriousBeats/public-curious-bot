import discord
import asyncio
import pygsheets
import gc

ranks = ["Private", "Private First Class", "Specialist", "Corporal", "Sergeant", "Staff Sergeant",
         "Sergeant First Class", "Master Sergeant", "First Sergeant",
         "Sergeant Major", "Command Sergeant Major", "Warrant Officer", "Second Lieutenant", "First Lieutenant",
         "Captain", "Major",
         "Lieutenant Colonel", "Colonel", "Commander",
         "Executive Officer", "Battalion Commander"]

activity = ["Active", "Semi-active", "Inactive", "Legacy", "ROA", "LOA"]

specializations = ["Heavy Ordnance", "ARF", "ARC", "Support", "Heavy","Medic","Heavy Ordnance Lead",
                   "Medical Officer", "Medical Lead", "Heavy Officer", "Heavy Lead",
                   "Support Officer", "Support Lead", "ARF Officer", "ARF Lead", "ARC Officer", "ARC Lead",
                   "Regimental Lead", "Regimental Advisor", "Jedi"]

subunits = ["Green Company","Green Company Officer", "Green Company Deputy","Green Company Lead","Improcco Company"]



# CHANGE THESE WITH EACH NEW ROSTER!
tagcol = 6
activitycol = 4
rankcol = 2
speccol = 10
promocol = 7
subcol = 9
steamcol = 5
namecol = 3
specdefault = 'Trooper'
specremove = ''
subdefault = 'Elite Corps'
subremove = ''
rankdefault = 'Vacant'
rankadd = 'Private'
actdefault = 'Active' #IF CHANGING, CHANGE RECRUITMENT METHOD
actremove = ''
tagdefault = ''
steamdefault = ''
namedefault = ''
promodefault = ''
notedefault = ''
rosterkey = '1TFQaOu5Metdjl_cMab6NzZbz5oZXR7ol4vbLlNqaLNo'
worksheet = 'Main Roster'

#edit remove and recruit value lists


## CHANGE WITH EACH NEW ROSTER



def sheet():
    gc = pygsheets.authorize(service_file='client_secret.json')
    target = gc.open_by_key(rosterkey).worksheet_by_title(worksheet)
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


async def member_update(before, after, client, timestamp):
    if len(before.roles) < len(after.roles):

        Role = next(role for role in after.roles if role not in before.roles)

    elif len(after.roles) < len(before.roles):

        Role = next(role for role in before.roles if role not in after.roles)

    # looks really bad but this is actually more efficient. Only checks the roster if we care about the role
    if Role.name in ranks or Role.name in specializations or Role.name in subunits or Role.name in activity:
        cells, target = sheet()
        tag = await client.fetch_user(before.id)
        tag = str(tag)

        rolename = Role.name

        rowcount = await checktag(cells, tag, tagcol)
        if rowcount == False:
            return False

        if len(before.roles) < len(after.roles):
            if rolename in ranks and rolename != cells[rowcount-1][rankcol-1]:
                target.update_value((rowcount, rankcol), rolename)
                target.update_value((rowcount, promocol), timestamp)
            elif rolename in specializations and rolename != cells[rowcount-1][speccol-1]:
                target.update_value((rowcount, speccol), rolename)
            elif rolename in activity and rolename != cells[rowcount-1][activitycol-1]:
                target.update_value((rowcount, activitycol), rolename)
            elif rolename in subunits and rolename != cells[rowcount-1][subcol-1]:
                target.update_value((rowcount, subcol), rolename)


        # for when roles are removed
        elif len(after.roles) < len(before.roles):
            if rolename in ranks and rolename == cells[rowcount-1][rankcol-1]:
                target.update_value((rowcount, rankcol), rankdefault)
            elif rolename in specializations and rolename == cells[rowcount-1][speccol-1]:
                target.update_value((rowcount, speccol), specdefault)
            elif rolename in subunits and rolename == cells[rowcount-1][subcol-1]:
                target.update_value((rowcount, subcol), subdefault)
            elif rolename in activity and rolename == cells[rowcount-1][activitycol-1]:
                target.update_value((rowcount, activitycol), actdefault)



async def remove(arg):
    cells, target = sheet()
    tag = str(arg)

    rowcount = await checktag(cells, tag, tagcol)
    if rowcount == False:
        return False

    # CHANGE
    value_list = [[None,rankdefault,namedefault,actremove,steamdefault,tagdefault,promodefault,None,subremove,specremove,None,None,None,None,notedefault,None]]
    # CHANGE
    target.update_row(rowcount, value_list)
    del cells, target, tag, rowcount, value_list, arg
    gc.collect()


async def recruit(arg1, arg2, nickname, timestamp):
    cells, target = sheet()
    tag = str(arg1)
    steamid = str(arg2)

    rowcount = await checktag(cells, rankdefault, rankcol)
    if rowcount == False:
        return False
    #CHANGE
    value_list = [[None,rankadd,nickname,actdefault,steamid,tag,timestamp,None,subdefault,specdefault,None,None,None,None,notedefault,None]]
    #CHANGE
    target.update_row(rowcount, value_list)
    del cells, target, tag, steamid, rowcount, value_list, arg1, arg2, nickname, timestamp
    gc.collect()


