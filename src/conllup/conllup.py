import os.path
from typing import Dict, List, TypedDict, Union, Literal

from .types import featuresJson_T, tokenJson_T, metaJson_T, treeJson_T, sentenceJson_T, tokensJson_T

tabLabel_T = Literal[
    "ID", "FORM", "LEMMA", "UPOS", "XPOS", "FEATS", "HEAD", "DEPREL", "DEPS", "MISC"
]
tabType_T = Literal["str", "int", "dict"]


class tabMeta_T(TypedDict):
    label: tabLabel_T
    type: tabType_T


def emptyFeaturesJson() -> featuresJson_T:
    return {}


def emptyNodeJson(ID: str = "_", FORM: str = "_", LEMMA: str = "_", UPOS: str = "_", XPOS: str = "_",
                  FEATS: featuresJson_T = {},
                  HEAD: int = -1,
                  DEPREL: str = "_", DEPS: featuresJson_T = {}, MISC: featuresJson_T = {}) -> tokenJson_T:
    return {
        "ID": ID,
        "FORM": FORM,
        "LEMMA": LEMMA,
        "UPOS": UPOS,
        "XPOS": XPOS,
        "FEATS": FEATS,
        "HEAD": HEAD,
        "DEPREL": DEPREL,
        "DEPS": DEPS,
        "MISC": MISC,
    }


def emptyMetaJson() -> metaJson_T:
    return {}


def emptyNodesOrGroupsJson() -> Dict[str, tokenJson_T]:
    return {}


def emptyTreeJson() -> treeJson_T:
    return {
        "nodesJson": emptyNodesOrGroupsJson(),
        "groupsJson": emptyNodesOrGroupsJson(),
    }


def emptySentenceJson() -> sentenceJson_T:
    return {
        "metaJson": emptyMetaJson(),
        "treeJson": emptyTreeJson(),
    }


def _featuresConllToJson(featuresConll: str) -> featuresJson_T:
    if featuresConll == "_":
        return {}

    featuresJson = emptyFeaturesJson()
    splittedFeaturesStrings = featuresConll.split("|")

    for featureKeyValue in splittedFeaturesStrings:
        splittedFeature = featureKeyValue.split("=")
        featureKey = splittedFeature[0]
        featureValue = "=".join(
            splittedFeature[1:]
        )  # reconstructing for this case : 'person=first=second'
        if featuresJson.get(featureKey):
            # we add all duplicated keys in this list, as it's forbidden in conll format
            raise Exception(f"DUPLICATED KEY : found (among others) the duplicated `{featureKey}` key")
        featuresJson[featureKey] = featureValue

    return featuresJson


def _featuresJsonToConll(featuresJson: featuresJson_T) -> str:
    featureItems = list(featuresJson.items())
    featureItems.sort(key=lambda item: item[0].lower())
    splittedFeatureConll=[f"{item[0]}={item[1]}" for item in featureItems]
    featuresConll = "|".join(splittedFeatureConll)
    if featuresConll == "":
        featuresConll = "_"
    return featuresConll


def _normalizeHyphensInTab(tokenTabData: str, tabLabel: str):
    """
    Some conll can be unproperly formatted, with different type of hyphens
    instead of the standard underscore "_"
    """
    if not tabLabel in ["FORM", "LEMMA"] and tokenTabData in ["-", "–"]:
        return "_"
    return tokenTabData


def _encode_int_data(data):
    if data == -1:
        return "_"
    else:
        return str(data)

def _decode_int_data(data):
    if data == "_":
        return -1
    else:
        return int(data, 10)

def _tokenConllToJson(nodeConll: str) -> tokenJson_T:
    trimmedNodeConll = nodeConll.rstrip().strip()
    splittedNodeConll = trimmedNodeConll.split("\t")
    if len(splittedNodeConll) != 10:
        raise Exception(
            f'COLUMNS NUMBER ERROR : {len(splittedNodeConll)} columns found instead of 10  --- line content = "{nodeConll}"'
        )

    tokenJson = {
        "ID": splittedNodeConll[0],
        "FORM": splittedNodeConll[1],
        "LEMMA": splittedNodeConll[2],
        "UPOS": splittedNodeConll[3],
        "XPOS": splittedNodeConll[4],
        "FEATS": _featuresConllToJson(splittedNodeConll[5]),
        "HEAD": _decode_int_data(splittedNodeConll[6]),
        "DEPREL": splittedNodeConll[7],
        "DEPS": _featuresConllToJson(splittedNodeConll[8]),
        "MISC": _featuresConllToJson(splittedNodeConll[9])
    }
    return tokenJson


