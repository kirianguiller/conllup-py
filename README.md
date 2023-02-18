# CONLLUP Python (conllup-py)

Convert .conlly dependency graph to/from JSON format (supported by arboratorgrew)\*

## Usefull links

- [conllup-js](https://github.com/kirianguiller/conllup-js) : Javascript version of this library
- [ArboratorGrew](https://arboratorgrew.elizia.net/#/) : An online collaborative annotation tools, that use the same JSON format for the dependency trees

## sentenceJson interface

```json
{
    "metaJson": {
        "sent_id": "corpusA_sent1",
        "text": "I eat an apple",
    },
    "treeJson": {
        "nodesJson": {
            "1": {
                "ID": "1",
                "FORM": "I",
                "LEMMA": "_",
                "UPOS": "_",
                "XPOS": "_",
                "FEATS": {},
                "HEAD": 4,
                "DEPREL": "_",
                "DEPS": {},
                "MISC": {},
            },
            "2": {
                "ID": "2",
                "FORM": "eat",
                "LEMMA": "_",
                "UPOS": "_",
                "XPOS": "_",
                "FEATS": {},
                "HEAD": 0,
                "DEPREL": "_",
                "DEPS": {},
                "MISC": {},
            },
            "3": {
                "ID": "3",
                "FORM": "an",
                "LEMMA": "a",
                "UPOS": "DET",
                "XPOS": "_",
                "FEATS": {},
                "HEAD": 4,
                "DEPREL": "_",
                "DEPS": {},
                "MISC": {},
            },
            "4": {
                "ID": "4",
                "FORM": "apple",
                "LEMMA": "apple",
                "UPOS": "NOUN",
                "XPOS": "_",
                "FEATS": {},
                "HEAD": 2,
                "DEPREL": "_",
                "DEPS": {},
                "MISC": {},
            }
        },
        "groupsJson": {}
    }
}

```

## Deploy new release

Require to have `pip install twine setuptools build` before doing any build 0) check all tests are passing `python3 -m pytest`

1. change versions
2. build new package `python3 -m build`
3. upload to pypi `python3 -m twine upload --repository pypi dist/*`
4. Optional : if you want to try the testpypi version of the package `pip install --index-url https://test.pypi.org/simple/ --no-deps conllup`

## Changelog
### 0.4.0:
- add `writeConlluFile()` and `readConlluFile()` to handle file reading and writing
### 0.3.1: 
- sorting of feature json when converted to conll string
### 0.3.0: add `replaceArrayOfTokens()` in `processing.py`
### 0.2.1
- fixed : `_metaConllLinesToJson() `when wrong formatting of meta line when missing part after equal sign (`# meta without right part = `)
### 0.2.0
- added `constructTextFromTreeJson` method (in `processing.py` file)
- added `emptySentenceConllu` method (in `processing.py` file)
- added `changeMetaFieldInSentenceConllu` method (in `processing.py` file)
- minor: some more typing annotations
### 0.1.0
First release, with the core methods : `sentenceConllToJson` and `sentenceJsonToConll`