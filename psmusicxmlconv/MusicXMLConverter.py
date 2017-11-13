import xml.etree.ElementTree as ET


class MusicXMLConverter:
    def __init__(self, mode="debug"):
        self._mode = mode
        # define some global properties used in other places for MusicXML
        self._multiplier = None  # gets a value when processing the first measure

        if (self._mode not in ["debug", "production"]):
            raise ValueError(
                'invalid mode set. Should be "debug" for a more verbose output for debugging OR "production".')

    def debugPrint(self, msg):
        if (self._mode == "debug"):
            print(msg)

    def measureIsSilent(self, inMeasureElem):
        """ Check if a measure has no audible notes. A measure is silent if all the notes in it are of type "rest" """
        inMeasureNotes = inMeasureElem.findall("note")
        if (len(inMeasureNotes) > 0):
            restCount = 0  # initialise rest count
            for inMeasureNote in inMeasureNotes:
                noteTypeRest = inMeasureNote.find("rest")
                if (noteTypeRest is not None):
                    restCount += 1

            if (restCount == len(inMeasureNotes)):
                return True
            else:
                return False

    def measureIsEmpty(self, inMeasureElem):
        """ Check if a measure has notes (Not even rests). A measure is empty and invalid if it has no notes at all """
        emptyMeasureMsg = "Measure found empty (invalid XML)"
        inMeasureNotes = inMeasureElem.findall("note")
        if (inMeasureNotes is None):
            self.debugPrint(emptyMeasureMsg)
            return True
        elif (len(inMeasureNotes)  == 0):
            self.debugPrint(emptyMeasureMsg)
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

                # pitch
                inPitch = inNote.find("pitch")
                if (inPitch is not None):
                    outPitch = ET.Element("pitch")
                    for childNode in inPitch:
                        if (True == (childNode.tag in ["step", "octave"])):
                            pitchSubElem = ET.Element(childNode.tag)
                            pitchSubElem.text = childNode.text
                            outPitch.append(pitchSubElem)
                    # handle the "alter" child tag separately even if the alter value is 0 include it otherwise
                    #   include the original scores alter value
                    inPitchAlter = inPitch.find("alter")
                    if (inPitchAlter is not None):
                        # use sources alter elem
                        outPitchAlter = ET.Element("alter")
                        outPitchAlter.text = inPitchAlter.text
                        outPitch.append(outPitchAlter)
                    else:
                        # make a zero value alter element
                        outPitchAlter = ET.Element("alter")
                        outPitchAlter.text = "0"
                        outPitch.append(outPitchAlter)

                    outNote.append(outPitch)

                # duration
                inDuration = inNote.find("duration")
                if (inDuration is not None):
                    outDuration = ET.Element("duration")
                    outDurationVal = int(inDuration.text) * self._multiplier
                    outDuration.text = str(int(outDurationVal))
                    outNote.append(outDuration)

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
                        if (True == ("times" in inBarlineRepeatAttribs)):
                            outBarlineRepeat.set("times", inBarlineRepeatAttribs["times"])
                        else:
                            outBarlineRepeat.set("times", "1")

                    # append barline repeat to the outBarline
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

            # tempo related
            outMeasureDirection = ET.Element("direction")
            outMeasureSound = ET.Element("sound")

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
                # Hardcode 4 here - A peculiarity of the reference implementation I dont understand this part
                outMeasureDivisions.text = str(4)
                # compute Multiplier here (Multiplier used to multiply MusicXML note duration
                #   i.e. "output note duration" = "input note duration" * "multiplier"
                self._multiplier = 4 / int(inMeasureDivisions.text)

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
                raise RuntimeError("Fatal Error: input measure key not found. Exiting")
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

            # process sound tempo
            inMeasureDirection = inMeasureElem.find("direction")
            if (inMeasureDirection is not None):
                inMeasureSound = inMeasureDirection.find("sound")
                if (inMeasureSound is not None):
                    inMeasureSoundAttribs = inMeasureSound.attrib

                    if (True == ("tempo" in inMeasureSoundAttribs)):
                        outMeasureSound.set("tempo", inMeasureSoundAttribs["tempo"])
                        self.debugPrint("tempo found")
                    else:
                        outMeasureSound.set("tempo", "90")
                else:
                    self.debugPrint("tempo not found")
                    outMeasureSound.set("tempo", "90")
            else:
                self.debugPrint("direction not found")

            # creating the nesting hierarchy
            # divisions
            outMeasureAttributes.append(outMeasureDivisions)
            # key
            outMeasureAttributes.append(outMeasureKey)
            # time
            outMeasureAttributes.append(outMeasureTime)

            # add it all to the first measure
            outMeasure.append(outMeasureAttributes)
            # ad sound tempo element to a direction element and add that to the measure
            outMeasureDirection.append(outMeasureSound)
            outMeasure.append(outMeasureDirection)

            # add any repeats
            outBarlines = self.processRepeatsInMeasure(inMeasureElem)
            if (len(outBarlines) > 0):
                for outBarline in outBarlines:
                    outMeasure.append(outBarline)
            else:
                self.debugPrint("No repeat barlines found")

            # add the notes of the measure
            measureNotes = self.processNotes(inMeasureElem)
            if (len(measureNotes) > 0):
                for measureNote in measureNotes:
                    outMeasure.append(measureNote)
            else:
                raise RuntimeError("Fatal Error: No notes in measure")

            return outMeasure
        else:
            self.debugPrint("Error while processing first measure got an unexpected measure number " + inMeasureNo +
                            ". Expected  " + "1")
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
        outPartName.text = "converted stuff"

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
                        self.debugPrint("setting measure number " + i + " to ", str(computedMeasureNo))

                    outMeasure = ET.Element("measure")
                    outMeasure.set("number", str(computedMeasureNo))

                    # add any repeats
                    outBarlines = self.processRepeatsInMeasure(inMeasures[i])
                    if (len(outBarlines) > 0):
                        for outBarline in outBarlines:
                            outMeasure.append(outBarline)
                    else:
                        self.debugPrint("No repeat barlines found")

                    # add the notes of the measure
                    measureNotes = self.processNotes(inMeasures[i])
                    if (len(measureNotes) > 0):
                        for measureNote in measureNotes:
                            outMeasure.append(measureNote)
                    else:
                        raise RuntimeError("Fatal Error: No notes in measure")

                    # append this measure as subelement of "part"
                    outPart.append(outMeasure)

        return ET.tostring(outTreeRoot)
        # for child in inputTreeRoot:
        #     self.debugPrint(child.tag, child.attrib)


if __name__ == '__main__':
    # test it
    converter = MusicXMLConverter()
    voltaTestFile = "/mnt/200GBlinuxPart/Musescore/PSConverterPurePy/samplefiles/MC_volta_test.xml"
    voltaWithTimesTestFile = "/mnt/200GBlinuxPart/Musescore/PSConverterPurePy/samplefiles/MC_repeat_test_3r.xml"
    emptyScoreFile = "/mnt/200GBlinuxPart/Musescore/PSConverterPurePy/samplefiles/MC_Empty_bars_test_more_variety.xml"
    six_eight_Score_File = "/home/aiena/Documents/MuseScore2/Scores/Test Suite/test_time_sig_6_8.xml"
    six_eight_Score_Broken_Empty_Measure_File = "/mnt/200GBlinuxPart/Musescore/PSConverterPurePy/samplefiles/MCtest_time_sig_6_8_empty_meas.xml"
    convXML = converter.convertXML(six_eight_Score_Broken_Empty_Measure_File)
    print(convXML)