class _seperateMetaAndTreeFromSentenceConll_RV(TypedDict):
    metaLines: List[str]
    treeLines: List[str]


def _seperateMetaAndTreeFromSentenceConll(
        sentenceConll: str,
) -> _seperateMetaAndTreeFromSentenceConll_RV:
    trimmedSentenceConll = sentenceConll.rstrip().strip()
    linesConll = trimmedSentenceConll.split("\n")

    metaLines: List[str] = []
    treeLines: List[str] = []
    for lineConll in linesConll:
        trimmedLineConll = lineConll.rstrip().strip()
        if trimmedLineConll[0] == "#":
            metaLines.append(trimmedLineConll)
        elif not trimmedLineConll[0].isnumeric():
            raise Exception(
                f"Warning: line didnt't start with a digit or '#' : '{trimmedLineConll}'"
            )
        else:
            treeLines.append(trimmedLineConll)

    if len(treeLines) == 0:
        print(f"Invalid CONLL : No token found \n$ '{sentenceConll}'")
    return {"metaLines": metaLines, "treeLines": treeLines}


def _isGroupToken(tokenJson: tokenJson_T) -> bool:
    return "-" in tokenJson["ID"]


def _metaConllLinesToJson(metaConllLines: List[str]) -> metaJson_T:
    metaJson: metaJson_T = emptyMetaJson()
    for metaCouple in metaConllLines:
        if " = " not in metaCouple:
            # unvalid line, skipping
            continue
        splittedKeyValue = metaCouple.split(" = ")
        if len(splittedKeyValue) == 2:
            # normal situation : `# meta_key = my meta value`
            [metaKey, metaValue] = splittedKeyValue
        elif len(splittedKeyValue) == 1:
            # weird case with no value, like : `# text_ortho = `
            metaKey = splittedKeyValue[0]
            metaValue = ""
        elif len(splittedKeyValue) >= 3:
            # if "=" signe occur in the value : `# text = 2 + 2 = 1`
            metaKey = splittedKeyValue[0]
            metaValue = " = ".join(splittedKeyValue[1:])
        else:
            # weird case (len = 0), where no "=" is in the meta, we skip it
            continue
        trimmedMetaKey = metaKey.strip("# ")
        metaJson[trimmedMetaKey] = metaValue
    return metaJson


def _treeConllLinesToJson(treeConllLines: List[str]) -> treeJson_T:
    treeJson = emptyTreeJson()

    for tokenConll in treeConllLines:
        tokenJson = _tokenConllToJson(tokenConll)
        if _isGroupToken(tokenJson) == True:
            # the token is a group token
            treeJson["groupsJson"][tokenJson["ID"]] = tokenJson
        else:
            # the token is a normal token
            treeJson["nodesJson"][tokenJson["ID"]] = tokenJson
    return treeJson


def sentenceConllToJson(sentenceConll: str) -> sentenceJson_T:
    if type(sentenceConll) != str:
        raise Exception(
            f"parameter `sentenceConll` in sentenceConllToJson() is not a string (got `{type(sentenceConll)}`"
        )
    sentenceJson: sentenceJson_T = emptySentenceJson()
    seperatedMetaAndTree = _seperateMetaAndTreeFromSentenceConll(sentenceConll)

    sentenceJson["metaJson"] = _metaConllLinesToJson(seperatedMetaAndTree["metaLines"])
    sentenceJson["treeJson"] = _treeConllLinesToJson(seperatedMetaAndTree["treeLines"])

    return sentenceJson


def _tokenJsonToConll(tokenJson: tokenJson_T) -> str:
    ID = tokenJson["ID"]
    FORM = tokenJson["FORM"]
    LEMMA = tokenJson["LEMMA"]
    UPOS = tokenJson["UPOS"]
    XPOS = tokenJson["XPOS"]
    FEATS = _featuresJsonToConll(tokenJson["FEATS"])
    HEAD = _encode_int_data(tokenJson["HEAD"])
    DEPREL = tokenJson["DEPREL"]
    DEPS = _featuresJsonToConll(tokenJson["DEPS"])
    MISC = _featuresJsonToConll(tokenJson["MISC"])

    tokenConll = f"{ID}\t{FORM}\t{LEMMA}\t{UPOS}\t{XPOS}\t{FEATS}\t{HEAD}\t{DEPREL}\t{DEPS}\t{MISC}"
    return tokenConll


