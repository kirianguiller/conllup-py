from data import PATH_DATA, PATH_OUTPUT

from pyconll import load_from_file


def pyconll_load():
    sentences = load_from_file(PATH_DATA)
    counter = 0
    for sentence in sentences:
        for token in sentence:
            if token.id:
                counter += 1
    return counter


def pyconll_load_and_save():
    sentences = load_from_file(PATH_DATA)
    with open(PATH_OUTPUT, "w") as outfile:
        sentences.write(outfile)


if __name__ == "__main__":
    print(pyconll_load())
