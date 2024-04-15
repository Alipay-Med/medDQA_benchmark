import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
import sys
from llava.model.builder import load_pretrained_model
from llava.mm_utils import get_model_name_from_path
from llava.eval.run_llava import eval_model
import requests
from llava.eval.run_llava import eval_model_no_load
import json
import argparse


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
    model_path = '/mntnlp/common_base_model/liuhaotian__llava-v1.5-7b'

    tokenizer, model, image_processor, context_len = load_pretrained_model(
        model_path=model_path,
        model_base=None,
        model_name=get_model_name_from_path(model_path),
    )

    data = open_json(path)
    answer_list = []
    for item in data:
        temp_dict = {}
        print(item['answer'])
        if use_context:
            context = item['context']
        else:
            context = ''     
        prompt_qs = item['question']
        image_file = item['url']
        args = type('Args', (), {
                "model_path": model_path,
                "model_base": None,
                "model_name": get_model_name_from_path(model_path),
                "query": prompt+context+prompt_qs,
                "conv_mode": None,
                "image_file": image_file,
                "sep": ",",
                "temperature": 0,
                "top_p": None,
                "num_beams": 1,
                "max_new_tokens": 512,
                "model": model,
                "tokenizer": tokenizer,
                "image_processor": image_processor,
                "context_len": context_len,
                })()
        try:
            answer = eval_model_no_load(args)
        except Exception as e:
            answer = 'ERROR'
        for k, v in item.items():
            temp_dict[k] = v
        temp_dict['pred_answer'] = answer
        answer_list.append(temp_dict)
        
        with open(writer_path, 'a+', encoding='utf-8') as file:
            line = json.dumps(temp_dict, ensure_ascii=False) + '\n'
            file.write(line)
            

