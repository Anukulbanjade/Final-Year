# character_mapping.py

# List of Devanagari characters mapped by class index.
character_mapping = [
    "क", "ख", "ग", "घ", "ङ", "च", "छ", "ज", "झ", "ञ",
    "ट", "ठ", "ड", "ढ", "ण", "त", "थ", "द", "ध", "न",
    "प", "फ", "ब", "भ", "म", "य", "र", "ल", "व", "श",
    "ष", "स", "ह", "क्ष", "त्र", "ज्ञ", "०", "१", "२", "३",
    "४", "५", "६", "७", "८", "९"
]

def get_character(class_index):
    """Return the Devanagari character for the given class index."""
    if 0 <= class_index < len(character_mapping):
        return character_mapping[class_index]
    else:
        return None
