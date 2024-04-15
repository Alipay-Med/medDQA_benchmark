## Dataset Files

1. **sampled_image_content_kv_table_annotation.csv**
   - Contains key-value pair annotations extracted from medical image content.
   - `kv`: Key-Value Pairs: This is a structured dict storing critical information extracted from images, such as patient age, examination date, and pre-examination clinical diagnosis findings.
   - `table`: List of Quadruplets and each quadruplet includes `item`, `result`, `range`, and `is_abnormal` flag, reflecting the structure of a laboratory report in the order they appear.
   - `report_type`: Laboratory Reports and a further classification of Clinical Reports (CT, MRI, Ultrasound, etc.)
   - `image_type`: The image type could be pdf, photo or screenshot
   - `image_quality`: The image quality could be high or low

2. **sampled_image_content_vqa.json**
   - This file includes VQAs based on image content recognition tasks.
   - `task` include:
     - `table_qa`: Questions pertaining to tables present in medical reports.
     - `entity_qa`: Questions focused on entities identified within the images or accompanying data.
     - `table_nr_qa`: Questions about numerical results in the tables.
   - `answer_type`: Indicate the type of answers expected, either:
     - `single` 
     - `multi`
### Customized Image Content VQA 
Note you can also generate you own image content VQA datasets by using:
```shell
python qa_generation/image_content_qa_generation.py sampled_image_content_kv_table_annotation.csv new_image_content_vqa.json

3. **sampled_clinical_reasoning_vqa.json**
   - This file includes VQAs based on clinical reasoning tasks.
   - `task` include:
     - `disease_qa`: Questions related to the identification or characteristics of diseases.
     - `status_qa`: Questions inquiring about the progression of a disease.
     - `advice_qa`: Questions seeking recommendations for health-related actions or treatments.
   - `answer_type`:
     - `MC` (Multiple Choice): Questions that provide a set of options from which the correct answer(s) should be chosen.
     - `SA` (Single Answer): Questions that require a single, specific answer.
   - `context`: Each question is supported by a piece of medical knowledge that is essential for deducing the correct answer.

4. **sampled_context_base.csv**
   - A collection of contexts
   - Provides essential medical background knowledge geared towards supporting clinical reasoning tasks within the domains of urology and general laboratory diagnostics.
   - Contains four main components for each piece of context:
     - `report_type`: Denotes whether it is a laboratory or clinical report.
     - `title`: Indicates the specific name or label of a disease, examination finding, or health-related topic.
     - `context_type`: Specifies the category a context falls into (e.g., "Disease-Advice" or "Disease-Treatment").
     - `description`: Delivers detailed medical information necessary to understand the context provided in the title.


