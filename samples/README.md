## Dataset Files

1. **sampled_image_content_kv_table_annotation.csv**
   - Contains high-quality annotations extracted from medical image content.
   - `kv`: Key-Value Pairs: This is a structured dict storing critical information extracted from images, such as patient age, examination date, and pre-examination clinical diagnosis findings.
   - `table`: List of Quadruplets and each quadruplet includes `item`, `result`, `range`, and `is_abnormal` flag, reflecting the structure of a laboratory report in the order they appear.
   - `report_type`: Laboratory Reports and a further classification of Clinical Reports (CT, MRI, Ultrasound, etc.)
   - `image_type`: The image type could be pdf, photo or screenshot
   - `image_quality`: The image quality could be high or low

2. **sampled_image_content_vqa.json**
   - This file includes VQAs based on image content recognition tasks.
   - `task`: `entity_qa`, `table_qa` or `table_nr_qa`
   - `answer_type`: `single` or `multi`
   **Customized Image Content VQA**
   Note you can also generate your own image content VQA datasets
   ```shell
   python qa_generation/image_content_qa_generation.py sampled_image_content_kv_table_annotation.csv new_image_content_vqa.json
   ```

3. **sampled_clinical_reasoning_vqa.json**
   - This file includes VQAs based on clinical reasoning tasks.
   - `task`: `disease_qa`, `status_qa` or `advice_qa`
   - `answer_type`: `MC` (Multiple Choice) or `SA` (Single Answer)
   - `context`: Each question is supported by a piece of medical knowledge that is essential for deducing the correct answer.

4. **sampled_context_base.csv**
   - A collection of contexts
   - Provides essential medical background knowledge geared towards supporting clinical reasoning tasks within the domains of urology and general laboratory diagnostics.
   - Contains three main components for each piece of context:
     - `title`: Indicates the specific name or label of a disease, examination finding, or health-related topic.
     - `context_type`: It refers to the type of a context. For example, "Disease-Advice" offers advice for controlling or alleviating a health issue, and "Disease-Treatment" provides specifics on the method to addressing a medical disease.
     - `description`: It offers detailed medical knowledge to arrive at the conclusion mentioned in the title, such as the criteria for diagnosing "Mild Anemia".


