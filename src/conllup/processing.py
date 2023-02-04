from typing import List, Tuple
from .types import treeJson_T
from .conllup import _isGroupToken


mappingSpacesAfter: List[Tuple[str, str]] = [
    ("\\s", "s"),
    ("\\\\t", "\t"),
    ("\\\\n", "\n"),
    ("\\\\v", "\v"),
    ("\\\\f", "\f"),
    ("\\\\r", "\r"),
]


def constructTextFromTreeJson(treeJson: treeJson_T) -> str:
    sentence = ""
    for token in treeJson["nodesJson"].values():
        if token and _isGroupToken(token) == False:
            form = token["FORM"]
            space = "" if token["MISC"].get("SpaceAfter") == "No" else " "
            if token["MISC"].get("SpacesAfter"):
                spaces = token["MISC"].get("SpacesAfter", '')
                for SpaceAfter, SpaceAfterConverted in mappingSpacesAfter:
                    spaces = spaces.replace(SpaceAfter, SpaceAfterConverted)

                sentence = sentence + form + spaces
                continue
            sentence = sentence + form + space
    return sentence
