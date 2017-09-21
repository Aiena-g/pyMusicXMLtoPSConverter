# pyMusicXMLtoPSConverter

**DESCRIPTION**
A pure python 3 converter to convert score rxported as Music XML from Musescire in Planeshift compatible ones

**INSTALLATION**
1) Make sure you have the following installed:
    The application need python 3 and ppython3 tk integration support for showing the GUI.
    Son on Ubuntu for example you would install the below 2 packages
    1) python3
    2) python3-tk

** RUNNUNG**
1) Make sure you have the above dependencies
2) Open up "bin/ConverterUI.py" and update folder paths in these two variables
 "self.MusecoreScoresFolder" AND "self.PlaneShiftScoresFolder" (HINT: search for these in the python file read the comment above and you will know exactly what to do)
3) make "launchConverter.sh" executable
4) Run "launchConverter.sh"
5) Choose source score by pressing browse button
6) choose destination score by pressing convert button
7) Hit the "Convert XML" button
8) Import into PS and test :)

**NOTES**
1)I am yet to replace step 2 (in **RUNNING**) with a configuration file to make things a lot easier.
2) This software is still in very early development)
