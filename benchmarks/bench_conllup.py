from data import PATH_DATA, PATH_OUTPUT

from conllup.conllup import readConlluFile, writeConlluFile


def conllup_load():
    sentences = readConlluFile(PATH_DATA)
    token_counter = 0
    for sentence in sentences:
        for token in sentence['treeJson']['nodesJson'].values():
            if token['ID']:
               token_counter += 1
    return token_counter


def conllup_load_and_save():
    sentences = readConlluFile(PATH_DATA)
    writeConlluFile(PATH_OUTPUT, sentences, overwrite=True)

if __name__ == "__main__":
    # print(conllup_load())
    conllup_load_and_save()