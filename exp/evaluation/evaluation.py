import json
import pandas as pd
import numpy as np
from rouge import Rouge

rouge = Rouge()  # Initialize the Rouge scoring object once to avoid re-initialization overhead.

punctuation_mapping = {
    '，': ',', '。': '.', '！': '!', '？': '?', '：': ':', '；': ';',
    '“': '"', '”': '"', '‘': "'", '’': "'", '（': '(', '）': ')',
    '【': '[', '】': ']', '～': '-', '~': '-', '—': '-', '…': '...',
}


def replace_chinese_punctuation(text):
    for chinese_punc, english_punc in punctuation_mapping.items():
        text = text.replace(chinese_punc, english_punc)
    return text

def preprocess_data(df):
    df['answer_clean'] = df['answer'].apply(replace_chinese_punctuation)
    df['pred_clean'] = df['pred_answer'].apply(replace_chinese_punctuation)
    return df

def calculate_rouge_l(row):
    scores = rouge.get_scores(row['pred_clean'], row['answer_clean'])
    return scores[0]['rouge-l']['f']

def calculate_acc(row):
    task, answer_type = row['task'], row.get('answer_type', '')
    answer_clean, pred_clean = row['answer_clean'], row['pred_clean']
    
    # Image content recognition vqa
    if 'fact' in task or 'table' in task:
        if 'single' in answer_type:
            return float(answer_clean in pred_clean)
        elif 'multi' in answer_type and 'nr' not in task: #table qa
            segments = answer_clean.split(';')
            score = 0.0
            score += 0.5 if segments[0] in pred_clean else 0
            score += 0.5 if len(segments) > 1 and segments[1] in pred_clean else 0
            return score
        else: #table nr qa
            if '无异常结果' in answer_clean:
                return float('无' in pred_clean and '无法判断' not in pred_clean)
            else:
                segments = answer_clean.split(';')
                return sum(1 for segment in segments if segment in pred_clean) / len(segments)
    # Clinical reasoning vqa
    else:  
        # Multiple Choice
        if 'MC' in answer_type:
            if len(pred_clean.replace(';;', '').split(';')) > 2:
                return 0
            return float(answer_clean in pred_clean)
        # Short Answer
        else:  
            return float(answer_clean in pred_clean)

def evaluate_models(tasks, models):
    results = []
    for task in tasks:
        for model in models:
            filepath = f'{task}/answer_{model}.json'
            with open(filepath, 'r', encoding='utf-8') as file:
                data = [json.loads(line.strip()) for line in file]
            df = preprocess_data(pd.DataFrame(data))
            df['task'] = task
            df['rouge_l'] = df.apply(calculate_rouge_l, axis=1)
            df['acc'] = df.apply(calculate_acc, axis=1)
            results.append(df)
    return pd.concat(results, ignore_index=True)

if __name__ == '__main__':
    tasks = ['tablereasonvqa']
    models = ['gpt4v', 'llava', 'mPLUGowl', 'qwen_vl_chat', 'qwen_vl_plus']
    df = evaluate_models(tasks, models)
    # Multi-level Evaluation
    res = df.groupby(['TASK', 'model']).agg({
        'rouge_l': 'mean',
        'acc': 'mean',
        'question': 'count'
    }).rename(columns={'question': 'count'}).round(2)
    print(res)
