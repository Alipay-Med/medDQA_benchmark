from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import requests
import json
import html
import time
import ast

# Constants
IV = "1234567890123456"
AES_KEY = ""
API_URL = ''
HEADERS = {'Content-Type': 'application/json'}
MODEL = "gpt-4" # gpt-4v
API_KEY = ""
SERVICE_NAME_ASYNC = '' 
SERVICE_NAME_CHATGPT = "" 
VISIT_DOMAIN = ""
VISIT_BIZ = ""
VISIT_BIZ_LINE = ""
CACHE_INTERVAL = -1

def aes_encrypt(data, key):
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, IV.encode('utf-8'))
    block_size = AES.block_size
    padding_length = (block_size - len(data) % block_size) % block_size
    data = data.encode('utf-8') + b'\0' * padding_length
    encrypted = cipher.encrypt(data)
    return b2a_hex(encrypted).decode('utf-8')


def aes_decrypt(data, key):
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, IV.encode('utf-8'))
    decrypted = cipher.decrypt(a2b_hex(data))
    return decrypted.rstrip(b'\0')


def get_first_query(message_key, text):
    return {
        "model": MODEL,
        "messageKey": message_key,
        "outputType": "pull",
        "n": 1,
        "messages": [{"role": "user", "content": text}],
        "api_key": API_KEY
    }


def get_second_query(message_key):
    return {"messageKey": message_key}


def get_post_data(service_name, query_conditions):
    param = {
        "serviceName": service_name,
        "visitDomain": VISIT_DOMAIN,
        "visitBiz": VISIT_BIZ,
        "visitBizLine": VISIT_BIZ_LINE,
        "cacheInterval": CACHE_INTERVAL,
        "queryConditions": query_conditions
    }
    encrypted_param = aes_encrypt(json.dumps(param), AES_KEY)
    return {"encryptedParam": encrypted_param}


def make_post_request(post_data):
    response = requests.post(API_URL, json=post_data, headers=HEADERS)
    return response.json()


def all_first_post(message_key, text, data):
    first_query = get_first_query(message_key, text + data['question'])
    post_data = get_post_data(SERVICE_NAME_ASYNC, first_query)
    response_data = make_post_request(post_data)
    x = response_data["data"]["values"]["data"]
    ast_str = ast.literal_eval("'" + x + "'")
    js = ast_str.replace('&quot;', '"')
    js = js.replace("&#39;", "'")
    content = json.loads(js)["message"]
    return content, response_data


def all_second_post(message_key):
    second_query = get_second_query(message_key)
    post_data = get_post_data(SERVICE_NAME_CHATGPT, second_query)
    response_data = make_post_request(post_data)
    success = response_data['success']
    if success:
        value = response_data["data"]["values"]
        if value:
            x = value["response"]
            ast_str = ast.literal_eval("'" + x + "'")
            js = ast_str.replace('&quot;', '"')
            js = js.replace("&#39;", "'")
            data = json.loads(js)
            if 'errorMsg' in data:
                content = data['errorMsg']
            else:
                content = html.unescape(data['choices'][0]['message']['content'])
        else:
            content = 'INCOMPLETE'
    else:
        content = 'ERROR'
    return content, response_data


def open_json(path):
    with open(path, 'r', encoding='utf-8') as file:
        data_list = [json.loads(line) for line in file]
        return data_list


def append_to_json_file(writer_path, data):
    with open(writer_path, 'a', encoding='utf-8') as file:
        line = json.dumps(data, ensure_ascii=False) + '\n'
        file.write(line)


def post_write_path(messageKey, data_path, output_path, prompt,retry):
    retry_list = []
    http_error = []
    data_list = open_json(data_path)
    if retry:
        train_list = retry
    else:
        train_list = range(len(data_list))
    cnt = 0
    
    for idx in train_list:
        data = data_list[idx]
        try:
            prompt_with_context = f"{prompt} {data['question']}"
            first_content, _ = all_first_post(messageKey + str(idx), prompt_with_context, data)
        except Exception as e:
            retry_list.append(idx)
            first_content = "ERROR"

        cnt += 1
        if cnt >= 10:
            time.sleep(10)
            cnt = 0

    print("\nPlease wait 100s")
    time.sleep(100)

    for idx in train_list:
        data = data_list[idx]
        try:
            content, _ = all_second_post(messageKey + str(idx))
        except Exception as e:
            content = "ERROR"
            retry_list.append(idx) if idx not in retry_list else None

        if content == "Internet error":
            retry_list.append(idx)
        elif content.startswith("HTTP error"):
            http_error.append(idx)
        else:
            pred_answer = content
            temp_dic = {}
            for k, v in data.items():
                temp_dic[k] = v
            temp_dic['pred_answer'] = pred_answer
            append_to_json_file(output_path, temp_dic)

    return retry_list, http_error


if __name__ == "__main__":
    from datetime import datetime

    now = datetime.now()
    messageKey = ''+str(now)
    prompt=''
    data_path = '/exp/result/esra_fact.json'
    output_path = '/exp/result/esra_fact_output.json'
    retry_list, http_error = post_write_path(messageKey, data_path, output_path, prompt=prompt,retry=None)
    retry_list, http_error
