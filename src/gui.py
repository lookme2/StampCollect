import os
import wx
from stamp import Stamp, StampCollection
import database

DB_PATH = os.path.join(os.path.dirname(__file__), "stamps.db")


class StampCollectionGUI(wx.Frame):
    def __init__(self, parent, title):
        super(StampCollectionGUI, self).__init__(parent, title=title, size=(600, 400))

        self.collection = StampCollection()
        self.conn = database.init_db(DB_PATH)
        self.image_path = None
        self._load_from_db()

        self.InitUI()
        self.Centre()
        self.Show()

    def InitUI(self):
        panel = wx.Panel(self)

        grid = wx.GridBagSizer(vgap=10, hgap=10)

        # Column 0: Stamp information
        stamp_box = wx.StaticBox(panel, label="Stamp Information")
        stamp_sizer = wx.StaticBoxSizer(stamp_box, wx.VERTICAL)

        # Description input
        desc_sizer = wx.BoxSizer(wx.HORIZONTAL)
        desc_sizer.Add(wx.StaticText(panel, label="Description"), flag=wx.RIGHT, border=8)
        self.description_input = wx.TextCtrl(panel)
        desc_sizer.Add(self.description_input, proportion=1)
        stamp_sizer.Add(desc_sizer, flag=wx.EXPAND|wx.BOTTOM, border=5)

        # Scott Number input
        scott_sizer = wx.BoxSizer(wx.HORIZONTAL)
        scott_sizer.Add(wx.StaticText(panel, label="Scott Number"), flag=wx.RIGHT, border=8)
        self.scott_input = wx.TextCtrl(panel)
        scott_sizer.Add(self.scott_input, proportion=1)
        stamp_sizer.Add(scott_sizer, flag=wx.EXPAND|wx.BOTTOM, border=5)

        # Used checkbox
        self.used_checkbox = wx.CheckBox(panel, label="Used")
        stamp_sizer.Add(self.used_checkbox, flag=wx.BOTTOM, border=5)

        # Add Stamp button
        add_button = wx.Button(panel, label="Add Stamp")
        stamp_sizer.Add(add_button, flag=wx.TOP, border=5)

        grid.Add(stamp_sizer, pos=(0, 0), flag=wx.EXPAND|wx.ALL, border=10)

        # Column 1: Image section
        image_box = wx.StaticBox(panel, label="Stamp Image")
        image_sizer = wx.StaticBoxSizer(image_box, wx.VERTICAL)

        # Image display
        self.image_bitmap = wx.StaticBitmap(panel, size=(150, 150))
        image_sizer.Add(self.image_bitmap, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=10)

        # Image buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        browse_button = wx.Button(panel, label="Browse")
        remove_button = wx.Button(panel, label="Remove")
        button_sizer.Add(browse_button)
        button_sizer.Add(remove_button, flag=wx.LEFT, border=5)
        image_sizer.Add(button_sizer, flag=wx.ALIGN_CENTER)

        grid.Add(image_sizer, pos=(0, 1), flag=wx.EXPAND|wx.ALL, border=10)

        # Row 1: Output area spanning both columns
        output_box = wx.StaticBox(panel, label="Collection Output")
        output_sizer = wx.StaticBoxSizer(output_box, wx.VERTICAL)
        self.output_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_READONLY)
        output_sizer.Add(self.output_text, proportion=1, flag=wx.EXPAND)

        grid.Add(output_sizer, pos=(1, 0), span=(1, 2), flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)

        # Other buttons (List Stamps, Exit) - maybe add them to the output box or somewhere else
        other_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        list_button = wx.Button(panel, label="List Stamps")
        exit_button = wx.Button(panel, label="Exit")
        other_buttons_sizer.Add(list_button)
        other_buttons_sizer.Add(exit_button, flag=wx.LEFT, border=5)
        output_sizer.Add(other_buttons_sizer, flag=wx.TOP|wx.ALIGN_CENTER, border=10)

        # Make columns expandable
        grid.AddGrowableCol(0, 1)
        grid.AddGrowableCol(1, 1)
        grid.AddGrowableRow(1, 1)

        panel.SetSizer(grid)

        # Bind events
        add_button.Bind(wx.EVT_BUTTON, self.OnAddStamp)
        list_button.Bind(wx.EVT_BUTTON, self.OnListStamps)
        exit_button.Bind(wx.EVT_BUTTON, self.OnExit)
        browse_button.Bind(wx.EVT_BUTTON, self.OnBrowseImage)
        remove_button.Bind(wx.EVT_BUTTON, self.OnRemoveImage)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

    def _save_to_db(self, stamp: Stamp) -> None:
        # Map simple GUI fields into the general stamps table
        condition = "Used" if getattr(stamp, "used", False) else "Mint"
        database.add_stamp(
            self.conn,
            name=stamp.description,
            catalog_number=stamp.scott_number,
            condition=condition,
            image_path=getattr(stamp, "image_path", None),
        )

    def _load_from_db(self) -> None:
        rows = database.list_stamps(self.conn, limit=1000)
        for r in rows:
            name = r["name"] or ""
            catalog = r["catalog_number"] or ""
            condition = (r["condition"] or "").lower()
            used = True if "used" in condition else False
            image_path = r["image_path"]
            stamp = Stamp(name, catalog, used, image_path)
            self.collection.add_stamp(stamp)

    def OnAddStamp(self, event):
        desc = self.description_input.GetValue()
        scott = self.scott_input.GetValue()
        used = self.used_checkbox.GetValue()

        if desc and scott:
            stamp = Stamp(desc, scott, used, self.image_path)
            self.collection.add_stamp(stamp)
            self._save_to_db(stamp)
            self.output_text.AppendText(f"Added: {stamp}\n")
            # Clear inputs
            self.description_input.SetValue("")
            self.scott_input.SetValue("")
            self.used_checkbox.SetValue(False)
            self.OnRemoveImage(None)  # Clear the image as well
        else:
            self.output_text.AppendText("Please enter both description and Scott number.\n")

    def OnListStamps(self, event):
        self.output_text.AppendText("Stamps in collection:\n")
        for stamp in self.collection.list_stamps():
            self.output_text.AppendText(f"{stamp}\n")
        self.output_text.AppendText("\n")

    def OnExit(self, event):
        self.conn.close()
        self.Destroy()

    def OnBrowseImage(self, event):
        with wx.FileDialog(self, "Choose a stamp image", wildcard="Image files (*.png;*.jpg;*.jpeg;*.bmp;*.gif)|*.png;*.jpg;*.jpeg;*.bmp;*.gif",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            self.image_path = fileDialog.GetPath()
            self._load_image()

    def OnRemoveImage(self, event):
        self.image_path = None
        self.image_bitmap.SetBitmap(wx.NullBitmap)

    def _load_image(self):
        if self.image_path and os.path.exists(self.image_path):
            image = wx.Image(self.image_path)
            # Scale to fit 100x100 while maintaining aspect ratio
            image = image.Scale(100, 100, wx.IMAGE_QUALITY_HIGH)
            bitmap = wx.Bitmap(image)
            self.image_bitmap.SetBitmap(bitmap)
        else:
            self.image_bitmap.SetBitmap(wx.NullBitmap)


def run_gui():
    app = wx.App()
    StampCollectionGUI(None, "Stamp Collection")
    app.MainLoop()
