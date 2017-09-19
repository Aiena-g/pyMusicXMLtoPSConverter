<?php
if ($argc != 3) {

    ?>

    This is a command line PHP script to convert MusicXML exported from Musescore into playable format by planeshift.

    Usage:
    <?php echo basename($argv[0]); ?> [INPUT_FILENAME] [OUTPUT_FILENAME]

    <?php
} else {

    $in_filename = $argv[1];
    $out_filename = $argv[2];

    if (file_exists($in_filename)) {
        if (is_readable($in_filename)) {
            echo "File is readable ...\n";
            echo "processing XML ...\n\n\n";
            try {
                $data = convertXML($in_filename);
//                echo $data ."\n\n";
                file_put_contents($out_filename, $data);
            } catch (Exception $e) {
                echo "Failed while converting XML ... exiting";
                exit(1);
            }
            //write to the output file

            echo "\n\n Done processing XML ...\n\n";
            echo "File savd out to: " . $out_filename . "\n\n";
        } else {
            echo "File exist but cannot be read check your permissions....\n";
            exit(0);
        }
    } else {
        echo "you have provided a path to a file which does not exists ... exiting\n";
        exit(0);
    }

    $out_filepath = dirname($out_filename);

    if (file_exists($out_filepath)) {
        if (is_readable($out_filepath)) {
            // do nothing
        } else {
            echo "cannot write to output file directory; check your permissions....\n";
            exit(0);
        }
    } else {
        echo "Output files directory path does not exists ... exiting\n";
        exit(0);
    }
}

/**
 * 
 * @param type $musescoreXMLFilename filename of input Musescore MusicXML
 * @return mixed returns "false" if the file is invalid OR converted XML if the file is valid
 */
