import FreeSimpleGUI as sg
from stamp import Stamp, StampCollection
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "stamps.db")

class StampCollectionGUI:
    def __init__(self):
        self.collection = StampCollection()
        self._init_db()
        self._load_from_db()
        self.layout = [
            [sg.Text("Description"), sg.Input(key="description")],
            [sg.Text("Scott Number"), sg.Input(key="scott_number")],
            [sg.Checkbox("Used", key="used")],
            [sg.Button("Add Stamp"), sg.Button("List Stamps"), sg.Button("Exit")],
            [sg.Output(size=(60, 10))]
        ]
        self.window = sg.Window("Stamp Collection", self.layout)

    def _init_db(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS stamps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                scott_number TEXT,
                used INTEGER
            )
        ''')
        conn.commit()
        conn.close()

    def _save_to_db(self, stamp):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO stamps (description, scott_number, used)
            VALUES (?, ?, ?)
        ''', (stamp.description, stamp.scott_number, int(stamp.used)))
        conn.commit()
        conn.close()

    def _load_from_db(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT description, scott_number, used FROM stamps')
        rows = c.fetchall()
        for desc, scott, used in rows:
            stamp = Stamp(desc, scott, bool(used))
            self.collection.add_stamp(stamp)
        conn.close()

    def run(self):
        while True:
            event, values = self.window.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break
            elif event == "Add Stamp":
                desc = values["description"]
                scott = values["scott_number"]
                used = values["used"]
                if desc and scott:
                    stamp = Stamp(desc, scott, used)
                    self.collection.add_stamp(stamp)
                    self._save_to_db(stamp)
                    print(f"Added: {stamp}")
                else:
                    print("Please enter both description and Scott number.")
            elif event == "List Stamps":
                for stamp in self.collection.list_stamps():
                    print(stamp)
        self.window.close()