import psycopg2
# pip install psycopg2-binary

label = []

file = open('oj.txt', "r")
for line in file:
    p = line.split('\t')
    p[1] = p[1].replace('\n', '')
    label.append(p)
file.close()

print(label)

#label.sort(key=lambda x: x[1])

# for i in label:
#    print(i[1].replace('_', ' '))

con = psycopg2.connect(
    host='localhost',
    database='RechercheTPE',
    user='postgres',
    password='postgres', )

cur = con.cursor()
for objet in label:
    res = cur.execute("INSERT INTO objets(id, name) VALUES ('{}', '{}')".format(objet[0], objet[1].replace('_', ' ').replace('\'', '')))

con.commit()

# print(res)

# rows = cur.fetchall()
# if not rows:
#    print('vide')
#else:
#    print(rows[0][0])

#for r in rows:
#    print("id: {}, name: {}".format(r[0], r[1]))

cur.close()
con.close()
