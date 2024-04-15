# Efficient Structural Restoration Annotation (ESRA)
We propose an efficient structure-aware labeling method to reconstruct both textual and tabular content in medical reports. It significantly reduces the human labeling errors and improves the efficiency of annotation process. 

<p align="center">
  <img src="../pics/ESRA.png" width="90%">
</p>

## How to use?
This system supports the integration of custom models for image processing and OCR. You can apply your own APIs in `detector.py` for the following optional and required models:
- Small angle detection model (optional)
- Large direction detection model (optional)
- Table angle detection model (optional)
- OCR model (required)

Once `detector.py` is configured, run `run.py` to get the ESRA result of an image
