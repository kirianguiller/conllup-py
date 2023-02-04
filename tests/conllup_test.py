from typing import List
import pytest
from src.conllup.conllup import (
    emptyFeaturesJson,
    emptyNodeJson,
    emptyNodesOrGroupsJson,
    emptyTreeJson,
    emptyMetaJson,
    emptySentenceJson,
)
from src.conllup.types import (
    sentenceJson_T,
    metaJson_T,
    treeJson_T,
    tokenJson_T,
    groupsJson_T,
)

from src.conllup.conllup import (
    _featuresConllToJson,
    _featuresJsonToConll,
    _tokenConllToJson,
    _tokenJsonToConll,
    _seperateMetaAndTreeFromSentenceConll,
    _decodeTabData,
    _encodeTabData,
    _treeConllLinesToJson,
    _metaConllLinesToJson,
    _compareTokenIndexes,
    _sortTokenIndexes,
    sentenceConllToJson,
    sentenceJsonToConll
)


featuresConll = "feat_key1=feat_value1|feat_key2=feat_value2"
featuresJson = {"feat_key1": "feat_value1", "feat_key2": "feat_value2"}

tokenConll = "1\tform\tlemma\tupos\txpos\tfeat_key=feat_value\t2\tdeprel\tdep_key=dep_value\tmisc_key=misc_value"

tokenJson: tokenJson_T = {
    "ID": "1",
    "FORM": "form",
    "LEMMA": "lemma",
    "UPOS": "upos",
    "XPOS": "xpos",
    "FEATS": {"feat_key": "feat_value"},
    "HEAD": 2,
    "DEPREL": "deprel",
    "DEPS": {"dep_key": "dep_value"},
    "MISC": {"misc_key": "misc_value"},
}


metaJson: metaJson_T = {"meta_key": "meta_value", "meta_key2": "meta_value2"}
groupsJson: groupsJson_T = emptyNodesOrGroupsJson()
treeJson: treeJson_T = {"nodesJson": {"1": tokenJson}, "groupsJson": groupsJson}

sentenceJson: sentenceJson_T = {"metaJson": metaJson, "treeJson": treeJson}

metaConll: str = "# meta_key = meta_value\n# meta_key2 = meta_value2"
metaConllLines: List[str] = metaConll.split("\n")
treeConll: str = f"{tokenConll}"
treeConllLines: List[str] = treeConll.split("\n")
sentenceConll: str = f"{metaConll}\n{treeConll}"

untrimmedMetaConll: str = "# meta_key = meta_value\n       # meta_key2 = meta_value2"
untrimmedMetaConllLines: List[str] = metaConll.split("\n")
untrimmedSentenceConll: str = f"{untrimmedMetaConll}\n{treeConll}"


# checks for hyphen instead of undescore
hyphenInsteadOfUnderscoretokenConll: str = "1	form	lemma	upos	–	–	0	deprel	_	_"
hyphenInsteadOfUnderscoretokenConllCorrected: str = "1	form	lemma	upos	_	_	0	deprel	_	_"
hyphenInsteadOfUnderscoretokenJson: tokenJson_T = {
    "ID": "1",
    "FORM": "form",
    "LEMMA": "lemma",
    "UPOS": "upos",
    "XPOS": "_",
    "FEATS": {},
    "HEAD": 0,
    "DEPREL": "deprel",
    "DEPS": {},
    "MISC": {},
}

# exclude FORM and LEMMA from hyphen-to-underscore replacement
# (there could be a literal hyphen in the text!)
preserveHyphenInFormLemmaTokenConll: str = "1	-	–	upos	_	_	0	deprel	_	_"
preserveHyphenInFormLemmaTokenJson: tokenJson_T = {
    "ID": "1",
    "FORM": "-",
    "LEMMA": "–",
    "UPOS": "upos",
    "XPOS": "_",
    "FEATS": {},
    "HEAD": 0,
    "DEPREL": "deprel",
    "DEPS": {},
    "MISC": {},
}

# checks for "=" symbol is misc or feature field
equalSymbolInMiscOrFeatureTokenConll: str = (
    "1	form	lemma	upos	_	person=first=second	_	_	_	_"
)
# hyphenInsteadOfUnderscoreLineConllCorrected: str = '1	form	lemma	upos	_	_	0	deprel	_	_'
equalSymbolInMiscOrFeatureTokenJson: tokenJson_T = {
    "ID": "1",
    "FORM": "form",
    "LEMMA": "lemma",
    "UPOS": "upos",
    "XPOS": "_",
    "FEATS": {"person": "first=second"},
    "HEAD": -1,
    "DEPREL": "_",
    "DEPS": {},
    "MISC": {},
}

