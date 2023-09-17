from src.conllup.conllup import emptyMetaJson, emptyNodesOrGroupsJson, emptyNodeJson
from src.conllup.processing import constructTextFromTreeJson, emptySentenceConllu, changeMetaFieldInSentenceConllu, \
    incrementIndex, incrementIndexesOfToken, replaceArrayOfTokens
from src.conllup.types import sentenceJson_T

sentenceJsonToReconstructTextWithSpacesAfter: sentenceJson_T = {
    "metaJson": emptyMetaJson(),
    "treeJson": {
        "nodesJson": {
            '1': {
                "ID": '1',
                "FORM": 'Ver',
                "LEMMA": '_',
                "UPOS": '_',
                "XPOS": '_',
                "FEATS": {},
                "HEAD": 5,
                "DEPREL": '_',
                "DEPS": {},
                "MISC": {"SpaceAfter": 'No', "SpacesAfter": '\\\\t'},
            },
            '2': {
                "ID": '2',
                "FORM": 'lo',
                "LEMMA": '_',
                "UPOS": '_',
                "XPOS": '_',
                "FEATS": {},
                "HEAD": 0,
                "DEPREL": '_',
                "DEPS": {},
                "MISC": {"SpacesAfter": '\\\\n\\\\n\\\\t'},
            },
        },
        "groupsJson": emptyNodesOrGroupsJson(),
        "enhancedNodesJson": emptyNodesOrGroupsJson(),
    },
}


def test_constructTextFromTreeJson():
    assert constructTextFromTreeJson(sentenceJsonToReconstructTextWithSpacesAfter["treeJson"]) == 'Ver\tlo\n\n\t'


nonEmptySentenceConllu = "# meta_1 = this is meta line\n" \
                         "1\tI\ti\t_\t_\t_\t_\t_\t_\t_\n" \
                         "2\teat\teat\t_\t_\t_\t_\t_\t_\t_\n" \
                         "3\tan\ta\t_\t_\t_\t_\t_\t_\t_\n" \
                         "4\tapple\tapple\t_\t_\t_\t_\t_\t_\t_\n"

emptiedSentenceConllu = "# meta_1 = this is meta line\n" \
                        "1\tI\t_\t_\t_\t_\t_\t_\t_\t_\n" \
                        "2\teat\t_\t_\t_\t_\t_\t_\t_\t_\n" \
                        "3\tan\t_\t_\t_\t_\t_\t_\t_\t_\n" \
                        "4\tapple\t_\t_\t_\t_\t_\t_\t_\t_\n"


def test_emptySentenceConllu():
    assert emptySentenceConllu(emptiedSentenceConllu) == emptiedSentenceConllu


conlluBeforeMetaChange = "# meta_1 = I want to change this meta\n" \
                         "1\tuseless_token\t_\t_\t_\t_\t_\t_\t_\t_\n"

conlluAfterMetaChange = "# meta_1 = New meta value\n" \
                        "1\tuseless_token\t_\t_\t_\t_\t_\t_\t_\t_\n"


def test_changeMetaFieldInSentenceConllu():
    assert changeMetaFieldInSentenceConllu(conlluBeforeMetaChange, "meta_1", "New meta value") == conlluAfterMetaChange


def test_incrementIndex():
    assert incrementIndex('ID', 3, 4, 5, 6, False) == 3
    assert incrementIndex('ID', 6, 4, 5, 7, False) == 8
    assert incrementIndex('ID', 6, 4, 5, 8, False) == 9
    assert incrementIndex('ID', 6, 4, 5, 4, False) == 5
    assert incrementIndex('HEAD', 3, 4, 5, 6, False) == 3
    assert incrementIndex('HEAD', 6, 4, 5, 7, False) == 8
    assert incrementIndex('HEAD', 6, 4, 5, 8, False) == 9
    assert incrementIndex('HEAD', 6, 4, 5, 4, False) == 5


def test_incrementIndexesOfToken():
    assert incrementIndexesOfToken(emptyNodeJson(ID="3"), 4, 5, 6, False) == emptyNodeJson(ID="3")
    assert incrementIndexesOfToken(emptyNodeJson(ID="6"), 4, 5, 7, False) == emptyNodeJson(ID="8")
    assert incrementIndexesOfToken(emptyNodeJson(ID="6", HEAD=8), 4, 5, 7, False) == emptyNodeJson(ID="8", HEAD=10)
    assert incrementIndexesOfToken(emptyNodeJson(ID="6", HEAD=1), 4, 7, 7, False) == emptyNodeJson(ID="-1", HEAD=1)
    assert incrementIndexesOfToken(emptyNodeJson(ID="6-8", HEAD=9), 4, 5, 7, False) == emptyNodeJson(ID="8-10", HEAD=11)
    assert incrementIndexesOfToken(emptyNodeJson(ID="6-8", HEAD=1), 4, 5, 7, False) == emptyNodeJson(ID="8-10", HEAD=1)
    assert incrementIndexesOfToken(emptyNodeJson(ID="6-8", HEAD=1), 4, 7, 7, False) == emptyNodeJson(ID="-1", HEAD=1)
    
    # newly added empty node feature
    assert incrementIndexesOfToken(emptyNodeJson(ID="6.1", HEAD=9), 4, 5, 7, False) == emptyNodeJson(ID="8.1", HEAD=11)
    # newly added deps feature
    assert incrementIndexesOfToken(emptyNodeJson(ID="6.1", HEAD=9, DEPS={"9": "mod"}), 4, 5, 7, False) == emptyNodeJson(ID="8.1", HEAD=11, DEPS={"11": "mod"})

treeJsonBefore = {
    "nodesJson":
        {"1": emptyNodeJson(ID="1", HEAD=4, FORM="Je"),
         "2": emptyNodeJson(ID="2", HEAD=3, FORM="suis"),
         "3": emptyNodeJson(ID="3", HEAD=4, FORM="aujourd'hui"),
         "4": emptyNodeJson(ID="4", HEAD=1, FORM=".")},
    "groupsJson": {},
    "enhancedNodesJson": {},
}

treeJsonAfterWithoutSmartBehavior = {
    "nodesJson":
        {"1": emptyNodeJson(ID="1", HEAD=5, FORM="Je"),
         "2": emptyNodeJson(ID="2", HEAD=-1, FORM="suis"),
         "3": emptyNodeJson(ID="3", HEAD=-1, FORM="aujourd'"),
         "4": emptyNodeJson(ID="4", HEAD=-1, FORM="hui"),
         "5": emptyNodeJson(ID="5", HEAD=1, FORM=".")},
    "groupsJson": {},
    "enhancedNodesJson": {},
}

treeJsonAfterWithSmartBehavior = {
    "nodesJson":
        {"1": emptyNodeJson(ID="1", HEAD=5, FORM="Je"),
         "2": emptyNodeJson(ID="2", HEAD=3, FORM="suis"),
         "3": emptyNodeJson(ID="3", HEAD=5, FORM="aujourd'", LEMMA="aujourd'"),
         "4": emptyNodeJson(ID="4", HEAD=5, FORM="hui", LEMMA="hui"),
         "5": emptyNodeJson(ID="5", HEAD=1, FORM=".")},
    "groupsJson": {},
    "enhancedNodesJson": {},
}


def test_replaceArrayOfTokens():
    assert replaceArrayOfTokens(treeJsonBefore, [3], ["aujourd'", "hui"],
                                smartBehavior=False) == treeJsonAfterWithoutSmartBehavior
    assert replaceArrayOfTokens(treeJsonBefore, [3], ["aujourd'", "hui"],
                                smartBehavior=True) == treeJsonAfterWithSmartBehavior
