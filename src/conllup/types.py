from typing import Dict, TypedDict


featuresJson_T = Dict[str, str]
depsJson_T = Dict[str, str]

class tokenJson_T(TypedDict):
    ID: str
    FORM: str
    LEMMA: str
    UPOS: str
    XPOS: str
    FEATS: featuresJson_T
    HEAD: int
    DEPREL: str
    DEPS: depsJson_T
    MISC: featuresJson_T

tokensJson_T = Dict[str, tokenJson_T]
nodesJson_T = tokensJson_T
groupsJson_T = tokensJson_T
enhancedNodesJson_T = tokensJson_T

class treeJson_T(TypedDict):
    nodesJson: nodesJson_T
    groupsJson: groupsJson_T
    enhancedNodesJson: enhancedNodesJson_T


metaJson_T = Dict[str, str]

class sentenceJson_T(TypedDict):
    metaJson: metaJson_T
    treeJson: treeJson_T

