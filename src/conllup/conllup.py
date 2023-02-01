from typing import Dict, List, TypedDict, Union, Literal

from .types import featuresJson_T, tokenJson_T, metaJson_T, treeJson_T, sentenceJson_T

tabLabel_T = Literal[
    "ID", "FORM", "LEMMA", "UPOS", "XPOS", "FEATS", "HEAD", "DEPREL", "DEPS", "MISC"
]
tabType_T = Literal["str", "int", "dict"]


class tabMeta_T(TypedDict):
    label: tabLabel_T
    type: tabType_T


CONLL_STRUCTURE: Dict[int, tabMeta_T] = {
    0: {"label": "ID", "type": "str"},
    1: {"label": "FORM", "type": "str"},
    2: {"label": "LEMMA", "type": "str"},
    3: {"label": "UPOS", "type": "str"},
    4: {"label": "XPOS", "type": "str"},
    5: {"label": "FEATS", "type": "dict"},
    6: {"label": "HEAD", "type": "int"},
    7: {"label": "DEPREL", "type": "str"},
    8: {"label": "DEPS", "type": "dict"},
    9: {"label": "MISC", "type": "dict"},
}


def emptyFeaturesJson() -> featuresJson_T:
    return {}


def emptyNodeJson() -> tokenJson_T:
    return {
        "ID": "_",
        "FORM": "_",
        "LEMMA": "_",
        "UPOS": "_",
        "XPOS": "_",
        "FEATS": emptyFeaturesJson(),
        "HEAD": -1,
        "DEPREL": "_",
        "DEPS": emptyFeaturesJson(),
        "MISC": emptyFeaturesJson(),
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


def _featuresConllToJson(featuresConll):
    if featuresConll == "_":
        return emptyFeaturesJson()

    featuresJson = emptyFeaturesJson()
    splittedFeaturesStrings = featuresConll.split("|")

    for featureKeyValue in splittedFeaturesStrings:
        splittedFeature = featureKeyValue.split("=")
        featureKey = splittedFeature[0]
        featureValue = "=".join(
            splittedFeature[1:]
        )  # reconstructing for this case : 'person=first=second'
        featuresJson[featureKey] = featureValue

    return featuresJson


def _featuresJsonToConll(featuresJson: featuresJson_T) -> str:
    splittedFeatureConll: List[str] = []
    for [featureKey, featureValue] in featuresJson.items():
        splittedFeatureConll.append(f"{featureKey}={featureValue}")
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


def _decodeTabData(tokenTabData: str, type: str) -> Union[str, int, featuresJson_T]:
    if type == "str":
        return tokenTabData
    elif type == "int":
        if tokenTabData == "_":
            return -1
        else:
            return int(tokenTabData, 10)

    elif type == "dict":
        return _featuresConllToJson(tokenTabData)
    else:
        raise Exception(f"{type} is not a correct type")


def _encodeTabData(tabData: Union[featuresJson_T, str, int]) -> str:
    if type(tabData) == str:
        return tabData
    elif type(tabData) == int:
        if tabData == -1:
            return "_"
        else:
            return str(tabData)
    elif type(tabData) == dict:
        return _featuresJsonToConll(tabData)
    else:
        raise Exception(f"Wrong type for tabData `{type(tabData)}`")


def _tokenConllToJson(nodeConll: str) -> tokenJson_T:
    trimmedNodeConll = nodeConll.rstrip().strip()
    splittedNodeConll = trimmedNodeConll.split("\t")
    if len(splittedNodeConll) != 10:
        raise Exception(
            f'CONLL PARSING ERROR : line "{nodeConll}" is not valid, {len(splittedNodeConll)} columns found instead of 10'
        )

    tokenJson = emptyNodeJson()
    for [tabIndex, tabMeta] in CONLL_STRUCTURE.items():
        tabLabel = tabMeta["label"]
        tabType = tabMeta["type"]

        tabDataUnormalized = splittedNodeConll[tabIndex]
        tabData = _normalizeHyphensInTab(tabDataUnormalized, tabLabel)

        tokenJson[tabLabel] = _decodeTabData(tabData, tabType)

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
        raise Exception(f"Invalid CONLL : No token found \n$ '{sentenceConll}'")
    return {"metaLines": metaLines, "treeLines": treeLines}


def _isGroupToken(tokenJson: tokenJson_T) -> bool:
    return "-" in tokenJson["ID"]


def _metaConllLinesToJson(metaConllLines: List[str]) -> metaJson_T:
    metaJson: metaJson_T = emptyMetaJson()
    for metaCouple in metaConllLines:
        [metaKey, metaValue] = metaCouple.split(" = ")
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
    splittedTokenConll: List[str] = []
    for tabIndex in CONLL_STRUCTURE:
        tabMeta = CONLL_STRUCTURE[tabIndex]
        tabLabel = tabMeta["label"]

        tabDataJson = tokenJson[tabLabel]
        tabDataConll = _encodeTabData(tabDataJson)
        splittedTokenConll.append(tabDataConll)
    tokenConll = "\t".join(splittedTokenConll)
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
  if metaConll == '':
    return treeConll
  return f"{metaConll}\n{treeConll}"
