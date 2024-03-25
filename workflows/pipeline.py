from lk_plants import (DataApp, PlantNetResult, PlantPhoto,
                       ViharamahadeviParkReport)

from workflows import scrape_app

def main():
    PlantPhoto.build_from_dir_data_original_image()
    PlantNetResult.build_from_plant_photos()
    PlantPhoto.build_contents()
    DataApp().write_all()

    ViharamahadeviParkReport().write()
    scrape_app.main()

if __name__ == "__main__":
    main()
