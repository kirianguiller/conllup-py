from src.conllup.types import sentenceJson_T
from src.conllup.conllup import emptyMetaJson, emptyNodesOrGroupsJson
from src.conllup.processing import constructTextFromTreeJson

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
