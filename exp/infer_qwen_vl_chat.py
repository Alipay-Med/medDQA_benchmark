import os
os.environ['CUDA_VISIBLE_DEVICES'] = '2'
import argparse
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig
import torch
import json

torch.manual_seed(1234)

def get_answer(model, tokenizer, image_url, question, context):
    query = tokenizer.from_list_format([
    {'image': image_url},
    {'text': context + question}
    ])
    response, history = model.chat(tokenizer, query=query, history=None)
    print(response)
    return response
    
def open_json(path):
    with open(path, 'r') as file:
        # for line in file:
        data_list = [json.loads(line) for line in file]
    return data_list

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--jsonPath', type=str, help='infer json path')
    parser.add_argument('--writerPath', type=str, help='save json path')
    parser.add_argument('--prompt', type=str, help='prompt')
    parser.add_argument('--use-context', action='store_true', help='use context or not')

    args = parser.parse_args()

    path = args.jsonPath
    writer_path = args.writerPath
    prompt = args.prompt
    use_context = args.use_context
    # load model
    model_path = ''
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(model_path, device_map="cuda", trust_remote_code=True).eval()

    data = open_json(path)
    answer_list = []
    for item in data:
        temp_dict = {}
        if use_context:
            context = item['context']
        else:
            context = ''

        try:
            answer = get_answer(model, tokenizer, item['url'], item['question'], prompt + context)
        except Exception as e:
            answer = 'ERROR'
        for k, v in item.items():
            temp_dict[k] = v
        temp_dict['pred_answer'] = answer
        answer_list.append(temp_dict)
        with open(writer_path, 'a+', encoding='utf-8') as file:
            line = json.dumps(temp_dict, ensure_ascii=False) + '\n'
            file.write(line)