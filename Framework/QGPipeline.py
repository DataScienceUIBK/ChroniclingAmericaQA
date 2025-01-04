import warnings
warnings.filterwarnings("ignore", message=r"Passing", category=FutureWarning)
warnings.filterwarnings("ignore", message=r"Passing", category=UserWarning)
import os
import torch
import pickle
import itertools
import pandas as pd
import spacy
import time
import json
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from tqdm import tqdm

nlp = spacy.load("en_core_web_sm")

class QGPipeline:
    def __init__(
        self,
        qg_model_name: str,
        min_para_token_num: int,  # Minimum number of tokens in a paragraph to consider for question generation
        min_anssent_token_num: int,  # Minimum number of tokens in a sentence that contains an answer.
        ans_ent_type_exclude_list: list  # List of entity types to exclude when extracting answers
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(qg_model_name, use_fast=False)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(qg_model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.min_para_token_num = min_para_token_num
        self.min_anssent_token_num = min_anssent_token_num
        self.ans_ent_type_exclude_list = ans_ent_type_exclude_list

    def __call__(self, inputs: str):
        nlp_inputs = nlp(" ".join(inputs.split()))
        output = []
        if len(nlp_inputs) < self.min_para_token_num:
            return output
        context = nlp_inputs.text
        sents, sents_pos, answers_pos = self._extract_answers_by_NER(nlp_inputs, context)
        flat_answers_pos = list(itertools.chain(*answers_pos))
        if len(flat_answers_pos) == 0:
            return output
        qg_examples = self._prepare_inputs_for_qg_from_answers_hl(context, sents, sents_pos, answers_pos)
        qg_inputs = [example['source_text'] for example in qg_examples]

        chunk_size = 12
        inputs_batches = [qg_inputs[i:i + chunk_size] for i in range(0, len(qg_inputs), chunk_size)]

        que_list = []
        for batch_input in inputs_batches:
            questions = self._generate_questions(batch_input)

            for example, que in zip(qg_examples, questions):
                if que in que_list:
                    continue
                que_list.append(que)
                output.append({'question': que, 'answer': example['answer'], 'ans_pos': example['answer_pos'], 'ans-sent_pos': example['answer-sent_pos']})
        return output

    def _extract_answers_by_NER(self, nlp_context, context):
        sents, sents_pos = [], []
        answers_pos = []
        for sent in nlp_context.sents:
            sents.append(sent.text)
            sents_pos.append([sent.start_char, sent.end_char])
            sent_ans_pos = []
            if len(sent) < self.min_anssent_token_num:
                answers_pos.append(sent_ans_pos)
            else:
                for ent in list(sent.ents):
                    if context[ent.start_char:ent.end_char] == ent.text:
                        if ent.label_ not in self.ans_ent_type_exclude_list:
                            sent_ans_pos.append([ent.start_char, ent.end_char])
                answers_pos.append(sent_ans_pos)
        return sents, sents_pos, answers_pos

    def _prepare_inputs_for_qg_from_answers_hl(self, context, sents, sents_pos, answers_pos):
        inputs = []
        for i, answer_pos in enumerate(answers_pos):
            if len(answer_pos) == 0:
                continue
            for pos_tuple in answer_pos:
                sents_copy = sents[:]
                sent = sents_copy[i]
                answer_check = context[pos_tuple[0]:pos_tuple[1]]
                ans_start_idx = pos_tuple[0] - sents_pos[i][0]
                ans_end_idx = pos_tuple[1] - sents_pos[i][0]
                answer_text = sent[ans_start_idx:ans_end_idx]
                assert answer_text == answer_check
                try:
                    sent = f"{sent[:ans_start_idx]} <hl> {answer_text} <hl> {sent[ans_end_idx:]}"
                    sents_copy[i] = sent
                    source_text = " ".join(sents_copy)
                    source_text = f"generate question: {source_text}"
                    source_text = source_text + " </s>"
                    inputs.append({"answer": answer_text, "answer_pos": pos_tuple, "answer-sent_pos": sents_pos[i], "source_text": source_text})
                except:
                    continue
        return inputs

    def _tokenize(self, inputs):
        inputs = self.tokenizer(inputs, max_length=512, padding=True, truncation=True, return_tensors="pt")
        return inputs

    def _generate_questions(self, inputs):
        with torch.cuda.amp.autocast():
            inputs = self._tokenize(inputs)
            outs = self.model.generate(
                input_ids=inputs['input_ids'].to(self.device),
                attention_mask=inputs['attention_mask'].to(self.device),
                max_length=32,
                num_beams=4,
            ).cpu()
            questions = [self.tokenizer.decode(ids, skip_special_tokens=True) for ids in outs]
        return questions


# Parameters
qg_model_name = "valhalla/t5-base-qg-hl"
min_para_token_num = 30
min_anssent_token_num = 10
qg_model = QGPipeline(qg_model_name, min_para_token_num, min_anssent_token_num, ans_ent_type_exclude_list=[])

# Input and output directories (replace these with configuration or environment variables)
input_dir = "path_to_input_directory"
output_dir = "path_to_output_directory"

try:
    for filename in os.listdir(input_dir):
        question_file_list = os.listdir(output_dir)
        if 'In_Processing.json' in question_file_list:
            question_file_list.remove('In_Processing.json')
        if 'ERRORS.txt' in question_file_list:
            question_file_list.remove('ERRORS.txt')
        if filename in question_file_list:
            continue

        with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as file_obj:
            data = json.load(file_obj)
        question_json = []

        processed_file_path = os.path.join(output_dir, 'In_Processing.json')
        if not os.path.exists(processed_file_path):
            with open(processed_file_path, mode='w', encoding='utf-8') as f:
                json.dump(question_json, f)

        with open(processed_file_path, mode='r', encoding='utf-8') as f:
            question_json = json.load(f)

        for para_id, item in enumerate(data):
            try:
                if para_id < len(question_json):
                    continue
                generated_questions = []
                para_id = item['para_id']
                para = item["paragraphs"]
                results = qg_model(para)
                print(f'{para_id}: SUCCESSFUL')
                generated_questions.append(results)
                item_data = item.copy()
                item_data.update({"questions": generated_questions})
                question_json.append(item_data)

                with open(processed_file_path, mode='w', encoding='utf-8') as f:
                    json.dump(question_json, f, indent=4)
            except Exception as e:
                if str(e).find('CUDA out of memory') >= 0:
                    print(f'{para_id}: ERROR')
                    with open(os.path.join(output_dir, 'ERRORS.txt'), mode='a') as f:
                        f.write(str(para_id) + '\n')
                else:
                    print(f'Error: {e}')
                    exit(0)
        os.rename(processed_file_path, os.path.join(output_dir, filename))

except Exception as e:
    print(f"Error during processing: {e}")