# check for group token, for exemple :
# 1-2  it's  _ _ _ _ _ _ _
# 1    it  it  _ _ _ _ _ _ _
# 2    's  's  _ _ _ _ _ _ _
groupConll: str = "1-2	it's	it's	upos	_	_	_	deprel	_	_"

groupJson: tokenJson_T = {
    "ID": "1-2",
    "FORM": "it's",
    "LEMMA": "it's",
    "UPOS": "upos",
    "XPOS": "_",
    "FEATS": {},
    "HEAD": -1,
    "DEPREL": "deprel",
    "DEPS": {},
    "MISC": {},
}

# incomplete line (different than 10 columns per lines)
incompleteSmallerTokenLine = "1-2	it's	it's	upos	_	_	deprel	_	_"  # has only 9 features
incompleteBiggerTokenLine = "1-2	it's	it's	upos	_	_	deprel	_	_	_	_"  # has 11 features


def test_featuresConllToJson():
    assert _featuresConllToJson(featuresConll) == featuresJson
    assert _featuresConllToJson("_") == emptyFeaturesJson()


def test_featuresJsonToConll():
    assert _featuresJsonToConll(featuresJson) == featuresConll


def test_decodeTabData():
    assert _decodeTabData("3", 'int') == 3
    assert _decodeTabData("3", 'str') == "3"
    assert _decodeTabData("person=first", 'dict') == {"person": "first"}
    with pytest.raises(Exception):
        _decodeTabData("3", 'fake_type')


def test_encodeTabData():
    assert _encodeTabData(3) == "3"
    assert _encodeTabData("3") == "3"
    assert _encodeTabData({"person": "first"}) == "person=first"
    with pytest.raises(Exception):
        _encodeTabData(["1", "2"])



def test_tokenConllToJson():
    with pytest.raises(Exception):
        _tokenConllToJson(incompleteSmallerTokenLine)
    with pytest.raises(Exception):
        _tokenConllToJson(incompleteBiggerTokenLine)

    assert _tokenConllToJson(tokenConll) == tokenJson
    assert _tokenConllToJson(preserveHyphenInFormLemmaTokenConll) == preserveHyphenInFormLemmaTokenJson
    assert _tokenConllToJson(equalSymbolInMiscOrFeatureTokenConll) == equalSymbolInMiscOrFeatureTokenJson
    assert _tokenConllToJson(hyphenInsteadOfUnderscoretokenConll) == hyphenInsteadOfUnderscoretokenJson
    assert _tokenConllToJson(groupConll) == groupJson


def test_tokenJsonToConll():
    assert _tokenJsonToConll(tokenJson) == tokenConll
    assert _tokenJsonToConll(groupJson) == groupConll


def test_seperateMetaAndTreeFromSentenceConll():
    assert _seperateMetaAndTreeFromSentenceConll(sentenceConll) == {
        "metaLines": metaConllLines,
        "treeLines": treeConllLines,
    }
    assert _seperateMetaAndTreeFromSentenceConll(untrimmedSentenceConll) == {
        "metaLines": untrimmedMetaConllLines,
        "treeLines": treeConllLines,
    }


def test_metaConllLinesToJson():
    assert _metaConllLinesToJson(metaConllLines) == metaJson
    assert _metaConllLinesToJson(["# weird_len_1 = "]) == {"weird_len_1": ""}
    assert _metaConllLinesToJson(["# weird_len_3 = 1 + 1 = 3"]) == {"weird_len_3": "1 + 1 = 3"}
    assert _metaConllLinesToJson(["# weird_len_4 = 1 + 1 = 3 = 6/2"]) == {"weird_len_4": "1 + 1 = 3 = 6/2"}
    assert _metaConllLinesToJson(["# weird_len_0"]) == {}


def test_treeConllLinesToJson():
    assert _treeConllLinesToJson(treeConllLines) == treeJson


def test_sentenceConllToJson():
    with pytest.raises(Exception):
        sentenceConllToJson("3")
    assert sentenceConllToJson(sentenceConll) == sentenceJson


def test_sentenceJsonToConll():
    assert sentenceJsonToConll(sentenceJson) == sentenceConll


def test_compareTokenIndexes():
    assert _compareTokenIndexes("3", "1") == 2
    assert _compareTokenIndexes("1", "4") == -3
    assert _compareTokenIndexes("2-4", "2") == -2


def test_sortTokenIndexes():
    assert _sortTokenIndexes(["4", "1", "7", "2-6", "2", "6"]) == ["1", "2-6", "2", "4", "6", "7"]