function convertXML($musescoreXMLFilename)
{
    //parse input file
    $dom = new DOMDocument();
    $dom->load($musescoreXMLFilename);

//    //validate file (Skipping input file is assumed valid)
//    if (false === $dom->validate()) {
//        echo "the file provided is an invalid XML file. Please ensure theat the XML is valid.";
//        return false;
//    }
    //continue to process XML assume it is valid
    $outXML = '<score-partwise version="2.0">'
        . '<part-list>'
        . '<score-part id="P1">'
        . '<part-name>converted stuff</part-name>'
        . '</score-part>'
        . '</part-list>'
        . '<part id="P1">';

    $measures = $dom->getElementsByTagName("measure");

    // This loop does the work: Iterates through the measures and copies the important stuff (read: "PlaneShift compatible tags") to outfile
    $i = 1;
    $j = 0;
    $k = 0;
    $l = 0;
    $alter = 0;
    $duration = 1;
    $multiplier = 1;

    // initialisation var for empty measure count
    $emptyMeasureCount = 0;

    //process measures
    for ($i = 0; $i < $measures->length; $i++) {

        //test if a measure is empty and skip it
        $notes = $measures->item($i)->getElementsByTagName("note");
        $measureIsEmpty = false; //initialise test var
        $noteCount = $notes->length;
        if ($noteCount === 1) {
            foreach ($notes[0]->childNodes as $noteChild) {
                if ($noteChild->nodeName === "rest") {
                    echo "measure found empty -- skipping measure $i\n";
                    $emptyMeasureCount++;
                    // skip the measure (only one note which is a rest is present === empty measure)
                    $measureIsEmpty = true;
                }
            }
        }

        if ($measureIsEmpty === true) {
            echo "empty measure count is now: $emptyMeasureCount \n";
            // do not process this measure
            continue;
        }


        $outXML .= '<measure number="' . ($i + (1 - $emptyMeasureCount)) . '">';

        if ($i === 0) {
            $multiplier = (4 / $dom->getElementsByTagName("divisions")->item(0)->childNodes->item(0)->nodeValue);
            $outXML .= '<attributes><divisions>4</divisions><key><fifths>';

            if ($dom->getElementsByTagName("fifths")->length > 0) {
                $outXML .= $dom->getElementsByTagName("fifths")->item(0)->childNodes->item(0)->nodeValue;
            } else {
                $outXML .= "0";
            }

            $outXML .= '</fifths></key><time><beats>';
            $outXML .= $dom->getElementsByTagName("beats")->item(0)->childNodes->item(0)->nodeValue;
            $outXML .= "</beats><beat-type>";
            $outXML .= $dom->getElementsByTagName("beat-type")->item(0)->childNodes->item(0)->nodeValue;
            $outXML .= "</beat-type></time></attributes><direction>";


            if ($dom->getElementsByTagName("sound")->length > 0) {
                $outXML .= '<sound tempo="' . $dom->getElementsByTagName("sound")->item(0)->getAttribute("tempo") . '"/>';
            } else {
                $outXML .= '<sound tempo="90"/>';
            }
            $outXML .= "</direction>";
        }

        // add repeats support
        $barlines = $measures->item($i)->getElementsByTagName("barline");

        if (is_object($barlines)) {
            if ($barlines->length > 0) {
                $outBarlinesDom = new DOMDocument();
                foreach ($barlines as $barline) {

                    //add the outer dom element
                    $elOutBarlineRoot = $outBarlinesDom->createElement("barline");
                    //ad input barlines atrib to output dom barline
                    if ($barline->hasAttributes()) {
                        foreach ($barline->attributes as $attrib) {
                            $elOutBarlineRoot->setAttribute($attrib->nodeName, $attrib->nodeValue);
                        }
                    }
                    // add the barlines attributes to the element
                    $outBarlinesDom->appendChild($elOutBarlineRoot);
//                    echo "found bar line \n";
//                  //HANDLE VOLTAS (ending tag)
                    $elInEndings = $barline->getElementsByTagName("ending");

                    if ($elInEndings->length > 0) {
                        // this loop should have ony one element so foreach should iter only once
                        // create an eding element
                        $elOutEnding = $outBarlinesDom->createElement("ending");

                        // add the source ending element's attribs to the newly created elem
                        foreach ($elInEndings->item(0)->attributes as $attrib) {
                            $elOutEnding->setAttribute($attrib->nodeName, $attrib->nodeValue);
                        }

                        // add the ending tag to the barline root elem
                        $elOutBarlineRoot->appendChild($elOutEnding);
                    }
//                  
                    //HANDLE REPEAT TAG INSIDE BARLINE
                    $elInRepeat = $barline->getElementsByTagName("repeat");

                    //check if repeat exists
                    if ($elInRepeat->length > 0) {
                        // add the repeat tag inside
                        $elRepeat = $outBarlinesDom->createElement("repeat");
                        // check if there is a times attribute for a repeat
                        //there is always a direction attrib for a barline
                        if ("backward" === $elInRepeat->item(0)->getAttribute("direction")) {
                            if ($elInRepeat->item(0)->hasAttribute("times")) {

                                $inElReapeatAttrNode = $elInRepeat->item(0)->getAttributeNode("times");
                                $elRepeat->setAttribute($inElReapeatAttrNode->name, $inElReapeatAttrNode->value);
                            } else {
                                $elRepeat->setAttribute("times", 1);
                            }
                        }

                        foreach ($elInRepeat->item(0)->attributes as $attrib) {
                            $elRepeat->setAttribute($attrib->nodeName, $attrib->nodeValue);
                        }

                        // append repeat element to the barline root element
                        $elOutBarlineRoot->appendChild($elRepeat);

                        // store this into the outXML
                        $outXML .= $outBarlinesDom->saveXML($elOutBarlineRoot);
//                        echo $outBarlinesDom->saveXML($elOutBarlineRoot);
                    }
                }
            }
        }



        // we only need the notes, no stupid <print> stuff or text nodes (whitespaces/tabs/newlines etc.)
        $notes = $measures->item($i)->getElementsByTagName("note");
        echo "DEBUG: measure " . ($i + 1) . " has " . $notes->length . " notes\n";


        $noteCounter = 0;
        foreach ($notes as $note) {
            $outXML .= "<note>";
            $duration = 1;

            $noteCounter++;
            echo "processing measure " . ($i + 1) . ", note " . $noteCounter . "\n";

            foreach ($note->childNodes as $noteChild) {
                if ($noteChild->nodeName === "rest") {
                    $outXML .= "<rest/>";
                } else if ($noteChild->nodeName === "chord") {
                    $outXML .= "<chord/>";
                } else if ($noteChild->nodeName === "duration") {
                    $duration = $noteChild->nodeValue;
                } else if ($noteChild->nodeName === "pitch") {
                    $outXML .= "<pitch>";
                    $alter = 0;
                    foreach ($noteChild->childNodes as $pitchNode) {
                        if ($pitchNode->nodeName === "step" || $pitchNode->nodeName === "octave") {
                            $outXML .= "<" . $pitchNode->nodeName . ">" . $pitchNode->nodeValue . "</" . $pitchNode->nodeName . ">";
                        } else if ($pitchNode->nodeName === "alter") {
                            $alter = $pitchNode->nodeValue;
                        }
                    }
                    $outXML .= "<alter>" . $alter . "</alter></pitch>";
                }
            }

            $outXML .= "<duration>" . ($duration * $multiplier) . "</duration>";
            $outXML .= "</note>";
        }

        $outXML .= '</measure>';
    } // close of main measures loop
    // close outfile and write it
    $outXML .= '</part></score-partwise>';
    return $outXML;
}
