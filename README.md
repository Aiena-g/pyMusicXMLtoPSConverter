# pyMusicXMLtoPSConverter

**DESCRIPTION**
A pure python 3 converter to convert scores exported as Music XML from Musescore into PlaneShift(PS) compatible ones

**INSTALLATION**
1) Make sure you have the following installed:
    The application needs python 3 and python3 tk (tkinter) integration support for showing the GUI.
    So on Ubuntu for example you would install the below 2 packages
    1) python3
    2) python3-tk

**RUNNING**
1) Make sure you have the above dependencies
3) make "launchConverter.sh" executable
4) Run "launchConverter.sh"
2) Specify default directories to look for source scores(from Musescore) and store PS converted scores in
5) Choose source score by pressing browse button
6) choose destination score by pressing convert button
7) Hit the "Convert XML" button
8) Import into PS and test :)

**EXPECTED INPUT**
1) The program expects the input to be in the MusicXML format. The application has been tested only against MusicXML 
exported from Musescore. The application may work with MusicXML exported from Finale/Siblelius other applications 
but it has not been tested and is not supported.
2) Please use a score with only one instrument and one voice. Multiple instruments, voices are not supported.

**EXPECTED OUTPUT**
A cleaned up and converted MusicXML score in the format needed for PS to process and use it

**NOTES**
1) This software is still in very early development
