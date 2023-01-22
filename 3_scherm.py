"""
@Author: Sueño (Swen) Keijer
@Date: 16-01-2023
@Description:
    
"""

# ---------------------------IMPORTS---------------------------

import csv
import psycopg2
import json
import requests
from datetime import datetime
from tkinter import *
API_Key = "fe52ea857c1dba7426d29f1ef6cdadd4"
# ---------------------------FUNCTIONS---------------------------

def makeConnection():
    conn = psycopg2.connect(
        dbname="projA",
        user="postgres",
        password="Sueno-2012",
        host="localhost",
        port="5432"
    )    
    return conn

def closeConnection(conn):
    conn.close()

def getRecentReviews(station):
    conn = makeConnection()
    cur = conn.cursor()
    cur.execute("SELECT r.bericht, r.naam FROM review AS r "
                "INNER JOIN beoordeling AS b ON r.id = b.review_id "
                "WHERE b.goedgekeurd = true AND station = %s "
                "ORDER BY r.datum DESC LIMIT 5", [station])
    return cur.fetchall()

def getweatherForecast(station):
    weather = requests.get("https://api.openweathermap.org/data/2.5/weather?q={},nl&lang=nl&APPID={}".format(station, API_Key))
    return json.loads(weather.content)

def getDate():
    return datetime.strftime(datetime.now(), "%d/%m/%Y, %H:%M:%S")
    
def getStationsList():
    file = open("stations.txt", "r")
    stationsList = file.read().splitlines()
    return stationsList
    
def getFacilities(station):
    conn = makeConnection()
    cur = conn.cursor()
    cur.execute("SELECT ov_bike, elevator, toilet, park_and_ride FROM station_service "
                "WHERE station_city=%s", [station])
    return cur.fetchone()

# ---------------------------START SCREEN---------------------------
  
class welcomeScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Selecteer station")
        self.container = Frame(self.root, width=400, height=250)
        self.container.pack_propagate(False)                        #stops shrinking
        self.container.pack(fill=BOTH, expand=True)

        stations = getStationsList()
        placeholder = StringVar()
        placeholder.set(stations[0])
        self.selected_station = stations[0]

        self.title = Label(
            self.container,
            text="Selecteer uw station",
            font=("Arial Black", 20, "bold")
        )
        self.select = OptionMenu(
            self.container,
            placeholder,
            *stations,
            command=self.set_selected_station
        )
        self.submit = Button(
            self.container,
            text="Select",
            command=self.submit_station
        )
        
        self.title.pack(pady=(50, 0), anchor=CENTER)
        self.select.pack(after=self.title, pady=(10, 0), anchor=CENTER)
        self.submit.pack(after=self.select, pady=(10, 0), anchor=CENTER)

    def set_selected_station(self, station):
        self.selected_station = station

    def submit_station(self):
        self.root.destroy()
        self.root = Tk()
        self.app = InfoScherm(self.root, self.selected_station)

# ---------------------------MAIN SCREEN---------------------------


