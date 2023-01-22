from datetime import datetime
import locale
import random

'''
@Author: Sueño (Swen) Keijer
@Date: 16-01-2023
@Description:
    _PART 1: Stationszuil_
    In dit programma vragen we de reizigers om hun naam, een berichtje over het station.
    Welk station maakt niet uit, we pakken een random station van de lijst uit stations.txt (een bestand in dezelfde folder met stations namen erin).
    Vervolgens wordt de datum en tijd toegevoegd aan de review, en wordt het opgeslagen in een .csv bestand.
'''

# ---------------------------METHODS---------------------------

def getName():
    naam = input("Wat is uw naam? (leeg laten indien u anoniem wilt blijven):\n")
    
    if len(naam.strip()) == 0:
        return "Anoniem"
    return naam
    
def getDate():
    return datetime.now()
    
def pickRandomStation():
    stations = open('stations.txt', 'r')
    stationsList = stations.read().splitlines()
    return random.choice(stationsList)
    
# ---------------------------MAIN ROUTINE---------------------------

while True:
    bericht = input('Type hier uw bericht (max 140 tekens):\n')
    
    if len(bericht) > 140:
        print("ERROR: het bericht is te lang. Probeer opnieuw.")
        continue
    if len(bericht.strip()) == 0:
        print("ERROR: u hebt niks ingevoerd. Probeer opnieuw.")
    
    review = "{},{},Zaandam,{}\n".format(bericht, getName(), getDate())
    
    csvFile = open('reviews.csv', 'a')
    csvFile.write(review)
    print("Gelukt! Uw bericht is opgestuurd.")
    break
