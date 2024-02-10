# ChroniclingAmericaQA: A Large-scale Question Answering Dataset based on Historical American Newspaper Pages

ChroniclingAmetricaQA, is a large-scale question-answering dataset comprising 485k question-answer pairs over a collection of historical American newspapers to facilitate the development of QA and MRC systems over historical texts.

## Download Links

### Dataset

Structured as JSON files, the ChricinclingAmericaQA dataset includes `train.json`, `val.json`, and `test.json` for training, validation, and testing phases, respectively.

- **Data Structure**: 
```json
[
    {
        "qestion": "",
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


- **Training Set**: [Download](https://huggingface.co/datasets/Bhawna/ChroniclingAmericaQA/resolve/main/Train.json?download=true)
- **Development Set**: [Download](https://huggingface.co/datasets/Bhawna/ChroniclingAmericaQA/blob/main/Dev.json?download=true)
- **Test Set**: [Download](https://huggingface.co/datasets/Bhawna/ChroniclingAmericaQA/resolve/main/Test.json?download=true)


### Dataset Statistics
|                   | Training  | Development | Test   |
| ----------------- | --------- | ----------- | ------ |
| Num. of Questions | 439,302   | 24,111      | 24,084 |
