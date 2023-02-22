# Benchmarks for conllup library
## Installation
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the benchmarks
```
source venv/bin/activate
python bench.py
```


## Results 
| Library | load time (s per 1k sent) |  dumps time (s per 1k sent) |
| --- | --- | --- |
| conllup | **0.12** | **0.05** |
| conllu | 0.26 | 0.08 |
| pyconll | **0.11** | 0.09 |