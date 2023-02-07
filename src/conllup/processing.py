import json
from typing import List, Tuple, Literal

from .conllup import _isGroupToken, emptyNodesOrGroupsJson, emptyNodeJson
from .types import treeJson_T, tokenJson_T

mappingSpacesAfter: List[Tuple[str, str]] = [
    ("\\s", "s"),
    ("\\\\t", "\t"),
    ("\\\\n", "\n"),
    ("\\\\v", "\v"),
    ("\\\\f", "\f"),
    ("\\\\r", "\r"),
]


def constructTextFromTreeJson(treeJson: treeJson_T) -> str:
    sentence: str = ""
    for token in treeJson["nodesJson"].values():
        if token and not _isGroupToken(token):
            form = token["FORM"]
            space = "" if token["MISC"].get("SpaceAfter") == "No" else " "
            if token["MISC"].get("SpacesAfter"):
                spaces = token["MISC"].get("SpacesAfter", '')
                for SpaceAfter, SpaceAfterConverted in mappingSpacesAfter:
                    spaces = spaces.replace(SpaceAfter, SpaceAfterConverted)

                sentence = sentence + form + spaces
                continue
            sentence = sentence + form + space
    return sentence


def emptySentenceConllu(sentenceConllu: str) -> str:
    emptiedConllLines = []
    for line in sentenceConllu.split("\n"):
        if line == "":
            # the last element of a newline-splitted conll array might is an empty string
            continue
        if line[0] == "#":
            emptiedConllLines.append(line)
        else:
            [tokenId, tokenForm] = line.split("\t")[0:2]
            emptiedLine = f'{tokenId}\t{tokenForm}\t_\t_\t_\t_\t_\t_\t_\t_'
            emptiedConllLines.append(emptiedLine)
    return "\n".join(emptiedConllLines) + "\n"


def changeMetaFieldInSentenceConllu(conllu: str, targetField: str, newValue: str) -> str:
    outputConlluLines = []
    for line in conllu.split("\n"):
        if line.startswith("#"):
            field = line.split(" = ")[0].strip("# ")
            if field == targetField:
                line = "# " + targetField + " = " + str(newValue)

        outputConlluLines.append(line)

    return "\n".join(outputConlluLines)


def incrementIndex(
        idOrHead: Literal['ID', 'HEAD'],
        index: int,
        startBefore: int,
        endBefore: int,
        endAfter: int,
        smartBehavior: bool,
) -> int:
    if index < startBefore:
        return index
    elif index > endBefore:
        return index + (endAfter - endBefore)
    elif idOrHead == 'HEAD' and smartBehavior:
        return index
    else:
        return -1


def incrementIndexesOfToken(
        tokenJson: tokenJson_T,
        startBefore: int,
        endBefore: int,
        endAfter: int,
        smartBehavior: bool,
) -> tokenJson_T:
    # handle ID
    if _isGroupToken(tokenJson):
        [tokenJsonId1, tokenJsonId2] = tokenJson["ID"].split('-')
        newTokenJsonId1 = incrementIndex(
            'ID',
            int(tokenJsonId1, 10),
            startBefore,
            endBefore,
            endAfter,
            smartBehavior,
        )
        newTokenJsonId2 = incrementIndex(
            'ID',
            int(tokenJsonId2, 10),
            startBefore,
            endBefore,
            endAfter,
            smartBehavior,
        )
        if newTokenJsonId1 != -1 and newTokenJsonId2 != -1:
            newGroupId = f"{newTokenJsonId1}-{newTokenJsonId2}"
            tokenJson["ID"] = newGroupId
        else:
            tokenJson["ID"] = '-1'
    else:
        tokenJsonId = tokenJson["ID"]
        newTokenJsonId = incrementIndex(
            'ID',
            int(tokenJsonId, 10),
            startBefore,
            endBefore,
            endAfter,
            smartBehavior,
        )
        tokenJson["ID"] = str(newTokenJsonId)

    # handle HEAD
    tokenJsonHead = tokenJson["HEAD"]
    if tokenJsonHead != -1:
        newTokenJsonHead = incrementIndex(
            'HEAD',
            tokenJsonHead,
            startBefore,
            endBefore,
            endAfter,
            smartBehavior,
        )
        tokenJson["HEAD"] = newTokenJsonHead
        if tokenJson["HEAD"] == -1:
            tokenJson["DEPREL"] = '_'
    return tokenJson


replaceAction_T = Literal[
    'SPLIT_ONE_TOKEN_INTO_MANY',  # this one also include the ADD_TOKEN_TO_RIGHT feature
    'RENAME_ONE_TOKEN',
    'DELETE_ONE_TOKEN',
    'OTHER'
]


def replaceArrayOfTokens(
        treeJson: treeJson_T,
        oldTokensIndexes: List[int],
        newTokensForms: List[str],
        smartBehavior: bool = False,
) -> treeJson_T:
    newNodesJson = emptyNodesOrGroupsJson()
    newGroupsJson = emptyNodesOrGroupsJson()

    replaceAction: replaceAction_T = 'OTHER'

    if len(oldTokensIndexes) == 1:
        if len(newTokensForms) == 0:
            replaceAction = 'DELETE_ONE_TOKEN'
        elif len(newTokensForms) == 1:
            replaceAction = 'RENAME_ONE_TOKEN'
        elif len(newTokensForms) >= 1:
            replaceAction = 'SPLIT_ONE_TOKEN_INTO_MANY'
    print(f"replaceArrayOfTokens() : detected action = {replaceAction}")

    startBefore = oldTokensIndexes[0]
    endBefore = oldTokensIndexes[-1]
    endAfter = endBefore + len(newTokensForms) - len(oldTokensIndexes)

    # add new tokens to new tree
    newTokenIndex = oldTokensIndexes[0]
    for newTokenForm in newTokensForms:
        newTokenJson = emptyNodeJson()
        if smartBehavior and (replaceAction == 'RENAME_ONE_TOKEN' or replaceAction == 'SPLIT_ONE_TOKEN_INTO_MANY'):
            oldTokenIndex = oldTokensIndexes[0]
            newTokenJson = json.loads(json.dumps(treeJson["nodesJson"][str(oldTokenIndex)]))
            newTokenJson["HEAD"] = incrementIndex(
                'HEAD',
                newTokenJson["HEAD"],
                startBefore,
                endBefore,
                endAfter,
                smartBehavior,
            )
            newTokenJson["LEMMA"] = newTokenForm
        newTokenJson["ID"] = str(newTokenIndex)
        newTokenJson["FORM"] = newTokenForm
        newNodesJson[newTokenJson["ID"]] = newTokenJson
        newTokenIndex += 1

    # add old tokens with corrected indexes
    for oldTokenJson in {**treeJson["nodesJson"], **treeJson["groupsJson"]}.values():
        oldTokenJsonCopy: tokenJson_T = json.loads(json.dumps(oldTokenJson))
        newTokenJson = incrementIndexesOfToken(
            oldTokenJsonCopy,
            startBefore,
            endBefore,
            endAfter,
            smartBehavior,
        )

        if newTokenJson["ID"] != '-1':
            if _isGroupToken(newTokenJson):
                # the token is a group token
                newGroupsJson[newTokenJson["ID"]] = newTokenJson
            else:
                # the token is a normal token
                newNodesJson[newTokenJson["ID"]] = newTokenJson
    newTreeJson: treeJson_T = {"nodesJson": newNodesJson, "groupsJson": newGroupsJson}
    return newTreeJson