class InfoScherm:
    def __init__(self, root, station):

        #Create start
        self.root = root
        self.root.title("Stationscherm")
        self.root.geometry("1000x600")

        #Create variables
        self.station = station
        self.facilities = getFacilities(self.station)
        self.weerbericht = getweatherForecast(self.station)
        self.reviews = getRecentReviews(self.station)

        #Create containers
        self.container = Frame(self.root)
        self.container.pack_propagate(False)
        self.container.pack(fill=BOTH, expand=True)

        self.container.columnconfigure(0, weight=1)
        self.container.columnconfigure(1, weight=3)
        self.container.columnconfigure(2, weight=3)
        self.container.rowconfigure(0, weight=2)
        self.container.rowconfigure(1, weight=3)
        self.container.rowconfigure(2, weight=3)
        self.container.rowconfigure(3, weight=1)


        self.title_container = Frame(self.container)
        self.title_container.grid(column=0, row=0, sticky=W, padx=30)
        self.title = Label(
            self.title_container,
            text="Welkom op station:",
            font=("Arial Black", 16),
            foreground="black"
        )
        self.title.grid(column=0, row=0, sticky=W)
        self.currentstation = Label(
            self.title_container,
            text=self.station,
            font=("Arial Black", 30, "bold"),
        )
        self.currentstation.grid(column=0, row=1)


        self.weerbericht_container = Frame(self.container)
        self.weerbericht_container.grid(column=2, row=0, sticky=E, padx=30)

        temperatuur = int(self.weerbericht["main"]["temp"]) - 273  # Kelvin naar Celsius
        weerbericht = self.weerbericht["weather"][0]


        # self.weerbericht_icon = Label(self.weerbericht_container)
        # self.weerbericht_icon.grid(column=0, row=0, rowspan=2)
        self.weerbericht_temp = Label(
            self.weerbericht_container,
            text="{}°".format(temperatuur),
            font=("Arial Black", 30, "bold")
        )
        self.weerbericht_temp.grid(column=1, row=0)
        self.weerbericht_desc = Label(
            self.weerbericht_container,
            text=weerbericht["description"].capitalize(),
            font=("Arial Black", 14)
        )
        self.weerbericht_desc.grid(column=1, row=1)

        types_facilities = ["ov_fiets", "lift" "toilet", "park_and_ride"]
        labels_facilities = ["OV-fiets", "Lift", "Toilet", "P&R"]
        self.facilities_container = Frame(self.container)
        self.facilities_container.grid(column=0, row=1, sticky=N, pady=(20, 0))
        self.facilities_container.columnconfigure(0, weight=1)
        self.facilities_container.columnconfigure(1, weight=1)
        self.facilities_container.columnconfigure(2, weight=1)
        self.facilities_container.columnconfigure(3, weight=1)

        self.facilities_list = []
        self.facilities_title = Label(
            self.facilities_container,
            text="Beschikbare faciliteiten:",
            font=("Arial Black", 16, "bold")
        )
        self.facilities_title.grid(column=0, row=0)

        for faciliteit in types_facilities:
            if self.facilities[types_facilities.index(faciliteit)]:
                faciliteit_container = Frame(self.facilities_container)
                faciliteit_container.grid(row=len(self.facilities_list)+1, column=0, columnspan=1, pady=5, sticky=W)
                faciliteit_container.grid(row=len(self.facilities_list)+1, column=0, columnspan=1, pady=5, sticky=W)

                faciliteit_label = Label(
                    faciliteit_container,
                    text="- "+labels_facilities[types_facilities.index(faciliteit)],
                    font=("Arial Black", 14)
                )
                faciliteit_label.grid(column=1, row=0, padx=10)

                self.facilities_list.append(faciliteit)

        self.reviews_container = Frame(self.container)
        self.reviews_container.grid(column=2, row=1, sticky=NW, pady=(40, 0))
        self.reviews_container.rowconfigure(0, weight=1)
        self.reviews_container.rowconfigure(1, weight=1)

        self.reviews_title = Label(
            self.reviews_container,
            text="Reviews:",
            font=("Arial Black", 16, "bold"),
        )
        self.reviews_title.grid(column=0, row=0, sticky=W)
        self.reviews_list = []

        if len(self.reviews) == 0:
            no_reviews = Label(
                self.reviews_container,
                text="Er zijn nog geen reviews van dit station.",
                font=("Arial Black", 13),
            )
            no_reviews.grid(column=0, row=1, sticky=W)
        for review in self.reviews:
            review_container = Frame(self.reviews_container)
            review_container.grid(column=len(self.reviews_list) % 2, columnspan=1, row=(len(self.reviews_list) // 2)+1, sticky=NW, pady=5)

            review_bericht = Label(
                review_container,
                text=review[0],
                font=("Arial Black", 14),
                wraplength=200,
                justify=LEFT
            )
            review_bericht.grid(row=0, column=0, sticky=W)
            review_naam = Label(
                review_container,
                text=f"- {review[1]}",
                font=("Arial Black", 12, "italic"),
                justify=LEFT
            )
            review_naam.grid(row=1, column=0, sticky=W)

            self.reviews_list.append(review)

        self.footer = Frame(self.container, width=600, height=50)
        self.footer.grid(column=0, row=3, columnspan=3, sticky=S, pady=(0, 10))

        self.datum = Label(
            self.footer,
            font=("Arial Black", 14),
        )
        self.datum.grid(column=0, row=0, sticky=W)

        def updateTime():
            self.datum.config(text = getDate())
            self.datum.after(1000, updateTime)
        updateTime()

# ---------------------------STARTUP---------------------------

if __name__ == "__main__":
    root = Tk()
    app = welcomeScreen(root)
    root.mainloop()
