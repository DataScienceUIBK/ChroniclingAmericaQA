# ChroniclingAmericaQA: A Large-scale Question Answering Dataset based on Historical American Newspaper Pages

ChroniclingAmetricaQA, is a large-scale question-answering dataset comprising question-answer pairs over a collection of historical American newspapers to facilitate the development of QA and MRC systems over historical texts. 

## Download Links

### Dataset

Structured as JSON files, the ChricinclingAmericaQA dataset includes `train.json`, `dev.json`, and `test.json` for training, validation, and testing phases, respectively.

- **Data Structure**: 
```json
[
    {
        "question": "",
        "answer": "",
        "org_answer": "",
        "para_id": "",
        "context": "",
        "publication_date": "",
        "trans_que": "",
        "trans_ans": "",
    }
]

```


- **Training Set**: [Download](https://huggingface.co/datasets/Bhawna/ChroniclingAmericaQA/resolve/main/train.json?download=true)
- **Development Set**: [Download](https://huggingface.co/datasets/Bhawna/ChroniclingAmericaQA/resolve/main/dev.json?download=true)
- **Test Set**: [Download](https://huggingface.co/datasets/Bhawna/ChroniclingAmericaQA/resolve/main/test.json?download=true)


### Dataset Statistics
|                   | Training  | Development | Test   |
| ----------------- | --------- | ----------- | ------ |
| Num. of Questions | 439,302   | 24,111      | 24,084 |

## Citation

If you find the dataset helpful, please consider citing our [paper](https://dl.acm.org/doi/10.1145/3626772.3657891).
```
@inproceedings{10.1145/3626772.3657891,
author = {Piryani, Bhawna and Mozafari, Jamshid and Jatowt, Adam},
title = {ChroniclingAmericaQA: A Large-scale Question Answering Dataset based on Historical American Newspaper Pages},
year = {2024},
isbn = {9798400704314},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3626772.3657891},
doi = {10.1145/3626772.3657891},
booktitle = {Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval},
pages = {2038–2048},
numpages = {11},
keywords = {heritage collections, ocr text, question answering},
location = {Washington DC, USA},
series = {SIGIR '24}
}
```
