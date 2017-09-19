import xml.etree.ElementTree as ET


class MusicXMLConverter:
    def __init(self):
        pass

    def measureIsEmpty(self, inMeasureElem):
        """Check if a measure is empty. A measure is empty if all the notes in it are rest"""
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

    def processNotes(self, inMeasureElem):
        "Process notes in a element"
        pass

    def processRepeatsInMeasure(self, inMeasureElem):
        """Handle repeats. Like barlines, voltas etc. Returns a list of "barline" XML elements"""
        inBarlines = inMeasureElem.findall("barline")
        # list to hold array of barlines for the repeats
        outBarlines = []

        if (len(inBarlines) > 0):
            for inBarline in inBarlines:
                outBarline = ET.Element("barline")
                outBarlineEnding = ET.Element("ending")
                outBarlineRepeat = ET.Element("repeat")

                inBarlineAttribs = inBarline.attrib
                for inBarlineAttrib in inBarlineAttribs:
                    outBarline.set(inBarlineAttrib, inBarlineAttribs[inBarlineAttrib])

                # important sub elements we care about are <repeat> and <ending> others are not important
                inBarlineEnding = inBarline.find("ending")
                if (inBarlineEnding is not None):
                    inBarlineEndingAttribs = inBarlineEnding.attrib
                    for inBarlineEndingAttrib in inBarlineEndingAttribs:
                        outBarlineEnding.set(inBarlineEndingAttrib, inBarlineEndingAttribs[inBarlineEndingAttrib])

                    #append barline ending to the outBarline
                        outBarline.append(outBarlineEnding)

                inBarlineRepeat = inBarline.find("repeat")
                if (inBarlineRepeat is not None):
                    inBarlineRepeatAttribs = inBarlineRepeat.attrib

                    # add all normal repeat attribs
                    for inBarlineRepeatAttrib in inBarlineRepeatAttribs:
                        outBarlineRepeat.set(inBarlineRepeatAttrib, inBarlineRepeatAttribs[inBarlineRepeatAttrib])

                    #Special PS case -- PS needs the times attrib irrespective even for 1 repeat time
                    if ("backward" == inBarlineRepeat.get("direction")):
                        if ("times" in inBarlineRepeatAttribs):
                            outBarlineRepeat.set("times",inBarlineAttribs["times"])
                        else:
                            outBarlineRepeat.set("times", "1")

                    #append barline ending to the outBarline
                    outBarline.append(outBarlineRepeat)
                else:
                    print("repeat elem not found inside barline")

                # finally add the barlines to the list
                outBarlines.append(outBarline)

        return outBarlines

    def processFirstMeasure(self, inMeasureElem):
        """Does special handling for the first measure as it includes important information like time signature etc."""
        if (self.measureIsEmpty(inMeasureElem)):
            print("Fatal Error: The first measure cannot be empty in your piece")
            exit()

        outMeasure = ET.Element("measure")
        inMeasureNo = int(inMeasureElem.get("number"))
        outMeasure.set("number", str(inMeasureNo))

        if (inMeasureNo == 1):
            # root
            outMeasureAttributes = ET.Element("attributes")

            # divisions
            outMeasureDivisions = ET.Element("divisions")

            # key
            outMeasureKey = ET.Element("key")
            outMeasureFifths = ET.Element("fifths")

            # time
            outMeasureTime = ET.Element("time")
            outMeasureBeats = ET.Element("beats")
            outMeasureBeatType = ET.Element("beat-type")

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

            # process time
            inMeasureTime = inMeasureAttributes.find("time")
            if (inMeasureTime is None):
                print("Fatal Error: time not found in measure. Exiting")
                exit()

            inMeasureBeats = inMeasureTime.find("beats")

            if (inMeasureBeats is not None):
                outMeasureBeats.text = inMeasureBeats.text
            else:
                print("Fatal Error: beats not found in measure. Exiting")
                exit()

            inMeasureBeatType = inMeasureTime.find("beat-type")
            if (inMeasureBeatType is not None):
                outMeasureBeatType.text = inMeasureBeatType.text
            else:
                print("Fatal Error: beats not found in measure. Exiting")
                exit()

            outMeasureTime.append(outMeasureBeats)
            outMeasureTime.append(outMeasureBeatType)

            # creating the nesting hierarchy
            # divisions
            outMeasureAttributes.append(outMeasureDivisions)
            # key
            outMeasureAttributes.append(outMeasureKey)
            # time
            outMeasureAttributes.append(outMeasureTime)
            # add any repeats
            outBarlines = self.processRepeatsInMeasure(inMeasureElem)
            if (len(outBarlines) > 0):
                for outBarline in outBarlines:
                    outMeasure.append(outBarline)
            else:
                print("No barlines found")
            # add it all to the first measure
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
        # inputTreeRoot = inputTree.getroot()

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

                # First measure
                # Do this irrespective of whether measure is empty or not
                if (0 == i):
                    outPart.append(self.processFirstMeasure(inMeasures[i]))
                    ''' important process it only with the func above function and
                        skip the other below code '''
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
