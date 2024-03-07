from lk_parks import MetaData


def main():
    MetaData.save_all()
    MetaData.build_readme()
    for md in MetaData.list_all():
        print(md)


if __name__ == "__main__":
    main()
