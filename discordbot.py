import interactions, sqlite3, datetime, os, multiprocessing, dotenv, pinger, ipaddress, socket

dotenv.load_dotenv('profile.env')

bot = interactions.Client(token=os.getenv('DISCORD_BOT_TOKEN'))

versionregex = [('1.19.3', 761),
                ('1.19.2', 760),
                ('1.19.1', 760),
                ('1.19', 759),
                ('1.18.2', 758),
                ('1.18.1', 757),
                ('1.18', 757),
                ('1.17.1', 756),
                ('1.17', 755),
                ('1.16.5', 754),
                ('1.16.4', 754),
                ('1.16.3', 753),
                ('1.16.2', 751),
                ('1.16.1', 736),
                ('1.16', 735),
                ('1.15.2', 578),
                ('1.15.1', 575),
                ('1.15', 573),
                ('1.14.4', 498),
                ('1.14.3', 490),
                ('1.14.2', 485),
                ('1.14.1', 480),
                ('1.14', 477),
                ('1.13.2', 404),
                ('1.13.1', 401),
                ('1.13', 393),
                ('1.12.2', 340),
                ('1.12.1', 338),
                ('1.12', 335),
                ('1.11.2', 316),
                ('1.11.1', 316),
                ('1.11', 315),
                ('1.10.2', 210),
                ('1.10.1', 210),
                ('1.10', 210),
                ('1.9.4', 110),
                ('1.9.3', 110),
                ('1.9.2', 109),
                ('1.9.1', 108),
                ('1.9', 107),
                ('1.8.9', 47),
                ('1.8.8', 47),
                ('1.8.7', 47),
                ('1.8.6', 47),
                ('1.8.5', 47),
                ('1.8.4', 47),
                ('1.8.3', 47),
                ('1.8.2', 47),
                ('1.8.1', 47),
                ('1.8', 47),
                ('1.7.10', 5),
                ('1.7.9', 5),
                ('1.7.8', 5),
                ('1.7.7', 5),
                ('1.7.6', 5),
                ('1.7.5', 4),
                ('1.7.4', 4),
                ('1.7.3', 4),
                ('1.7.2', 4)]

conn = sqlite3.connect('./test.db')

datalist = {}

def translate2versionNumber(version):
    for vers in versionregex:
        if vers[0]==version:
            return vers[1]
    return -1

def getComponents():
    return [
        interactions.Button(
        label = '<<',
        style = interactions.ButtonStyle.PRIMARY,
        custom_id = 'previousserver'
    ),
    interactions.Button(
        label = '>>',
        style = interactions.ButtonStyle.PRIMARY,
        custom_id = 'nextserver'
    )
    ]

