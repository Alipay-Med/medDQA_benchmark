from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import requests
import json
import argparse
import ast

def aes_encrypt(data, key):
    """
    Encrypt the data using AES in CBC mode.

    Parameters:
    data (str): The plaintext data to encrypt. It will be padded to a multiple of 16 bytes if necessary.
    key (str): The encryption key to use.

    Returns:
    str: The encrypted data represented as a hexadecimal string.
    """

    # Initialization vector for CBC mode
    iv = "1234567890123456"

    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    pad = lambda s: s + (AES.block_size - len(s) % AES.block_size) * chr(0)
    padded_data = pad(data).encode('utf-8')
    encrypted_data = cipher.encrypt(padded_data)

    return b2a_hex(encrypted_data).decode('utf-8')

def aes_decrypt(encrypted_data, key):
    """
    Decrypt the data previously encrypted with AES in CBC mode.

    Parameters:
    encrypted_data (str): The encrypted data represented as a hexadecimal string.
    key (str): The decryption key to use.

    Returns:
    bytes: The decrypted plaintext data, with padding removed.
    """

    # Initialization vector for CBC mode
    iv = '1234567890123456'

    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    encrypted_data_bytes = a2b_hex(encrypted_data)
    decrypted_data = cipher.decrypt(encrypted_data_bytes)
    return decrypted_data.rstrip(b'\0')


def get_post_data(image_url, question):
    param_qw = {
        "serviceName":"",
        "visitDomain":"",
        "visitBiz":"",
        "visitBizLine":"",
        "cacheInterval":"-1",
        "queryConditions":{
            "model":"qwen-vl-plus",
            "messages":[
          		{
            		"role":"system","content":[{"text":"You are a helpful assistant."}]
          		},
              {
            		"role":"user","content":[
                  {
                    "image": image_url
                  },
                  {
                    "text": question
                  }
                ]
          		}
            ],
          	"top_p":"0.9"
        }
    }
    
    data = json.dumps(param_qw)
    key = ""  # use your own api key
    str = aes_encrypt(data, key)
    post_data = {
        "encryptedParam": str
    }
    return post_data

def get_response(post_data):
    url = ''
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, data=json.dumps(post_data), headers=headers)
    x = response.json()["data"]["values"]["data"]
    ast_str = ast.literal_eval("'" + x + "'")

    js = ast_str.replace('&quot;', '"').replace("&#39;", "'")
    
    data = json.loads(js)
    content = data['output']['choices'][0]['message']['content'][0]['text']
    return content

def open_json(path):
    with open(path, 'r') as file:
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

    data = open_json(path)
    error_list = []
    for idx, item in enumerate(data):
        if use_context:
            context = item['context']
        else:
            context = ''
        temp_dict = {}
        print(f"question:{item['question']}\nanswer:{item['answer']}")
        post_data = get_post_data(item['url'], prompt+context+item['question'])
        try:
            answer = get_response(post_data)
        except Exception as e:
            answer = 'ERROR'
            error_list.append(idx)
        print(f"pred_answer:{answer}\n")
        for k, v in item.items():
            temp_dict[k] = v
        temp_dict['pred_answer'] = answer
        with open(writer_path, 'a+', encoding='utf-8') as file:
            line = json.dumps(temp_dict, ensure_ascii=False) + '\n'
            file.write(line)