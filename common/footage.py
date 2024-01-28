import json
from os.path import join, exists


class Footage:
    def __init__(self, data_folder: str, metadata = None):
        self.folder = data_folder
        self.open(data_folder=data_folder, metadata=metadata)

    def open(self, data_folder: str = None, metadata = None):
        if metadata != None:
            self.metadata = metadata
        elif data_folder != None and exists(join(data_folder, "metadata.json")):
                self.metadata = json.loads( open(join(data_folder, "metadata.json") ).read())
        else:
            print("ERROR: No metadata found")
            exit()

        if "fps" in self.metadata:
            self.fps = self.metadata["fps"]
        else:
            self.fps = 24

        self.bands = {}
        for band in self.metadata["bands"]:
            b = self.metadata["bands"][band]

            if "url" in b:
                b["name"] = "u_band_" + band
                b["url"] = self.getBandUrl(band)
                self.bands[band] = b

            elif "values" in b:
                b["name"] = band
                self.bands[band] = b


    def getBandUrl(self, band: str):
        return join(self.folder, self.metadata["bands"][band]["url"])


    def setWidth(self, width: int):
        self.metadata["width"] = width

    def setHeight(self, height: int):
        self.metadata["height"] = height

    @property
    def width(self):
        return self.metadata["width"]

    @property
    def height(self):
        return self.metadata["height"]