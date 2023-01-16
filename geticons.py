import sqlite3, base64

conn = sqlite3.connect('servers.db')
c = conn.cursor()
c.execute("""SELECT ip, icon FROM ping WHERE icon LIKE '%data%'""")
data = c.fetchall()
conn.close()

for ip, img in data:
    img = img.replace('data:image/png;base64,', '')
    with open('./favicons/'+ip+'.png', 'wb') as f:
        f.write(base64.b64decode(img))