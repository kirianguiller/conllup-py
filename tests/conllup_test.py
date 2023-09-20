from pathlib import Path
from typing import List
import pytest
from src.conllup.conllup import (
    _depsConllToJson,
    _depsJsonToConll,
    emptyDepsJson,
    emptyFeaturesJson,
    emptyNodesOrGroupsJson,
    readConlluFile, _getStringForManySentencesJson, EmptyConllError, ConllParseError, _sortTokensJson,
)
from src.conllup.types import (
    sentenceJson_T,
    metaJson_T,
    treeJson_T,
    tokenJson_T,
    groupsJson_T,
    enhancedNodesJson_T
)

from src.conllup.conllup import (
    _featuresConllToJson,
    _featuresJsonToConll,
    _tokenConllToJson,
    _tokenJsonToConll,
    _seperateMetaAndTreeFromSentenceConll,
    _treeConllLinesToJson,
    _metaConllLinesToJson,
    _compareTokenIndexes,
    _sortTokenIndexes,
    sentenceConllToJson,
    sentenceJsonToConll
)


featuresConll = "feat_key1=feat_value1|feat_key2=feat_value2"
featuresConllReverseOrder = "feat_key2=feat_value2|feat_key1=feat_value1"
featuresJson = {"feat_key1": "feat_value1", "feat_key2": "feat_value2"}

tokenConll = "1\tform\tlemma\tupos\txpos\tfeat_key=feat_value\t2\tdeprel\tdep_key:dep_value:dep_aux\tmisc_key=misc_value"

tokenJson: tokenJson_T = {
    "ID": "1",
    "FORM": "form",
    "LEMMA": "lemma",
    "UPOS": "upos",
    "XPOS": "xpos",
    "FEATS": {"feat_key": "feat_value"},
    "HEAD": 2,
    "DEPREL": "deprel",
    "DEPS": {"dep_key": "dep_value:dep_aux"},
    "MISC": {"misc_key": "misc_value"},
}


metaJson: metaJson_T = {"meta_key": "meta_value", "meta_key2": "meta_value2"}
groupsJson: groupsJson_T = emptyNodesOrGroupsJson()
enhancedNodesJson: enhancedNodesJson_T = emptyNodesOrGroupsJson()
treeJson: treeJson_T = {"nodesJson": {"1": tokenJson}, "groupsJson": groupsJson, "enhancedNodesJson": enhancedNodesJson}

sentenceJson: sentenceJson_T = {"metaJson": metaJson, "treeJson": treeJson}

metaConll: str = "# meta_key = meta_value\n# meta_key2 = meta_value2"
metaConllLines: List[str] = metaConll.split("\n")
treeConll: str = f"{tokenConll}"
treeConllLines: List[str] = treeConll.split("\n")
sentenceConll: str = f"{metaConll}\n{treeConll}\n"

untrimmedMetaConll: str = "# meta_key = meta_value\n       # meta_key2 = meta_value2"
untrimmedMetaConllLines: List[str] = metaConll.split("\n")
untrimmedSentenceConll: str = f"{untrimmedMetaConll}\n{treeConll}"


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

