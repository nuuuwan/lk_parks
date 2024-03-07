from lk_parks import MetaData


def main():
    MetaData.build_from_dir_data_image_original()
    MetaData.build_readme()


if __name__ == "__main__":
    main()
