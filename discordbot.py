import interactions, sqlite3, datetime, os, pathlib, dotenv

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

datalist = []
serverindex = 0
searchoptions = ''


def translate2versionNumber(version):
    for vers in versionregex:
        if vers[0]==version:
            return vers[1]

def createServerEmbed(server, index, lastindex):
    # (1671117080733501935, '85.14.194.229', 761, 10, 'maenner auf liegefahrraedern haben keinen sex.', 0, '1.19.3', 0)

    ip = server[1]
    serverdescription = server[4]
    isColored = server[5]
    serverversion = server[6]
    ismodded = server[7]
    maxplayers = server[3]
    global searchoptions

    c = conn.cursor()
    c.execute('SELECT rowid FROM ping WHERE time = ? AND ip = ? AND protvers = ? AND maxplayers = ? AND desc = ? AND iscolored = ? AND version = ? AND ismodded = ?', server)
    c.execute('SELECT name FROM pingplayers WHERE pingid = ?', c.fetchone())
    players = c.fetchall()
    c.close()

    unpackplayers = '⠀'
    for player in players:
        unpackplayers+=str(player[0])+'\n'

    embedfooter = interactions.EmbedFooter(
        text='scan took place on '+str(datetime.datetime.fromtimestamp(server[0] // 1000000000))
    )

    if(ismodded):
        serverversion='``'+serverversion+'``'

    indexautherfield = interactions.EmbedAuthor(
        name = searchoptions[:-2]+' ('+str(index)+'/'+str(lastindex)+')'
    )

    playersfield = interactions.EmbedField(
        name = f'Players {str(len(players))}/{str(maxplayers)}',
        value = unpackplayers
    )

    serverversionfield = interactions.EmbedField(
        name='Version',
        value=serverversion
    )

    if isColored:
        serverdescription='*'+serverdescription+'*'

    return interactions.Embed(
        title=ip,
        description=serverdescription,
        footer=embedfooter,
        author=indexautherfield,
        fields=[serverversionfield, playersfield]
    )

@bot.event
async def on_ready():
    print(f'ready as {bot.me.name}')

@bot.command(name='searchplayer',
             description='Search for player in database.',
             options=[
                interactions.Option(
                    name = 'name',
                    type = interactions.OptionType.STRING,
                    description = 'The name of the player u want to search for.',
                    required    = True
                )
             ])
async def server(ctx: interactions.CommandContext,
                 name: str = None):
    global serverindex
    serverindex = 0
    global datalist
    datalist = []
    global searchoptions
    searchoptions = 'Servers where '+name+' is on--'

    c = conn.cursor()
    c.execute('SELECT pingid FROM pingplayers WHERE name = ?', (name,))
    for serverid in c.fetchall():
        c.execute('SELECT * FROM ping WHERE rowid = ?', serverid)
        datalist.append(c.fetchone())
    c.close()
    if len(datalist)==0:
        await ctx.send('the search u did did not yield any results ):')
        return

    button1 = interactions.Button(
        label = '<<',
        style = interactions.ButtonStyle.PRIMARY,
        custom_id = 'previousserver'
    )

    button2 = interactions.Button(
        label = '>>',
        style = interactions.ButtonStyle.PRIMARY,
        custom_id = 'nextserver'
    )

    await ctx.send('', embeds=createServerEmbed(datalist[serverindex], serverindex+1, len(datalist)), components=[button1, button2])

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
    global searchoptions
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

    global serverindex
    serverindex = 0
    global datalist
    datalist = c.fetchall()

    c.close()

    if len(datalist)==0:
        await ctx.send('the search u did did not yield any results ):')
        return

    button1 = interactions.Button(
        label = '<<',
        style = interactions.ButtonStyle.PRIMARY,
        custom_id = 'previousserver'
    )

    button2 = interactions.Button(
        label = '>>',
        style = interactions.ButtonStyle.PRIMARY,
        custom_id = 'nextserver'
    )

    await ctx.send('', embeds=createServerEmbed(datalist[serverindex], serverindex+1, len(datalist)), components=[button1, button2])

@bot.component('previousserver')
async def button_response(ctx):
    global serverindex
    global datalist
    serverindex-=1
    if len(datalist)==0:
        await ctx.edit('I dont have any servers selected do /server', embeds=None, components=[])
        return
    if serverindex<0:
        serverindex+=1
        await ctx.edit('')
        return
    
    button1 = interactions.Button(
        label = '<<',
        style = interactions.ButtonStyle.PRIMARY,
        custom_id = 'previousserver'
    )

    button2 = interactions.Button(
        label = '>>',
        style = interactions.ButtonStyle.PRIMARY,
        custom_id = 'nextserver'
    )
    await ctx.edit('', embeds=createServerEmbed(datalist[serverindex], serverindex+1, len(datalist)), components=[button1, button2])

@bot.component('nextserver')
async def button_response(ctx):
    global serverindex
    global datalist
    serverindex+=1
    if len(datalist)==0:
        await ctx.edit('I dont have any servers selected do /server', embeds=None, components=[])
        return
    if serverindex>=len(datalist):
        serverindex-=1
        await ctx.edit('')
        return
    button1 = interactions.Button(
        label = '<<',
        style = interactions.ButtonStyle.PRIMARY,
        custom_id = 'previousserver'
    )

    button2 = interactions.Button(
        label = '>>',
        style = interactions.ButtonStyle.PRIMARY,
        custom_id = 'nextserver'
    )
    await ctx.edit('', embeds=createServerEmbed(datalist[serverindex], serverindex+1, len(datalist)), components=[button1, button2])

bot.start()