# enhanced (empty) node
enhancedNodeConll: str = "1.2	it's	it's	upos	_	_	_	deprel	_	_"
enhancedNodeJson: enhancedNodesJson_T = {
    "ID": "1.2",
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
    with pytest.raises(Exception):
        _featuresConllToJson("bla=1|bla=2") == {"bla", "2"}

def test_featuresJsonToConll():
    assert _featuresJsonToConll(featuresJson) == featuresConll
    assert _featuresJsonToConll({"b": "2", "a": "1"}) == "a=1|b=2"  # test for alphabetical ordering of the features

def test_featuresConllToJsonAndBack():
    # string to json to string
    assert _featuresJsonToConll(_featuresConllToJson(featuresConll)) == featuresConll
    
    # string (reverse order) to json to string
    assert _featuresJsonToConll(_featuresConllToJson(featuresConllReverseOrder)) == featuresConll
    
    # json to string to json
    assert _featuresConllToJson(_featuresJsonToConll(featuresJson)) == featuresJson


depsConll = "1:deprel1|2:deprel2|3.1:deprel3.1|3.2:deprel3.2"
emptyDepsConll = "_"
depsJson = {"1": "deprel1", "2": "deprel2", "3.1": "deprel3.1", "3.2": "deprel3.2"}


def test_depsConllToJson():
    assert _depsConllToJson(depsConll) == depsJson
    assert _depsConllToJson("_") == emptyDepsJson()

def test_depsJsonToConll():
    assert _depsJsonToConll(depsJson) == depsConll
    assert _depsJsonToConll({"1": "deprel1", "2": "deprel2", "3.1": "deprel3.1", "3.2": "deprel3.2"}) == depsConll

def test_tokenConllToJson():
    with pytest.raises(Exception):
        _tokenConllToJson(incompleteSmallerTokenLine)
    with pytest.raises(Exception):
        _tokenConllToJson(incompleteBiggerTokenLine)
    # with pytest.raises(Exception) as exc_info:
    #     _tokenConllToJson("1\t\t_\t\t_\t_\t_\t_\t_\t_")
    # assert str(exc_info.value) == """EMPTY COLUMN ERROR : columns [2, 4] are empty  --- line content = "1\t\t_\t\t_\t_\t_\t_\t_\t_\""""

    assert _tokenConllToJson(tokenConll) == tokenJson
    assert _tokenConllToJson(equalSymbolInMiscOrFeatureTokenConll) == equalSymbolInMiscOrFeatureTokenJson
    assert _tokenConllToJson(groupConll) == groupJson
    assert _tokenConllToJson(enhancedNodeConll) == enhancedNodeJson


def test_tokenJsonToConll():
    assert _tokenJsonToConll(tokenJson) == tokenConll
    assert _tokenJsonToConll(groupJson) == groupConll
    assert _tokenJsonToConll(enhancedNodeJson) == enhancedNodeConll



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
    assert _compareTokenIndexes("3", "1") == 2 # 3 is two after 1
    assert _compareTokenIndexes("1", "4") == -3 # 1 is three before 4
    assert _compareTokenIndexes("2-4", "2") == -1 # 2-4 is one before 2
    assert _compareTokenIndexes("2-3", "2-5") == -2 # 2-3 is two before 2-5
    assert _compareTokenIndexes("2.2", "2") == 1 # 2.2 is after 2 (we don't care how much)
    assert _compareTokenIndexes("3", "3.4") == -1 # 3 is before 3.4 (we don't care how much)
    assert _compareTokenIndexes("4-5", "2.1") == 2 # 4-5 is two after 2.1


def test_sortTokenIndexes():
    assert _sortTokenIndexes(["3-4", "4", "1", "3", "7", "2-6", "2", "3.1", "6"]) == ["1", "2-6", "2", "3-4", "3", "3.1", "4", "6", "7"]


sentenceConll2 = """1-2\tit's\t_\t_\t_\t_\t_\t_\t_\t_
1\tit\tit\t_\t_\t_\t_\t_\t_\t_
2\t's\t's\t_\t_\t_\t_\t_\t_\t_
2.1\t's\t's\t_\t_\t_\t_\t_\t_\t_
"""


def test_sentenceConllToJsonToConll():
    assert sentenceJsonToConll(sentenceConllToJson(sentenceConll)) == sentenceConll
    assert sentenceJsonToConll(sentenceConllToJson(sentenceConll2)) == sentenceConll2


PATH_TEST_DATA_FOLDER = Path(__file__).parent / "data"
PATH_TEST_CONLLU = str(PATH_TEST_DATA_FOLDER / "english.conllu")


def test_readConlluFile():
    sentencesJson = readConlluFile(PATH_TEST_CONLLU)
    assert len(sentencesJson) == 2


PATH_TEST_CONLLU_EMPTY = str(PATH_TEST_DATA_FOLDER / "empty.conllu")
def test_readConllFile_raise_errors():
    with pytest.raises(EmptyConllError):
        readConlluFile(PATH_TEST_CONLLU_EMPTY)

PATH_TEST_CONLLU_CONTAINS_MULTIPLE_ERROR = str(PATH_TEST_DATA_FOLDER / "contains_multiple_errors.conllu")
def test_readConllFile_raise_errors():
    with pytest.raises(ConllParseError) as e_info:
        readConlluFile(PATH_TEST_CONLLU_CONTAINS_MULTIPLE_ERROR)
    assert e_info.value.args[0] == """Parsing Errors with file `contains_multiple_errors.conllu` :\nsent_id = has_9_columns_token_3 - line = 5 : COLUMNS NUMBER ERROR : 9 columns found instead of 10  --- line content = \"3	qu'	que	SCONJ	_	_	2	_	SpaceAfter=No\"\nsent_id = has_9_columns_token_3 - line = 6 : DUPLICATED KEY : found (among others) the duplicated `Mood` key"""


def test_getStringForManySentencesJson():
    assert _getStringForManySentencesJson([sentenceConllToJson(sentenceConll2)]) == sentenceConll2 + "\n"


alphabetical_keys_dict = {
    "1": "un",
    "15": "quinze",
    "4": "quatre",
    "11": "onze",
    "3": "trois",
    "5": "cinq",
    "2": "deux",
}

alphabetical_keys_dict_sorted = {
    "1": "un",
    "2": "deux",
    "3": "trois",
    "4": "quatre",
    "5": "cinq",
    "11": "onze",
    "15": "quinze",
}

def test_sort_tokens_json():
    # /!\ we can't compare directly the dict because the order of the keys is not guaranteed (pytest order the keys alphabetically already, which make the test success even if the order is different)
    assert list(_sortTokensJson(alphabetical_keys_dict).keys()) == list(alphabetical_keys_dict_sorted.keys())