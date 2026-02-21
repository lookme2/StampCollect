class Stamp:
    def __init__(self, description, scott_number, used=False):
        self.description = description
        self.scott_number = scott_number
        self.used = used
        self.qtyUsed = None
        self.qtyMint = None
        self.plateBlock = False
        self.year = None
        self.usedPrice = None
        self.mintPrice = None

    def __repr__(self):
        status = "Used" if self.used else "Unused"
        return f"<Stamp: {self.description}, Scott #{self.scott_number}, {status}>"


class StampCollection:
    def __init__(self):
        self.stamps = []

    def add_stamp(self, stamp):
        """Add a stamp to the collection."""
        self.stamps.append(stamp)

    def remove_stamp(self, stamp):
        """Remove a stamp from the collection."""
        if stamp in self.stamps:
            self.stamps.remove(stamp)

    def list_stamps(self):
        """Return a list of all stamps in the collection."""
        return self.stamps

    def __len__(self):
        """Return the number of stamps in the collection."""
        return len(self.stamps)
