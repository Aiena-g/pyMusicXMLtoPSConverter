import xml.etree.ElementTree as ET


class MusicXMLConverter:
    def __init__(self):
        self._mode = "debug"
        if (self._mode not in ["debug", "production"]):
            raise ValueError('invalid mode set. Should be "debug" for a more verbose output for debugging OR "production".')


    def debugPrint(self, msg):
        if (self._mode == "debug"):
            print(msg)

    def measureIsEmpty(self, inMeasureElem):
        """ Check if a measure is empty. A measure is empty if all the notes in it are of type "rest" """
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
        """ Process notes in a element. Returns a list with all the notes in the measure converted as per PS format """
        inNotes = inMeasureElem.findall("note")
        # list to hold array of processed note elements
        lstOutNotes = []

        for inNote in inNotes:
            for childNode in inNote:
                outNote = ET.Element("note")

                # rest
                inRest = inNote.find("rest")
                if (inRest is not None):
                    outRest = ET.Element("rest")
                    outNote.append(outRest)

                # chord
                inChord = inNote.find("chord")
                if (inChord is not None):
                    outChord = ET.Element("chord")
                    outNote.append(outChord)

                # duration
                inDuration = inNote.find("duration")
                if (inDuration is not None):
                    outDuration = ET.Element("duration")
                    outDuration.text = inDuration.text
                    outNote.append(outDuration)

                # pitch
                inPitch = inNote.find("pitch")
                if (inPitch is not None):
                    outPitch = ET.Element("pitch")
                    for childNode in inPitch:
                        if (childNode.tag in ["step", "octave", "alter"]):
                            pitchSubElem = ET.Element(childNode.tag)
                            pitchSubElem.text = childNode.text
                            outPitch.append(pitchSubElem)

                    outNote.append(outPitch)

                # append the mote to the list of notes
                lstOutNotes.append(outNote)

        # finally return the list of notes
        return lstOutNotes

    def processRepeatsInMeasure(self, inMeasureElem):
        """ Handle repeats. Like barlines, voltas etc. Returns a list of "barline" XML elements """
        inBarlines = inMeasureElem.findall("barline")
        # list to hold array of barlines for the repeats
        lstOutBarlines = []

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

                        # append barline ending to the outBarline
                        outBarline.append(outBarlineEnding)

                inBarlineRepeat = inBarline.find("repeat")
                if (inBarlineRepeat is not None):
                    inBarlineRepeatAttribs = inBarlineRepeat.attrib

                    # add all normal repeat attribs
                    for inBarlineRepeatAttrib in inBarlineRepeatAttribs:
                        outBarlineRepeat.set(inBarlineRepeatAttrib, inBarlineRepeatAttribs[inBarlineRepeatAttrib])

                    # Special PS case -- PS needs the times attrib irrespective even for 1 repeat time
                    if ("backward" == inBarlineRepeat.get("direction")):
                        if ("times" in inBarlineRepeatAttribs):
                            outBarlineRepeat.set("times", inBarlineAttribs["times"])
                        else:
                            outBarlineRepeat.set("times", "1")

                    # append barline ending to the outBarline
                    outBarline.append(outBarlineRepeat)
                else:
                    self.debugPrint("repeat elem not found inside barline")

                # finally add the barlines to the list
                lstOutBarlines.append(outBarline)

        return lstOutBarlines

    def processFirstMeasure(self, inMeasureElem):
        """ Does special handling for the first measure as it includes important information like time signature etc."""

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
                raise RuntimeError("Fatal Error extracting attributes. Exiting")
            else:
                inMeasureDivisions = inMeasureAttributes.find("divisions")

            # process divisions
            if (inMeasureDivisions is None):
                raise RuntimeError("Fatal Error extracting divisions. Exiting")
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
                    raise RuntimeError("Fatal Error: fifths not found in measure. Exiting")
            else:
                raise RuntimeError ("Fatal Error: input measure key not found. Exiting")
                exit()

            # process time
            inMeasureTime = inMeasureAttributes.find("time")
            if (inMeasureTime is None):
                raise RuntimeError("Fatal Error: time not found in measure. Exiting")
                exit()

            inMeasureBeats = inMeasureTime.find("beats")

            if (inMeasureBeats is not None):
                outMeasureBeats.text = inMeasureBeats.text
            else:
                raise RuntimeError("Fatal Error: beats not found in measure. Exiting")
                exit()

            inMeasureBeatType = inMeasureTime.find("beat-type")
            if (inMeasureBeatType is not None):
                outMeasureBeatType.text = inMeasureBeatType.text
            else:
                raise RuntimeError("Fatal Error: beats not found in measure. Exiting")
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
            # add it all to the first measure
            outMeasure.append(outMeasureAttributes)

            # add the notes of the measure
            measureNotes = self.processNotes(inMeasureElem)
            if (len(measureNotes) > 0):
                for measureNote in measureNotes:
                    outMeasure.append(measureNote)
            else:
                raise RuntimeError("Fatal Error: No notes in measure")
            # add any repeats
            outBarlines = self.processRepeatsInMeasure(inMeasureElem)
            if (len(outBarlines) > 0):
                for outBarline in outBarlines:
                    outMeasure.append(outBarline)
            else:
                self.debugPrint("No repeat barlines found")

            return outMeasure
        else:
            self.debugPrint("Error while processing first measure got an unexpected measure number ", inMeasureNo,
                            ". Expected  ",
                            "1")
            exit()

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
                self.debugPrint("Processing measure" + inMeasures[i].get("number"))

                # First measure
                # Do this irrespective of whether measure is empty or not
                if (0 == i):

                    if (self.measureIsEmpty(inMeasures[i])):
                        raise RuntimeError("Fatal Error: The first measure cannot be empty in your piece")

                    outPart.append(self.processFirstMeasure(inMeasures[i]))
                else:
                    if (self.measureIsEmpty(inMeasures[i])):
                        # skip processing this measure
                        self.debugPrint("skipping measure")
                        continue

                    # otherwise begin processing the measure

                    computedMeasureNo = int(inMeasures[i].get("number")) - emptyMeasureCount

                    if (emptyMeasureCount > 0):
                        self.debugPrint("setting measure number "+ i + " to ", str(computedMeasureNo))

                    outMeasure = ET.Element("measure")
                    outMeasure.set("number", str(computedMeasureNo))

                    # add the notes of the measure
                    measureNotes = self.processNotes(inMeasures[i])
                    if (len(measureNotes) > 0):
                        for measureNote in measureNotes:
                            outMeasure.append(measureNote)
                    else:
                        raise RuntimeError("Fatal Error: No notes in measure")

                    # add any repeats
                    outBarlines = self.processRepeatsInMeasure(inMeasures[i])
                    if (len(outBarlines) > 0):
                        for outBarline in outBarlines:
                            outMeasure.append(outBarline)
                    else:
                        self.debugPrint("No repeat barlines found")

                    # append this measure as subelement of "part"
                    outPart.append(outMeasure)

        return ET.tostring(outTreeRoot)
        # for child in inputTreeRoot:
        #     self.debugPrint(child.tag, child.attrib)


# test it
converter = MusicXMLConverter()
voltaTestFile = "/mnt/200GBlinuxPart/Musescore/PSConverterPurePy/samplefiles/MC_volta_test.xml"
emptyScoreFile = "/mnt/200GBlinuxPart/Musescore/PSConverterPurePy/samplefiles/MC_Empty_bars_test_more_variety.xml"
convXML = converter.convertXML(emptyScoreFile)
print(convXML)
