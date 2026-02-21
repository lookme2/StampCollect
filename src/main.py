from database import init_db
from gui import StampCollectionGUI


def main():
    init_db()
    StampCollectionGUI().run()


if __name__ == "__main__":
    main()
