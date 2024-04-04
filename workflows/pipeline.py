from lk_plants import (App, DataApp, PlantNetResult, PlantPhoto, ReadMe,
                       WikiPage)


def main():
    PlantPhoto.build_from_dir_data_original_image()
    PlantNetResult.build_from_plant_photos()
    PlantPhoto.build_contents()
    WikiPage.build()
    DataApp.write_all()
    ReadMe().write()
    App.scrape()


if __name__ == "__main__":
    main()
