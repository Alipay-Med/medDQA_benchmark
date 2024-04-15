import os
os.environ['CUDA_VISIBLE_DEVICES'] = '1'
import argparse
import torch
from PIL import Image
from transformers import TextStreamer
import sys
import requests
import json
from mplug_owl2.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN
from mplug_owl2.conversation import conv_templates, SeparatorStyle
from mplug_owl2.model.builder import load_pretrained_model
from mplug_owl2.mm_utils import process_images, tokenizer_image_token, get_model_name_from_path, KeywordsStoppingCriteria


def get_answer(model, tokenizer, pic_url, question, context):
    query = context + question
    conv = conv_templates["mplug_owl2"].copy()
    roles = conv.roles
    
    image = Image.open(requests.get(pic_url, stream=True).raw).convert("RGB")
    
    max_edge = max(image.size) # We recommand you to resize to squared image for BEST performance.
    image = image.resize((max_edge, max_edge))

    image_tensor = process_images([image], image_processor)
    image_tensor = image_tensor.to(model.device, dtype=torch.float16)
    
    inp = DEFAULT_IMAGE_TOKEN + query
    conv.append_message(conv.roles[0], inp)
    conv.append_message(conv.roles[1], None)
    prompt = conv.get_prompt()

    input_ids = tokenizer_image_token(prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors='pt').unsqueeze(0).to(model.device)
    stop_str = conv.sep2
    keywords = [stop_str]
    stopping_criteria = KeywordsStoppingCriteria(keywords, tokenizer, input_ids)
    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    
    temperature = 0.7
    max_new_tokens = 512

    with torch.inference_mode():
        output_ids = model.generate(
            input_ids,
            images=image_tensor,
            do_sample=True,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            streamer=streamer,
            use_cache=True,
            stopping_criteria=[stopping_criteria])
    
    outputs = tokenizer.decode(output_ids[0, input_ids.shape[1]:]).strip()
    return outputs

def open_json(path):
    with open(path, 'r') as file:
        data_list = [json.loads(line) for line in file]
    return data_list


if __name__=='__main__':
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
    model_name = get_model_name_from_path(model_path)
    tokenizer, model, image_processor, context_len = load_pretrained_model(model_path, None, model_name, load_8bit=False, load_4bit=False, device="cuda")
    data = open_json(path)
    answer_list = []
    for item in data:
        temp_dict = {}
        print(item['answer'])
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
            