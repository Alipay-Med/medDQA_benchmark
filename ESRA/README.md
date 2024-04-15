# Efficient Structural Restoration Annotation (ESRA)
We propose an efficient structure-aware labeling method to reconstruct both textual and tabular content in medical reports. It significantly reduces the human labeling errors and improves the efficiency of annotation process. Statistically, this method has elevated the accuracy rate from 70\% to 96.8\%.

<p align="center">
  <img src="pics/ESRA.png" width="90%">
</p>

## How to use?
This system supports the integration of custom models for image processing and OCR. You can apply your own APIs for the following optional and required models:
- Small angle detection model (optional)
- Large direction detection model (optional)
- Table angle detection model (optional)
- OCR model (required)

Modifying `detector.py`
To adapt the `detector.py` script to your specific needs, follow these steps:
- API Integration: Implement the connection to your custom APIs within the detector.py. Replace the placeholders with the necessary API call logic to ensure the models are correctly engaged during the detection and recognition processes.
- Configuration: Set the model parameters and API keys (if applicable) as required to connect to your services.
- Handling Responses: Adequately parse the responses from your APIs to be compatible with the rest of the detector.py processing pipeline, ensuring that the output is in the expected formats for post-processing and analysis.

Once `detector.py` is configured, run `run.py` to get the ESRA result of an image
