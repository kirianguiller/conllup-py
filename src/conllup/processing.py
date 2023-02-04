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
    sentence: str = ""
    for token in treeJson["nodesJson"].values():
        if token and not _isGroupToken(token):
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


def emptySentenceConllu(sentenceConllu: str) -> str:
    emptiedConllLines = []
    for line in sentenceConllu.split("\n"):
        if line == "":
            # the last element of a newline-splitted conll array might is an empty string
            continue
        if line[0] == "#":
            emptiedConllLines.append(line)
        else:
            [tokenId, tokenForm] = line.split("\t")[0:2]
            emptiedLine = f'{tokenId}\t{tokenForm}\t_\t_\t_\t_\t_\t_\t_\t_'
            emptiedConllLines.append(emptiedLine)
    return "\n".join(emptiedConllLines) + "\n"


def changeMetaFieldInSentenceConllu(conllu: str, targetField: str, newValue: str) -> str:
    outputConlluLines = []
    for line in conllu.split("\n"):
        if line.startswith("#"):
            field = line.split(" = ")[0].strip("# ")
            if field == targetField:
                line = "# " + targetField + " = " + str(newValue)

        outputConlluLines.append(line)

    return "\n".join(outputConlluLines)
