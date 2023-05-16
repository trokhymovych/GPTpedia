# GPTpedia
The repository for developing Q&amp;A system based on Wikipedia and generative models.

## Pipelines available: 
### Pipeline 1: Raw Q&A pipeline
It implements the logic of extraction Wikipedia pages, parsing, selection of sections to analise and q&a model. 

Usage example: 
```python
from wikigpt.modules.models.qna_pipeline import QNAPipeline
qna_model = QNAPipeline()
question = "What is the shape of the Earth?"
answers = qna_model.question_answer(question)

print("Question: ",  question)
print("Answers: ", answers)
```
Result: 
```
Question: What is the shape of the Earth?
Answers:  [('spherical', 0.6795759797096252), ('circumference', 0.6381819248199463), 
('a plane or disk', 0.485660582780838), ('roughly spherical', 0.4851073920726776), ('geoid', 0.4751525819301605), 
('a sphere', 0.3425728678703308), ('convex', 0.32221758365631104), ('ellipsoid', 0.31942540407180786), 
('180 degrees of north-south curvature', 0.3023468554019928), ('spherical', 0.2844327986240387), 
('spherical', 0.16854353249073029), ('Earth undulates', 0.14663374423980713), ('slightly lumpy', 0.13553234934806824), 
('ellipsoid', 0.12807822227478027)]
```

### Pipeline 2: Generation Q&A pipeline (without context)
For this example we are using `databricks/dolly-v2-3b` model. It can be any other model available in huggingface hub.

Usage example: 
```python
from gptpedia.modules.models.generation_base_pipeline import GenerationPipelineBase
generation_pipeline = GenerationPipelineBase()
question = "What is the shape of the Earth?"
answer = generation_pipeline.generate_answer(question=question, context="")
print("Question: ",  question)
print("Answers: ", answer)
```
Result:
```
Question: What is the shape of the Earth?
Answers:  The shape of the Earth is a longstanding subject of debate. 
Currently, the Earth is presumed to be approximately an Ellipsoid, 
which is a family of approximate shapes that include a Homogeneous 
Oblate spheroid (egg-shaped), Ellipses, and Hyperbolic Ellipses.\n\n^^
```

### Pipeline 3: Generation Q&A pipeline (with context)
For this example we are using `databricks/dolly-v2-3b` model. It can be any other model available in huggingface hub.

Usage example: 
```python
from gptpedia.modules.models.generation_base_pipeline import GenerationPipelineBase
from gptpedia.modules.models.context_search import ContextPipeline
generation_pipeline = GenerationPipelineBase()
context_search_pipeline = ContextPipeline()

question = "What is the shape of the Earth?"
context = context_search_pipeline.generate_contex(question)
answer = generation_pipeline.generate_answer(question=question, context=context)
print("Question: ",  question)
print("Answers: ", answer)
print("Context:", context)
```
Result:
```
Question:  What is the shape of the Earth?
Answers:  Earth has a roughly spherical shape
Context:  <context found>
```
