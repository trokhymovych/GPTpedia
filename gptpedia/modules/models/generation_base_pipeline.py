import logging

from typing import Any

from langchain import HuggingFacePipeline, LLMChain, PromptTemplate
from transformers import pipeline


logger = logging.getLogger(__name__)


class GenerationPipelineBase:
    def __init__(self, logger_object: logging.Logger = logger, **kwargs: Any) -> None:
        self.logger = logger_object
        self.logger.info("Begin initialization")

        model_name = kwargs.get("model_name", "databricks/dolly-v2-3b")
        generate_text = pipeline(
            model=model_name, trust_remote_code=True, device_map="auto", return_full_text=True
        )
        # template for an instruction with input
        prompt_with_context = PromptTemplate(
            input_variables=["instruction", "context"],
            template="Answer the question delimited by <> <{instruction}>\n\n"
                     "Take into account context delimited by ^:\n^{context}^")

        hf_pipeline = HuggingFacePipeline(pipeline=generate_text)
        self.llm_context_chain = LLMChain(llm=hf_pipeline, prompt=prompt_with_context)

        self.logger.info("Initialization completed")

    def generate_answer(self, question: str, context: str) -> str:
        """
        Method that implements question answering pipeline using langchain
        """
        generation_result = self.llm_context_chain.predict(
            instruction=question,
            context=context
        ).lstrip()
        return generation_result
