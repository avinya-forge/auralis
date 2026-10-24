import os
import pytest
from src.engine.precision_polisher import clean_typography, PrecisionPolisher

def test_clean_typography_apostrophes():
    # Contractions
    assert clean_typography("Can'T") == "Can't"
    assert clean_typography("Don'T") == "Don't"
    assert clean_typography("It'S") == "It's"
    assert clean_typography("Ain'T") == "Ain't"
    assert clean_typography("She'S") == "She's"
    assert clean_typography("That'S") == "That's"
    assert clean_typography("You'Re") == "You're"
    assert clean_typography("I'M") == "I'm"
    assert clean_typography("You'Ve") == "You've"
    assert clean_typography("They'Ll") == "They'll"
    assert clean_typography("Dylan'S") == "Dylan's"

def test_clean_typography_ordinals():
    assert clean_typography("115Th Dream") == "115th Dream"
    assert clean_typography("21St Century") == "21st Century"
    assert clean_typography("1St Avenue") == "1st Avenue"
    assert clean_typography("2Nd Time") == "2nd Time"
    assert clean_typography("3Rd Rock") == "3rd Rock"

def test_clean_typography_rock_and_roll():
    assert clean_typography("Rock 'N' Roll") == "Rock 'n' Roll"
    assert clean_typography("Guns N' Roses") == "Guns N' Roses"

def test_precision_polisher_instance():
    polisher = PrecisionPolisher()
    assert polisher.organized_root is not None