def createServerEmbed(server, index, lastindex, searchoptions):
    # (1671117080733501935, '85.14.194.229', 761, 10, 'maenner auf liegefahrraedern haben keinen sex.', 0, '1.19.3', 0)

    ip = server[1]
    serverdescription = server[4]
    isColored = server[5]
    serverversion = server[6]
    ismodded = server[7]
    maxplayers = server[3]

    c = conn.cursor()
    c.execute('SELECT rowid FROM ping WHERE time = ? AND ip = ? AND protvers = ? AND maxplayers = ? AND desc = ? AND iscolored = ? AND version = ? AND ismodded = ?', server)
    c.execute('SELECT name FROM pingplayers WHERE pingid = ?', c.fetchone())
    players = c.fetchall()
    c.close()

    unpackplayers = ''
    if len(players)==0:
        unpackplayers = '⠀'
    for player in players:
        unpackplayers+=str(player[0])+'\n'

    if(ismodded):
        serverversion='``'+serverversion+'``'

    if isColored:
        serverdescription='``'+serverdescription+'``'

    return interactions.Embed(
        title=ip,
        description=serverdescription,
        footer=interactions.EmbedFooter(
        text='scan took place on '+str(datetime.datetime.fromtimestamp(server[0] // 1000000000))
    ),
        author=interactions.EmbedAuthor(
        name = searchoptions[:-2]+' ('+str(index)+'/'+str(lastindex)+')'
    ),
        fields=[interactions.EmbedField(
        name='Version',
        value=serverversion
    ), interactions.EmbedField(
        name = f'Players {str(len(players))}/{str(maxplayers)}',
        value = unpackplayers
    )],
        thumbnail = interactions.EmbedImageStruct(
            url=f'https://eu.mc-api.net/v3/server/favicon/{ip}'
        )
    )

@bot.event
async def on_ready():
    print(f'ready as {bot.me.name}')

@bot.command(name='scan',
             description='scan a server.',
             options=[
                interactions.Option(
                    name        = 'ip',
                    type        = interactions.OptionType.STRING,
                    description = 'The ip of the server u want to scan.',
                    required    =  True
                )
             ])
async def scan(ctx: interactions.CommandContext,
               ip):
    await ctx.defer()
    try:
        if ipaddress.ip_address(socket.gethostbyname(ip)).is_private:
            await ctx.send('I dont like that u tried to snoop in my network not nice ):')
            return
    except:
        pass
    try:
        p = multiprocessing.Process(target=pinger.main, args=(ip,))
        p.start()
        p.join(4)
        p.terminate()
    except Exception as e:
        await ctx.send('Ping errored.')
        print('Tell that admin else guy to fix this error.')
        print(e)
        return
    c = conn.cursor()
    c.execute('SELECT * FROM ping WHERE ip = ? ORDER BY time DESC', (ip,))
    datalist[str(ctx.channel_id)]                  = {}
    datalist[str(ctx.channel_id)]['servers']       = []
    datalist[str(ctx.channel_id)]['servers'].append(c.fetchone())
    datalist[str(ctx.channel_id)]['searchoptions'] = 'Scan of '+ip+'.--'
    datalist[str(ctx.channel_id)]['count']         =  0 
    
    c.close()

    if len(datalist[str(ctx.channel_id)]['servers'])==0 or datalist[str(ctx.channel_id)]['servers'][0]==None:
        await ctx.send(f'the scan u did to the ip {ip} was unsuccessful ):')
        return

    await ctx.send('', embeds=createServerEmbed(datalist[str(ctx.channel_id)]['servers'][datalist[str(ctx.channel_id)]['count']], datalist[str(ctx.channel_id)]['count']+1, len(datalist[str(ctx.channel_id)]['servers']), datalist[str(ctx.channel_id)]['searchoptions']), components=getComponents())



@bot.command(name='searchplayer',
             description='Search for player in database.',
             options=[
                interactions.Option(
                    name        = 'name',
                    type        = interactions.OptionType.STRING,
                    description = 'The name of the player u want to search for.',
                    required    = True
                )
             ])
async def searchplayer(ctx: interactions.CommandContext,
                 name: str = None):
    global datalist
    datalist[str(ctx.channel_id)]            = {}
    datalist[str(ctx.channel_id)]['servers'] = []
    datalist[str(ctx.channel_id)]['count']   = 0

    c = conn.cursor()
    c.execute('SELECT pingid FROM pingplayers WHERE name = ?', (name,))
    for serverid in c.fetchall():
        c.execute('SELECT * FROM ping WHERE rowid = ?', serverid)
        datalist[str(ctx.channel_id)]['servers'].append(c.fetchone())
    c.close()
    if len(datalist[str(ctx.channel_id)]['servers'])==0:
        await ctx.send('I dont know '+name+' ):')
        return
    await ctx.send('', embeds=createServerEmbed(datalist[str(ctx.channel_id)]['servers'][datalist[str(ctx.channel_id)]['count']], datalist[str(ctx.channel_id)]['count']+1, len(datalist[str(ctx.channel_id)]['servers']), 'Servers where '+name+' is on--'), components=getComponents())

@bot.command(
    name='server',
    description='Find a server with spesific atributes.',
    options = [
        interactions.Option(
            name        = 'description',
            description = 'Search for a keyword in description.',
            type        = interactions.OptionType.STRING,
            required    = False,
        ),
        interactions.Option(
            name        = 'iscolored',
            description = 'Check if the description is colord.',
            type        = interactions.OptionType.BOOLEAN,
            required    = False,
        ),
        interactions.Option(
            name        = 'ismodded',
            description = 'Check if the server is modded.',
            type        = interactions.OptionType.BOOLEAN,
            required    = False,
        ),
        interactions.Option(
            name        = 'version',
            description = 'Search for a spesific version.',
            type        = interactions.OptionType.STRING,
            required    = False,
        ),
        interactions.Option(
            name        = 'versiontext',
            description = 'Search for a server software like paper.',
            type        = interactions.OptionType.STRING,
            required    = False,
        ),
    ],
)
async def server(ctx: interactions.CommandContext,
                 description: str = None,
                 iscolored: bool = None,
                 ismodded: bool = None,
                 version: str = None,
                 versiontext: str = None):
    sqlcommand = 'SELECT * FROM ping WHERE maxplayers <> 0 '
    sqlarguments = []
    searchoptions= ''
    if description!=None:
        sqlcommand+='AND desc LIKE ? '
        sqlarguments.append(f'%{description}%')
        searchoptions+=f'description contains {description}, '
    if iscolored!=None:
        sqlcommand+='AND iscolored = ? '
        if iscolored:
            sqlarguments.append('1')
            searchoptions+='description is colored, '
        else:
            sqlarguments.append('0')
            searchoptions+='description is not colored, '
    if ismodded!=None:
        sqlcommand+='AND ismodded = ? '
        if ismodded:
            sqlarguments.append('1')
            searchoptions+='server is modded, '
        else:
            sqlarguments.append('0')
            searchoptions+='server is not modded, '
    if version!=None:
        sqlcommand+='AND protvers = ? '
        if translate2versionNumber(version)==-1:
            await ctx.send(f'Iam sorry but i dont know any version called "{version}".\nU can try a non snapshot from this https://wiki.vg/Protocol_version_numbers (and also 1.7.3 that isnt listed there for some reason).')
            return
        searchoptions+=f'version is {version}, '
        sqlarguments.append(str(translate2versionNumber(version)))
    if versiontext!=None:
        sqlcommand+='AND version LIKE ? '
        searchoptions+=f'version contains {versiontext}, '
        sqlarguments.append(f'%{versiontext}%')
    sqlcommand+='ORDER BY ip DESC'
    
    c = conn.cursor()

    c.execute(sqlcommand, tuple(sqlarguments))
    global datalist
    datalist[str(ctx.channel_id)]                  = {}
    datalist[str(ctx.channel_id)]['count']         = 0
    datalist[str(ctx.channel_id)]['servers']       = c.fetchall()
    datalist[str(ctx.channel_id)]['searchoptions'] = searchoptions

    c.close()

    if len(datalist[str(ctx.channel_id)]['servers'])==0:
        await ctx.send('the search u did did not yield any results ):')
        return

    await ctx.send('', embeds=createServerEmbed(datalist[str(ctx.channel_id)]['servers'][datalist[str(ctx.channel_id)]['count']], datalist[str(ctx.channel_id)]['count']+1, len(datalist[str(ctx.channel_id)]['servers']), datalist[str(ctx.channel_id)]['searchoptions']), components=getComponents())

@bot.component('previousserver')
async def button_response(ctx: interactions.ComponentContext):
    ctx.defer()
    global datalist
    if str(ctx.channel_id) not in datalist or len(datalist[str(ctx.channel_id)])==0:
        await ctx.edit('I dont have any servers selected do /server', embeds=None, components=[])
        return
    datalist[str(ctx.channel_id)]['count']-=1
    if datalist[str(ctx.channel_id)]['count']<=1:
        datalist[str(ctx.channel_id)]['count']+=1
        await ctx.edit('')
        return
    await ctx.edit('', embeds=createServerEmbed(datalist[str(ctx.channel_id)]['servers'][datalist[str(ctx.channel_id)]['count']], datalist[str(ctx.channel_id)]['count']+1, len(datalist[str(ctx.channel_id)]['servers']), datalist[str(ctx.channel_id)]['searchoptions']), components=getComponents())


@bot.component('nextserver')
async def button_response(ctx):
    ctx.defer()
    global datalist
    if str(ctx.channel_id) not in datalist or len(datalist[str(ctx.channel_id)])==0:
        await ctx.edit("I don't have any servers selected do /server", embeds=None, components=[])
        return
    datalist[str(ctx.channel_id)]['count']+=1
    if datalist[str(ctx.channel_id)]['count']>=len(datalist[str(ctx.channel_id)]['servers']):
        datalist[str(ctx.channel_id)]['count']=len(datalist[str(ctx.channel_id)]['servers'])
        await ctx.edit('')
        return
    await ctx.edit('', embeds=createServerEmbed(datalist[str(ctx.channel_id)]['servers'][datalist[str(ctx.channel_id)]['count']], datalist[str(ctx.channel_id)]['count']+1, len(datalist[str(ctx.channel_id)]['servers']), datalist[str(ctx.channel_id)]['searchoptions']), components=getComponents())

@bot.command(name='asfile',
             description='Upload all selected ips to the null pointer.')
async def asfile(ctx):
    await ctx.defer()
    global datalist
    if str(ctx.channel_id) not in datalist or len(datalist[str(ctx.channel_id)])==0:
        await ctx.send("I don't have any servers selected do /server", embeds=None, components=[])
        # proper grammar
        return
    if len(datalist[str(ctx.channel_id)]['servers']) == 1:
        await ctx.send('Cmon man u really need to upload 1 ip?')
        await ctx.send('I can tell u here rn the ip is {}.'.format(datalist[str(ctx.channel_id)]['servers'][0][1]))
        return
    filestr = ''
    servers = []
    for server in datalist[str(ctx.channel_id)]['servers']:
        if server[1] not in servers:
            servers.append(server[1])
    for server in servers:
        filestr+=server+'\n'
    with open('ips.txt', 'w') as f:
        f.write(filestr)
    filelink = os.popen(f"curl -F'file=@ips.txt' http://0x0.st", ).read()
    await ctx.send(f'i uploaded all ips to '+filelink)
    
bot.start()
conn.commit()
conn.close()