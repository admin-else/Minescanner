import sqlite3, time, util
from flask import Flask, jsonify, request, redirect, render_template
from flask import request
import numpy as np

from pprint import pprint

app = Flask(__name__)
conn = sqlite3.connect('servers.db', check_same_thread=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/servers', methods=['GET'])
def get_servers():
    """
    page     # the page
    limit    # items per page default 20
    motd     # seracges for motd
    maxage   # maximal age in minutes
    protvers # 760 for ex
    iscolored# 1for yes 0for no
    pplon    # players on
    versname # for ex paper
    ismodded # 1yes 0no

    """
    page      = request.args.get('page',     default = 1,    type = int)
    limit     = request.args.get('limit',    default = 20,   type = int)
    motd      = request.args.get('motd',     default = None, type = str)
    maxage    = request.args.get('maxage',   default = None, type = int) #in minutes
    protvers  = request.args.get('protvers', default = None, type = int)
    iscolored = request.args.get('iscolored',default = None, type = int)
    pplon     = request.args.get('pplon',    default = None, type = int)
    versname  = request.args.get('versname', default = None, type = str)
    ismodded  = request.args.get('ismodded', default = None, type = int)



    # Eastereggs

    if motd!=None and motd.lower()=='trolman':
        print('We catched a troll XD')
        return redirect('https://www.youtube.com/watch?v=neJJVYApU8Q?Autoplay=1', code=302)

    sqlparams = []
    sqlcmd = 'SELECT * FROM ping WHERE uptodate = 1 '

    if motd!=None:
        sqlcmd+='AND desc LIKE ? '
        sqlparams.append(f'%{motd}%')

    if maxage!=None:
        time_ns = time.time_ns()
        time_ns -=60000000000*maxage
        sqlcmd+='AND time > ? '
        sqlparams.append(time_ns)

    if protvers!=None:
        sqlcmd+='AND protvers = ? '
        sqlparams.append(protvers)

    if iscolored!=None:
        sqlcmd+='AND iscolored = ? '
        sqlparams.append(iscolored)

    if pplon!=None:
        sqlcmd+='AND pOn <= ? '
        sqlparams.append(pplon)

    if versname!=None:
        sqlcmd+='AND verstext LIKE ? '
        sqlparams.append(f'%{versname}%')

    if ismodded!=None:
        sqlcmd+='AND ismodded = ? '
        sqlparams.append(ismodded)

    sqlcmd += 'ORDER BY time DESC'

    c = conn.cursor()
    c.execute(sqlcmd, tuple(sqlparams))
    rawdata = c.fetchall()
    c.close()

    pages = list(util.chunk_pad(rawdata, limit))

    if len(pages)==0:
        return jsonify({'error': 'Search did not yield any results'})
    
    if len(pages)<page:
        return jsonify({'error': 'Page out of rage.'})

    data = pages[page-1]

    data = [util.s_to_dict(ping_data) for ping_data in data if ping_data!=None]

    data = {
        'servers': data,
        'lastpage': len(pages),
        'page': page,
        'totalserver': len(rawdata)
    }

    return jsonify(data)

if __name__ == '__main__':
    app.run()
    conn.close()


# HAHAHA l trolman i dont care