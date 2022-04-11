import discord
import asyncio
import pygsheets
import gc

ranks = ["PVT","PFC","SPC","CPL","SGT","SSG","SFC","MSG","1SG","SGM","CSM","WO","2ndLT","1stLT","CPT","MAJ","LTC","COL","CMD","XO","BCMD"]

activity = ["Active","Semi-Active","Inactive","LOA","ROA","Purge","Rank Freeze"]

specializations = ["HVO","MED","HVY","SUP","ARF","ARC","HVOO","MEDO","MEDL","HVYO","HVYL","SUPO","SUPL","ARFO","ARFL","ARCO","ARCL","REGL"]

subunits = ["Vaughn","332ndO","332nd","Appo","TCXO","TC"]



# CHANGE THESE WITH EACH NEW ROSTER!
tagcol = 7
activitycol = 8
rankcol = 2
speccol = 10
promocol = 12
subcol = 11
notecol = 9
steamcol = 6
namecol = 5
specdefault = 'N/A'
subdefault = 'N/A'
rankdefault = 'Purge'
rankadd = 'PVT'
rankremove = 'Vacant'
actdefault = 'Active' #IF CHANGING, CHANGE RECRUITMENT METHOD
actremove = 'N/A'
tagdefault = ''
loredefault = ''
steamdefault = ''
namedefault = ''
promodefault = ''
promoterdefault = ''
notedefault = ''
roster_key = '1LqWf4g4cmzqWnGzkweLl24dUEf0Z5XHZb2hDDEtPWzc'
worksheet_name = '501st Roster'
#edit remove and recruit value lists


## CHANGE WITH EACH NEW ROSTER



def sheet():
    gc = pygsheets.authorize(service_file='client_secret.json')
    target = gc.open_by_key(roster_key).worksheet_by_title(worksheet_name)
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
    value_list = [[None,rankremove,None,namedefault,loredefault,steamdefault,tagdefault,actremove,notedefault,specdefault,subdefault,promodefault,promoterdefault,'FALSE',None,None,None,None]]
    # CHANGE
    target.update_row(rowcount, value_list)
    del cells, target, tag, rowcount, value_list, arg
    gc.collect()


async def recruit(arg1, arg2, nickname, timestamp):
    cells, target = sheet()
    tag = str(arg1)
    steamid = str(arg2)

    rowcount = await checktag(cells, rankremove, rankcol)
    if rowcount == False:
        return False
    #CHANGE
    value_list = [[None,rankadd,None,nickname,loredefault,steamid,tag,actdefault,notedefault,specdefault,subdefault,timestamp,promoterdefault,'FALSE',None,None,None,None]]
    #CHANGE
    target.update_row(rowcount, value_list)
    del cells, target, tag, steamid, rowcount, value_list, arg1, arg2, nickname, timestamp
    gc.collect()


