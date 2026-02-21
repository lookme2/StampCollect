import os
import FreeSimpleGUI as sg
from stamp import Stamp, StampCollection
import database

DB_PATH = os.path.join(os.path.dirname(__file__), "stamps.db")


class StampCollectionGUI:
    def __init__(self):
        self.collection = StampCollection()
        self.conn = database.init_db(DB_PATH)
        self._load_from_db()
        self.layout = [
            [sg.Text("Description"), sg.Input(key="description")],
            [sg.Text("Scott Number"), sg.Input(key="scott_number")],
            [sg.Checkbox("Used", key="used")],
            [sg.Button("Add Stamp"), sg.Button("List Stamps"), sg.Button("Exit")],
            [sg.Output(size=(60, 10))]
        ]
        self.window = sg.Window("Stamp Collection", self.layout)

    def _save_to_db(self, stamp: Stamp) -> None:
        # Map simple GUI fields into the general stamps table
        condition = "Used" if getattr(stamp, "used", False) else "Mint"
        database.add_stamp(
            self.conn,
            name=stamp.description,
            catalog_number=stamp.scott_number,
            condition=condition,
        )

    def _load_from_db(self) -> None:
        rows = database.list_stamps(self.conn, limit=1000)
        for r in rows:
            name = r["name"] or ""
            catalog = r["catalog_number"] or ""
            condition = (r["condition"] or "").lower()
            used = True if "used" in condition else False
            stamp = Stamp(name, catalog, used)
            self.collection.add_stamp(stamp)

    def run(self):
        while True:
            event, values = self.window.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break
            elif event == "Add Stamp":
                desc = values["description"]
                scott = values["scott_number"]
                used = values.get("used", False)
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
