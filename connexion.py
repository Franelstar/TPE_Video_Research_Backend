import psycopg2
# pip install psycopg2-binary

con = psycopg2.connect(
    host='localhost',
    database='RechercheTPE',
    user='postgres',
    password='postgres', )

cur = con.cursor()

#res = cur.execute("INSERT INTO scene_lieux_scene(id_scene, id_lieu, probabilite) VALUES ('{}', '{}', '{}')".format(
 #                   1, int(4), 3))

#con.commit()

#print(res)

cur.execute("SELECT * FROM video WHERE titre = '{}' and duree = '{}' and nbre_frame = '{}' and video_file = '{}' and duree_str = '{}'".format(
            'rencontre.mp4', int(13), 337, '/home/franel/PycharmProjects/API_TPE/instance/uploads/chsniebqivegmgdqigox.mp4', '00:00:13.480'))
rows = cur.fetchall()
if not rows:
    print('vide')
else:
    print(rows[0][0])

for r in rows:
    print("id: {}, name: {}".format(r[0], r[1]))


cur.close()
con.close()
