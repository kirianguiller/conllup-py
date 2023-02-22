import os
import timeit
from conllup.conllup import readConlluFile

from data import PATH_OUTPUT, PATH_DATA

data_sentences_number = len(readConlluFile(PATH_DATA))

print(f"Testing on `{PATH_DATA}` file, composed of `{data_sentences_number}` sentences \n...\n")

ITERATIONS = 1
ROUNDING = 3

conllup_load = timeit.timeit('conllup_load()', number=ITERATIONS, setup="from bench_conllup import conllup_load") / ITERATIONS
print("conllup_load :", round(conllup_load * 1000 / data_sentences_number, ROUNDING), "s per 1k sentences")


conllu_load = timeit.timeit('conllu_load()', number=ITERATIONS, setup="from bench_conllu import conllu_load") / ITERATIONS
print("conllu_load :", round(conllu_load * 1000 / data_sentences_number, ROUNDING), "s per 1k sentences")


pyconll_load = timeit.timeit('pyconll_load()', number=ITERATIONS, setup="from bench_pyconll import pyconll_load") / ITERATIONS
print("pyconll_load :", round(pyconll_load * 1000 / data_sentences_number, ROUNDING), "s per 1k sentences")

print("\n")

conllup_load_and_save = timeit.timeit('conllup_load_and_save()', number=ITERATIONS, setup="from bench_conllup import conllup_load_and_save") / ITERATIONS
print("conllup_save :", round((conllup_load_and_save - conllup_load) * 1000 / data_sentences_number, ROUNDING), "s per 1k sentences")


conllu_load_and_save = timeit.timeit('conllu_load_and_save()', number=ITERATIONS, setup="from bench_conllu import conllu_load_and_save") / ITERATIONS
print("conllu_save :", round((conllu_load_and_save - conllu_load) * 1000 / data_sentences_number, ROUNDING), "s per 1k sentences")


pyconll_load_and_save = timeit.timeit('pyconll_load_and_save()', number=ITERATIONS, setup="from bench_pyconll import pyconll_load_and_save") / ITERATIONS
print("pyconll_save :", round((pyconll_load_and_save - pyconll_load) * 1000 / data_sentences_number, ROUNDING), "s per 1k sentences")


os.remove(PATH_OUTPUT)
