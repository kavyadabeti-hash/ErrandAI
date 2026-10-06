# ErrandAI

ErrandAI is a small Streamlit app that turns a list of errands into a practical plan using a model served through the NVIDIA API.

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Set your environment variables in a `.env` file:
   `NVIDIA_API_KEY=...`
   `NVIDIA_MODEL=google/diffusiongemma-26b-a4b-it`
4. Start the app:
   `streamlit run app.py`

The app validates the entered errands and shows a clear error if the API configuration is missing or the configured model is a safety-only model that cannot generate plans.
