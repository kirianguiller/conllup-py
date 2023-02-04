from src.conllup.types import sentenceJson_T
from src.conllup.conllup import emptyMetaJson, emptyNodesOrGroupsJson
from src.conllup.processing import constructTextFromTreeJson, emptySentenceConllu, changeMetaFieldInSentenceConllu

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
        "MISC": { "SpaceAfter": 'No', "SpacesAfter": '\\\\t' },
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
        "MISC": { "SpacesAfter": '\\\\n\\\\n\\\\t' },
      },
    },
    "groupsJson": emptyNodesOrGroupsJson(),
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