def _compareTokenIndexes(a: str, b: str) -> int:
    a1 = int(a.split('-')[0])
    b1 = int(b.split('-')[0])
    if a1 - b1 != 0:
        return a1 - b1
    else:
        return len(b) - len(a)


import functools


def _sortTokenIndexes(tokenIndexes: List[str]) -> List[str]:
    return sorted(tokenIndexes, key=functools.cmp_to_key(_compareTokenIndexes))

def _sortTokensJson(tokensJson: tokensJson_T) -> tokensJson_T:
    sortedTokensJson: tokensJson_T = {}
    tokenIndexes = list(tokensJson.keys())
    sortedTokenIndexes = _sortTokenIndexes(tokenIndexes)
    for tokenIndex in sortedTokenIndexes:
        sortedTokensJson[tokenIndex] = tokensJson[tokenIndex]
    return sortedTokensJson

def _treeJsonToConll(treeJson: treeJson_T) -> str:
    treeConllLines: List[str] = []
    tokensJson = {**treeJson["nodesJson"], **treeJson["groupsJson"]}
    tokenIndexes = [token["ID"] for token in tokensJson.values()]
    sortedTokenIndexes = _sortTokenIndexes(tokenIndexes)
    for tokenIndex in sortedTokenIndexes:
        tokenJson = tokensJson[tokenIndex]
        tokenConll = _tokenJsonToConll(tokenJson)
        treeConllLines.append(tokenConll)

    treeConll = '\n'.join(treeConllLines)
    return treeConll


def _metaJsonToConll(metaJson: metaJson_T) -> str:
    metaConllLines: List[str] = []

    for metaKey in metaJson:
        metaValue = metaJson[metaKey]
        metaConllLine = f"# {metaKey} = {metaValue}"
        metaConllLines.append(metaConllLine)

    metaConll = '\n'.join(metaConllLines)

    return metaConll


def sentenceJsonToConll(sentenceJson: sentenceJson_T) -> str:
    metaConll = _metaJsonToConll(sentenceJson["metaJson"])
    treeConll = _treeJsonToConll(sentenceJson["treeJson"])
    return "\n".join([metaConll, treeConll]).strip() + "\n"




class EmptyConllError(Exception):
    pass

class ConllParseError(Exception):
    pass

def findConllFormatErrors(conllText):
    errorsMessages = []
    for idxLine, line in enumerate(conllText.rstrip().split("\n"), start=1):
        errorSuffix = f"Line {idxLine} : "
        if line.strip().rstrip():
            if line[0] != "#":
                try:
                    _tokenConllToJson(line)
                except Exception as e:
                    errorsMessages.append(errorSuffix + str(e))
    return errorsMessages


def readConlluFile(filePath: str, keepEmptyTrees = False):
    if not os.path.isfile(filePath):
        raise FileNotFoundError(f"No file found `{filePath}`")

    if os.path.getsize(filePath) == 0:
        raise EmptyConllError(f"You provided an empty conllu `{filePath}`")

    sentencesJson: List[sentenceJson_T] = []
    with open(filePath, "r", encoding="utf-8") as infile:
        conllContent = infile.read().rstrip()

    try:
        for potentialSentenceConll in conllContent.split("\n\n"):
            if potentialSentenceConll.strip():
                sentenceJson = sentenceConllToJson(potentialSentenceConll)
                if keepEmptyTrees or len(sentenceJson["treeJson"]["nodesJson"].values()):
                    sentencesJson.append(sentenceConllToJson(potentialSentenceConll))

    except Exception as e:
        errors = findConllFormatErrors(conllContent)
        if len(errors):
            # we have detected errors manually
            errorText = "\n".join(findConllFormatErrors(conllContent))
        else:
            # no error was found manually, the error is something else
            errorText = str(e)
        fileName = filePath.split("/")[-1]
        raise ConllParseError(f"Parsing Errors with file `{fileName}` :\n{errorText}")

    return sentencesJson


def _getStringForManySentencesJson(sentencesJson: List[sentenceJson_T]):
    sentencesConll = [sentenceJsonToConll(sentenceJson) for sentenceJson in sentencesJson]
    concatString = "\n".join(sentencesConll) + "\n"
    return concatString


def writeConlluFile(filePath: str, sentencesJson: List[sentenceJson_T], overwrite=False):
    if (overwrite is False) and os.path.isfile(filePath):
        raise Exception(f"Already found a file in`{filePath}`. Consider passing `overwrite=True` to this function")
    concatSentencesConll = _getStringForManySentencesJson(sentencesJson)
    with open(filePath, "w", encoding="utf-8") as outfile:
        outfile.write(concatSentencesConll)
