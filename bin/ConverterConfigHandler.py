#  Handles the configuration file for the config parser

import configparser
import os


class ConverterConfigHandler:
    def __init__(self, confFilePath):
        # define some config variables
        self.MusescoreScoresDefaultFldr = ""
        self.PlaneShiftScoresDefaultFldr = ""

        # do not change this path anywhere else in any other functions
        self._configFilePath = confFilePath

        # define a configparser
        self._confparser = configparser.ConfigParser()

        # open the file and load the ini
        if not os.path.isfile(self._configFilePath):
            # create key value pairs inside section "PATHS" with empty values and write out a file
            self._confparser.add_section("PATHS")
            self._confparser.set("PATHS", "musescore_def_folder", "")
            self._confparser.set("PATHS", "planeshift_score_def_folder", "")
            self.writeFile()
        else:
            self._confparser.read(self._configFilePath)

    def writeFile(self):
        self._confparser.write(open(self._configFilePath, 'w'))


    def readMusescoreScoresDefaultFldr(self):
        return self._confparser.get("PATHS", "musescore_def_folder")

    def writeMusescoreScoresDefaultFldr(self, folderPath):
        self._confparser.set("PATHS", "musescore_def_folder", folderPath)
        self.writeFile()

    def readPlaneShiftScoresDefaultFldr(self):
        return self._confparser.get("PATHS", "musescore_def_folder")

    def writePlaneShiftScoresDefaultFldr(self, folderPath):
        self._confparser.set("PATHS", "planeshift_score_def_folder", folderPath)
        self.writeFile()
