from lk_parks import MetaData


def main():
    MetaData.build_from_dir_data_image_original()
    MetaData.build_readme()
    MetaData.write_idx_summary()


if __name__ == "__main__":
    main()
