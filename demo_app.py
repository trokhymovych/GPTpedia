import time

import streamlit as st
import streamlit.components.v1 as components

from gptpedia.modules.models.context_search import ContextPipeline
from gptpedia.modules.models.generation_base_pipeline import GenerationPipelineBase


@st.cache_data
def load_context_searcher():
    return ContextPipeline()

@st.cache_data
def load_generator():
    return GenerationPipelineBase()

def generate_text(question: str, context: str):
    with st.spinner("Searching for context in Wikipedia (takes approx. 30 seconds..."):
        if context == "Yes":
            context = context_search_pipeline.generate_contex(question)
        else:
            context = ""

    with st.spinner("Generating answer..."):
        st.session_state.text = generation_pipeline.generate_answer(question=question, context=context)
        return
    return

generation_pipeline = load_generator()
context_search_pipeline = load_context_searcher()

# Configure Streamlit page and state
st.set_page_config(page_title="GPTpedia", page_icon="🕸")

if "text" not in st.session_state:
    st.session_state.text = ""
if "text_error" not in st.session_state:
    st.session_state.text_error = ""
if "n_requests" not in st.session_state:
    st.session_state.n_requests = 0

st.title("Wikipedia Q&A pipeline")
st.markdown(
    "This is a mini demo app based on [databricks/dolly-v2-3b](https://huggingface.co/databricks/dolly-v2-3b) "
    "for question answering based on Wikipedia"
)

topic = st.text_input(label="Question", placeholder="What is the shape of Earth?")
wiki_context_bool = st.radio('Do you want to look for context in Wikipedia?', ['Yes', 'No'])

if st.button(label="Generate text"):
    generate_text()
    print(topic, wiki_context_bool)
    print(st.session_state.text)

    st.markdown("""---""")
    st.text_area(label="Generated answer", value=st.session_state.text, height=100)