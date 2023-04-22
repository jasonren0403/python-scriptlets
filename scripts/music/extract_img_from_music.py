import glob
from pathlib import Path

import mutagen


def extract_folder_music_img(glob_pattern):
    # extract_folder_music_img(r"path\to\*.mp3")
    for file in glob.iglob(glob_pattern):
        fpath = Path(file)
        afile = mutagen.File(fpath)
        # print(afile.keys())
        if 'APIC:' not in afile.tags:
            print(f"File {file} do not contain APIC frame")
            continue
        else:
            title = afile.tags["TIT2"]
            # print(title.text[0])
            artwork = afile.tags['APIC:'].data  # access APIC frame and grab the image
            img_path = fpath.with_name(f"{title.text[0]}.jpg")
            with open(img_path, 'wb') as img:
                print(f"Writing artwork to {img_path}")
                img.write(artwork)  # write artwork to new image
