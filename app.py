import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEFAULT_MODEL = "google/diffusiongemma-26b-a4b-it"
SAFETY_ONLY_MODELS = {
    "nvidia/llama-3.1-nemotron-safety-guard-8b-v3",
    "nvidia/llama-3.1-nemoguard-8b-content-safety",
    "nvidia/llama-3.1-nemoguard-8b-topic-control",
    "meta/llama-guard-4-12b",
}


def get_model_settings():
    api_key = os.getenv("NVIDIA_API_KEY")
    model = os.getenv("NVIDIA_MODEL") or DEFAULT_MODEL
    if model in SAFETY_ONLY_MODELS:
        return api_key, DEFAULT_MODEL
    return api_key, model


st.set_page_config(page_title="ErrandAI", page_icon="E", layout="centered")

st.title("ErrandAI")
st.caption("Turn a messy list of errands into a practical daily route.")

with st.sidebar:
    st.header("Quick setup")
    st.write("Add these values to your .env file before generating a plan:")
    st.code(f"NVIDIA_API_KEY=your_key\nNVIDIA_MODEL={DEFAULT_MODEL}")
    st.markdown("Examples")
    st.code(
        "I need to go to the bank, pick up a parcel, and buy groceries before 6pm.\n"
        "I have a dentist appointment at 2pm and need to drop off a package on the way home."
    )


api_key, model = get_model_settings()

sample_errands = [
    "I need to go to the bank, collect my parcel, and buy groceries before 6pm.",
    "I have a dentist appointment at 2pm and need to drop off a package on the way home.",
    "I need to return a library book, buy lunch ingredients, and visit the pharmacy before 5pm.",
]


if "user_input" not in st.session_state:
    st.session_state.user_input = ""


st.write("Enter your errands below and let ErrandAI sort them into a realistic order.")

for index, sample in enumerate(sample_errands):
    if st.button(f"Use example: {sample[:38]}...", key=f"sample_{index}"):
        st.session_state.user_input = sample

user_input = st.text_area(
    "Enter your errands",
    value=st.session_state.user_input,
    placeholder="I need to go to the bank, collect my parcel, buy groceries...",
    height=180,
)

col1, col2 = st.columns([1, 1])
with col1:
    create_plan_clicked = st.button("Create Plan", type="primary")
with col2:
    clear_clicked = st.button("Clear")

if clear_clicked:
    st.session_state.user_input = ""
    st.rerun()

if create_plan_clicked:
    cleaned_input = user_input.strip()
    st.session_state.user_input = cleaned_input

    if not cleaned_input:
        st.warning("Please enter your errands before creating a plan.")
    elif not api_key:
        st.error("Set NVIDIA_API_KEY in your .env file before creating a plan.")
    elif not model:
        st.error("Set NVIDIA_MODEL in your .env file before creating a plan.")
    else:
        try:
            client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=api_key,
            )
            with st.spinner("Creating your plan..."):
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are ErrandAI, an intelligent daily errand planner. "
                                "Organize the user's errands into a practical, efficient order. "
                                "Consider deadlines, priorities, locations, dependencies, and travel time when provided. "
                                "Do not invent details that the user has not supplied. "
                                "Answer in clear, easy-to-follow steps with a short rationale for the order."
                            ),
                        },
                        {"role": "user", "content": cleaned_input},
                    ],
                    temperature=0.2,
                    max_tokens=1000,
                )
            answer = response.choices[0].message.content
            if isinstance(answer, dict):
                st.error("The configured NVIDIA model is a safety-only model and cannot generate plans. Please use a supported chat model.")
            elif answer:
                st.subheader("Your Recommended Plan")
                st.markdown(answer)
                st.caption("This plan is based only on the details you supplied.")
            else:
                st.error("The service returned an empty plan. Please try again.")
        except Exception as exc:
            error_text = str(exc).lower()
            if "not found" in error_text or "gone" in error_text or "410" in error_text:
                st.error(
                    "The configured NVIDIA model is unavailable or retired. Set NVIDIA_MODEL to a supported chat model (for example: google/diffusiongemma-26b-a4b-it)."
                )
            else:
                st.error(
                    "Could not create a plan. Check the NVIDIA model, API key, and connection, then try again."
                )
