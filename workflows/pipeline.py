from lk_parks import PlantNetResult, PlantPhoto
from lk_parks.core.data_app.DataApp import DataApp

def main():
    PlantPhoto.build_from_dir_data_original_image()
    PlantNetResult.build_from_plant_photos()
    PlantPhoto.build_contents()
    DataApp().write_all()


if __name__ == "__main__":
    main()
