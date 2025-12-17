import numpy as np
from django.db import transaction
from Resume.models import Question
from Resume.embeddings import embed_texts

qs = Question.objects.filter(question_type="subjective")
texts = [q.reference_answer or "" for q in qs]
embs = embed_texts(texts,batch_size=16)


for q,emb in zip(qs, embs):
    q.reference_vector = emb.tolist()
with transaction.atomic():


    Question.objects.bulk_update(qs,["reference_vector"])