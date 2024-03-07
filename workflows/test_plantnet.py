import os

from plantnet import PlantNet

TEST_IMAGE_PATH = os.path.join(
    'data', 'images', 'Photo-2024-02-22-07-16-55.jpg'
)

p = PlantNet.from_env()
print(p.identify(TEST_IMAGE_PATH))
