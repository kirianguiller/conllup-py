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