import pandas as pd
import numpy as np
import random
import json
import argparse

# Define the function to generate the VQA data
def generate_image_content_vqa(source_path, dest_path):
    df = pd.read_csv(source_path)
    df['is_table'] = np.where(df['report_type'] == 'Laboratory', 1, 0)
    data = []
    for i, row in df.iterrows():
        img = row['img_path']
        img_type = row['image_type']
        img_quality = row['image_quality']
        kv = eval(row['kv']) if pd.notnull(row['kv']) and row['kv'] else None
        
        # ENTITY QA GENERATION
        if pd.notnull(kv):
            task='fact_qa'
            for k,v in kv.items():
                q1 = random.choice([f'{k}是什么？', f'{k}是？', f'图片里的{k}是什么？',f'该报告中{k}对应的文字是什么？'])
                a1 = f'{v}' if v != '' else '无'
                data.append((img, q1, a1, len(a1),task, 'single_entity', img_type, row['is_table'],img_quality))
            if len(list(kv.keys()))>1:
                for i in range(5):
                    k1,k2 = random.sample(list(kv.keys()), 2)
                    q2=f'{k1}和{k2}对应的文字是什么？'
                    v1 = '无' if kv[k1] == '' else kv[k1]
                    v2 = '无' if kv[k2] == '' else kv[k2]
                    a2 = f'{v1};{v2}'
                    data.append((img, q2, a2, len(a2),task, 'multi_entity', img_type, row['is_table'],img_quality))
                    
        # TABLE QA GENERATION
        if row['is_table'] == 1:
            task='table_qa'
            items=eval(row['table'])
            abnormals=[t[0] for t in items if "否" in t[3]]
            for item,result,refer,infer in items:
                #TABLE QA GENERATION 
                txt_name=random.choice(["该检测指标的", "的", "该指标的", "这个检测项目的", '该指标的'])
                txt_result=random.choice(["检测结果", "结果", "检查结果"])
                txt_range=random.choice(["参考值", "参考范围", '参考区间', '正常值', '正常范围', "正常区间"]) 
                txt_ask=random.choice(["是什么?", "是多少?"]) 
                # result
                q4 = f'{item}{txt_name}{txt_result}{txt_ask}'
                a4 = f'{result}' if result != '无' else '无'
                data.append((img, q4, a4, len(a4),task, 'single_span', img_type, row['is_table'],img_quality))
                q5 = f'{item}{txt_name}{txt_range}{txt_ask}'
                a5 = f'{refer}' if refer != '无' else '无'
                data.append((img, q5, a5, len(a5),task, 'single_span', img_type, row['is_table'],img_quality))
                # result and reference
                txt_q = txt_name+txt_result + random.choice(['和', ',']) + txt_range + random.choice(['分别', '']) + txt_ask
                q6 = random.choice([f'{item}{txt_q}'])
                a6=f'{result}' if result != '无' else '无' 
                a6+=f';{refer}' if refer != '无' else ';无'
                data.append((img, q6, a6, len(a6),task, 'multi_span', img_type, row['is_table'],img_quality))
                #TABLE NR QA GENERTAION
                abnormal_ask=random.choice(["是否异常?"])
                q7=random.choice([f'{item}{txt_name}{txt_result}{abnormal_ask}'])
                if '是' in infer:
                    a7='正常'
                elif '否' in infer:
                    a7='异常' 
                else:
                    a7='无法判断'
                data.append((img, q7, a7, len(a7),'table_nr_qa', 'multi_span', img_type, row['is_table'],img_quality))
            q8=f'图片中有哪些检查项目的结果不在参考区间内？'
            a8 = '无异常结果' if abnormals == [] else ';'.join(abnormals)
            data.append((img, q8, a8, len(a8),'table_nr_qa', 'multi_span', img_type, row['is_table'],img_quality))
    final = pd.DataFrame(data, columns=['img_path', 'question', 'answer', 'answer_length', 'task', 'answer_type', 'image_type', 'is_table', 'image_quality'])
    final['idx'] = range(1, len(final) + 1)
    print(final['task'].value_counts())
    
    data = final[['img_path', 'question', 'answer', 'answer_length', 'task', 'answer_type', 'image_type', 'is_table', 'image_quality']].to_dict(orient='records')
    with open(dest_path, 'w') as jsonl_file:
        for entry in data:
            jsonl_file.write(json.dumps(entry, ensure_ascii=False) + '\n')
    print(f"Data has been saved to {dest_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate VQA Data")
    parser.add_argument("source_path", type=str, help="Path to the source CSV file")
    parser.add_argument("dest_path", type=str, help="Path to the destination JSONL file")
    args = parser.parse_args()
    source_path = args.source_path
    dest_path = args.dest_path
    
    try:
        generate_image_content_vqa(source_path, dest_path)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
    
