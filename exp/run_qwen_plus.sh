pip install tiktoken
pip install transformers_stream_generator
pip install icecream


# create dir
root_path=/exp/result/

save_version_name=zero_shot_final

mkdir $root_path$save_version_name
mkdir $root_path$save_version_name/entity_vqa/
mkdir $root_path$save_version_name/table_vqa/
mkdir $root_path$save_version_name/clinical_reasoning_vqa/
prompt=""

echo $prompt
root_fact_path=$root_path$save_version_name/entity_vqa/
root_table_path=$root_path$save_version_name/table_vqa/
root_table_reason_path=$root_path$save_version_name/clinical_reasoning_vqa/

run_path=`dirname $0`$"/"


# json path
entity_vqa_json_path=/exp/result/dataset/entity_qa.json
table_vqa_json_path=/exp/result/dataset/table_qa.json
clinical_reasoning_vqa_json_path=/exp/result/dataset/reasoning_qa.json


#######################################################################
# run qwen-vl-plus
model_name=qwen_vl_plus


# writer path
entity_vqa_write_path=$root_fact_path$"answer_"$model_name$".json"
echo $entity_vqa_write_path
table_vqa_write_path=$root_table_path$"answer_"$model_name$".json"
echo $table_vqa_write_path
clinical_reasoning_vqa_write_path=$root_table_reason_path$"answer_"$model_name$".json"
echo $clinical_reasoning_vqa_write_path

# run python 
echo $run_path$"infer_"$model_name$".py"
nohup python $run_path$"infer_"$model_name$".py" --jsonPath $entity_vqa_json_path --writerPath $entity_vqa_write_path --prompt "$prompt" &
nohup python $run_path$"infer_"$model_name$".py" --jsonPath $table_vqa_json_path --writerPath $table_vqa_write_path --prompt "$prompt" &
nohup python $run_path$"infer_"$model_name$".py" --jsonPath $clinical_reasoning_vqa_json_path --writerPath $clinical_reasoning_vqa_write_path --prompt "$prompt"





