import os
import xml.etree.ElementTree as ET
from psmusicxmlconv import MusicXMLConverter


def get_test_data_dir():
    dir = os.path.dirname(os.path.abspath('__file__'))
    path = os.path.abspath(os.path.join(dir, "test_data"))
    return path


def test_measure_is_silent():
    path = os.path.join(get_test_data_dir(), 'measures', 'plain_silent_mid_measure.xml')
    inputTree = ET.parse(path)
    testMeasure = inputTree.getroot()
    conv = MusicXMLConverter.MusicXMLConverter()
    assert conv.measureIsSilent(testMeasure) == True

def test_measure_is_empty():
    path = os.path.join(get_test_data_dir(), 'measures', 'plain_empty_mid_measure.xml')
    inputTree = ET.parse(path)
    testMeasure = inputTree.getroot()
    conv = MusicXMLConverter.MusicXMLConverter()
    assert conv.measureIsEmpty(testMeasure) == True