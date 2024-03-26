from lk_plants import DataApp, PlantNetResult, PlantPhoto, ReadMe, WikiPage
from workflows import scrape_app


def main():
    PlantPhoto.build_from_dir_data_original_image()
    PlantNetResult.build_from_plant_photos()
    PlantPhoto.build_contents()
    WikiPage.build()
    DataApp.write_all()

    ReadMe().write()
    scrape_app.main()


def test_main():
    ReadMe().write()


if __name__ == "__main__":
    test_main()
