from lk_parks import PlantNetResult, PlantPhoto


def main():
    PlantPhoto.build_from_dir_data_original_image()
    PlantNetResult.build_from_plant_photos()
    PlantPhoto.build_contents()


if __name__ == "__main__":
    main()
