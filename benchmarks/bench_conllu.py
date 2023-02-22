from data import PATH_DATA, PATH_OUTPUT
import conllu


def conllu_load():
    with open(PATH_DATA, "r") as infile:
        sentences = conllu.parse(infile.read())
    token_counter = 0
    for sentence in sentences:
        for token in sentence:
            if token['form']:
                token_counter += 1


def conllu_load_and_save():
    with open(PATH_DATA, "r") as infile:
        sentences = conllu.parse(infile.read())
   
    with open(PATH_OUTPUT, 'w') as outfile:
        outfile.writelines([sentence.serialize() + "\n" for sentence in sentences])