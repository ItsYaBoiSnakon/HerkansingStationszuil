'''
@Author: Sueño (Swen) Keijer
@Date: 18-01-2023
@Description:
    _PART 2: Moderators Screen_
    In dit programma gaat de moderator te werk.
    Er zijn functie's geschreven om de database aan te maken, te lezen en in te schrijven
    Vervolgens zijn er 2 main routines geschreven: de login en de reviews keuren
'''

# ---------------------------IMPORTS---------------------------

import csv
import psycopg2
from datetime import datetime

# ---------------------------FUNCTIONS---------------------------

'''
Maak een connectie met de database
'''
def makeConnection():
    conn = psycopg2.connect(
        dbname='projA',
        user='postgres',
        password='Sueno-2012',
        host='localhost',
        port='5432'
    )
    
    cur = conn.cursor()
    cur.execute(
                "CREATE TABLE IF NOT EXISTS review (id SERIAL PRIMARY KEY, bericht VARCHAR(140) NOT NULL, "
                "naam VARCHAR(40) NOT NULL, station VARCHAR(30) NOT NULL, datum TIMESTAMP NOT NULL); "
    
                "CREATE TABLE IF NOT EXISTS moderator (email VARCHAR(255) PRIMARY KEY, naam VARCHAR(40) NOT NULL);"
    
                "CREATE TABLE IF NOT EXISTS beoordeling (review_id INTEGER PRIMARY KEY REFERENCES review, goedgekeurd "
                "BOOLEAN NOT NULL, datum TIMESTAMP NOT NULL, moderator_email VARCHAR(255) REFERENCES moderator); "
    )
    
    return conn

def closeConnection(conn):
    conn.close()    
    
def uploadReviews(conn):
    try:
        
        csvFile = open('reviews.csv', 'r+')
        csvRead = csv.reader(csvFile, delimiter=",")
        reviews = list(csvRead)
        csvFile.truncate(0)
        # print(reviews)
        
        if len(reviews) > 0:
            print("Review(s) gevonden, start importing...")
            cur = conn.cursor()
            for review in reviews:
                cur.execute(
                    "INSERT INTO review (bericht, naam, station, datum)"
                    "VALUES (%s, %s, %s, %s)", review
                    )
            conn.commit()
            print("Succes! Alle reviews uploaded naar de server!")
            return
        print("Er zijn geen nieuwe reviews gevonden in reviews.csv")
        
    except FileNotFoundError:
        print("ERROR: Geen bestand met reviews gevonden")

def downloadReviews(conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT * "
        "FROM review r "
        "WHERE NOT EXISTS "
        "(SELECT * FROM beoordeling b WHERE b.review_id = r.id);"
    )
    return cur.fetchall()

def getModeratorName(conn, email):   
    cur = conn.cursor()
    cur.execute("SELECT naam FROM moderator "
                "WHERE moderator.email = %s;", [email])
    modName = cur.fetchone()

    if modName:
        return modName[0]

def makeModerator(conn, moderator_email, moderator_naam):
    cur = conn.cursor()
    
    cur.execute("INSERT INTO moderator (email, naam) "
                "VALUES (%s, %s);", [moderator_email, moderator_naam])
    
    conn.commit()

def insertBeoordeling(conn, beoordeling):
    cur = conn.cursor()
    
    cur.execute("INSERT INTO beoordeling (review_id, goedgekeurd, datum, moderator_email) "
                "VALUES (%s, %s, %s, %s)", beoordeling)
    conn.commit()
    
'''
# ---------------------------MAIN ROUTINE : LOGIN---------------------------
'''

print("\n---------------Moderator window---------------")

conn = makeConnection()

while True:
    
    email = input("Emailadres: ")
    if len(email.strip()) == 0:
        print("ERROR: Probeer opnieuw")
        continue    #Loop back if input is empty
    
    name = getModeratorName(conn, email)
    if name is not None:
        print("Welkom terug {}".format(name))
        break
    
    print("\n-- Onbekend email, account wordt aangemaakt --")
    while True:
        name = input("Naam: ")
        if len(name.strip()) == 0:
            print("ERROR: Probeer opnieuw")
            continue
        
        makeModerator(conn, email, name)
        print("Welkom {}".format(name))
        break
    break # in case the continue at the top didnt happen, and everything resolves, break the loop

'''    
# ---------------------------MAIN ROUTINE : CHECK REVIEWS---------------------------
'''

uploadReviews(conn)

reviews = downloadReviews(conn)
reviewNum = 1
for review in reviews:
    print("\nBericht {} van {}\nDate: {}\nName: {}\nPlaats: {}\nBericht: \n{}"\
    .format(reviewNum, len(reviews), datetime.strftime(review[4], "%d/%b/%Y, %H:%M:%S"), review[2], review[3], review[1]))
        
    while True:
        try:
            check = input("\nType 0 om af te keuren, type 1 om goed te keuren: ")
            dateBeoordeling = datetime.now()
            if int(check) == 1:                
                beoordelingOut = [review[0], True, dateBeoordeling, email]               
                print("Succesvol goedgekeurd!")
            elif int(check) == 0:
                beoordelingOut = [review[0], False, dateBeoordeling, email]               
                print("Succesvol afgekeurd!")
            else:
                raise ValueError
            insertBeoordeling(conn, beoordelingOut)
            reviewNum += 1
            break
        except ValueError:
            print("Verkeerde input, probeer opnieuw")
else:
    print("Er zijn geen reviews meer over, lekker gewerkt {}!".format(name))
    closeConnection(conn)

