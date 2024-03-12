from lk_parks import PlantNetResult, PlantPhoto, DataApp
def main():
    PlantPhoto.build_from_dir_data_original_image()
    PlantNetResult.build_from_plant_photos()
    PlantPhoto.build_contents()
    DataApp().write_all()


if __name__ == "__main__":
    main()
