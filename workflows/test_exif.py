import os
import json
from exif import Image as ExifImage

def main():
    TEST_IMAGE_PATH = os.path.join('data_test', 'exif.jpg')
    img = ExifImage(TEST_IMAGE_PATH)
    d = {}
    for key in img.list_all():
        value = str(img.get(key))
        d[key] = value
    
    print(json.dumps(d, indent=2))

if __name__ == "__main__":
    main()