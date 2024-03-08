from lk_parks import NameTranslator


def main():
    nt = NameTranslator()
    nt.cleanup()
    print(nt.get('Terminalia arjuna'))


if __name__ == "__main__":
    main()
