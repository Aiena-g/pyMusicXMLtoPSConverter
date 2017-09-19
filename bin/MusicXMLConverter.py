import xml.etree.ElementTree as ET


class MusicXMLConverter:
    def __init(self):
        pass

    def measureIsEmpty(self, inMeasureElem):
        inMeasureNotes = inMeasureElem.findall("note")
        if (len(inMeasureNotes) > 0):
            restCount = 0;  # initialise rest count
            for inMeasureNote in inMeasureNotes:
                noteTypeRest = inMeasureNote.find("rest")
                if (noteTypeRest is not None):
                    restCount += 1

            if (restCount == len(inMeasureNotes)):
                return True
            else:
                return False

    def processFirstMeasure(self, inMeasureElem):
        if (self.measureIsEmpty(inMeasureElem)):
            print("Fatal Error: The first measure caannot be empty in your piece")
            exit()

        outMeasure = ET.Element("measure")
        inMeasureNo = int(inMeasureElem.get("number"))
        outMeasure.set("number", str(inMeasureNo))

        if (inMeasureNo == 1):
            outMeasureAttributes = ET.Element("attributes")
            outMeasureDivisions = ET.Element("divisions")
            outMeasureKey = ET.Element("key")
            outMeasureFifths = ET.Element("fifths")

            # process attributes root
            inMeasureAttributes = inMeasureElem.find("attributes")

            if (inMeasureAttributes is None):
                print("Fatal Error extracting attributes. Exiting")
                exit()
            else:
                inMeasureDivisions = inMeasureAttributes.find("divisions")

            # process divisions
            if (inMeasureDivisions is None):
                print("Fatal Error extracting divisions. Exiting")
                exit()
            else:
                outMeasureDivisions.text = inMeasureDivisions.text

            # process key -- fifths
            inMeasureKey = inMeasureAttributes.find("key")
            if (inMeasureKey is not None):
                inMeasureFifths = inMeasureKey.find("fifths")
                if (inMeasureFifths is not None):
                    outMeasureFifths.text = inMeasureFifths.text
                    outMeasureKey.append(outMeasureFifths)
                else:
                    print("Fatal Error: fifths not found in measure. Exiting")
                    exit()
            else:
                print("Fatal Error: input measure key not found. Exiting")
                exit()

            # creating the nesting hierarchy
            outMeasureAttributes.append(outMeasureDivisions)
            outMeasureAttributes.append(outMeasureKey)
            outMeasure.append(outMeasureAttributes)
            return outMeasure
        else:
            print("Error while processing first measure got an unexpected measure number ", inMeasureNo, ". Expected  ",
                  "1")
            exit()

        pass  # TODO: Do the basics clefs etc here

    def convertXML(self, musescoreXMLfilePath):

        # parse input file and store the root
        inputTree = ET.parse(musescoreXMLfilePath)
        inputTreeRoot = inputTree.getroot()

        # create the root output element
        outTreeRoot = ET.Element("score-partwise")
        outTreeRoot.set("version", "2.0")

        outPartList = ET.Element("part-list")

        outScorePart = ET.Element("score-part")
        outScorePart.set("id", "P1")

        outPartName = ET.Element("part-name")
        outPartName.text = "converted-stuff"

        # add it as subelement of score-part
        outScorePart.append(outPartName)
        # add it as subelement of  part -list
        outPartList.append(outScorePart)
        # add it as subelement of  score-partwise
        outTreeRoot.append(outPartList)

        # create the main part
        outPart = ET.Element("part")
        outPart.set("id", "P1")
        # add it as subelement of the root
        outTreeRoot.append(outPart)

        inputPart = inputTree.find("part")

        # declare an empty measure counter to rectifiy the measure number later
        emptyMeasureCount = 0

        inMeasures = inputPart.findall("measure")
        if (len(inMeasures) > 0):

            for i in range(0, len(inMeasures)):
                print("Processing measure", inMeasures[i].get("number"))

                # Do this irrespective of whether measure is empty or not
                if (0 == i):
                    outPart.append(self.processFirstMeasure(inMeasures[i]))
                    ''' important process it only with this function and
                        skip the other code it otherwise do not execute below code '''
                    continue

                if (self.measureIsEmpty(inMeasures[i])):
                    # skip processing this measure
                    print("skipping measure")
                    continue
                else:

                    # otherwise begin processing the measure

                    computedMeasureNo = int(inMeasures[i].get("number")) - emptyMeasureCount

                    if (emptyMeasureCount > 0):
                        print("setting measure number ", i, " to ", str(computedMeasureNo))

                    outMeasure = ET.Element("measure")
                    outMeasure.set("number", str(computedMeasureNo))

                    # append this measure as subelement of "part"
                    outPart.append(outMeasure)

        return ET.tostring(outTreeRoot)
        # for child in inputTreeRoot:
        #     print(child.tag, child.attrib)


# test it
converter = MusicXMLConverter()
voltaTestFile = "/mnt/200GBlinuxPart/Musescore/PSConverterPurePy/samplefiles/MC_volta_test.xml"
emptyScoreFile = "/mnt/200GBlinuxPart/Musescore/PSConverterPurePy/samplefiles/MC_Empty_bars_test_more_variety.xml"
convXML = converter.convertXML(voltaTestFile)
print(convXML)
