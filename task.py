#!/usr/bin/python
from gensim.models.word2vec import Word2Vec
import os
model_restored = Word2Vec.load('~/repos/CloudApp/test/pretrained.model')
output = model_restored.most_similar("bear")
n = 10
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'output.txt'),'w+')as outFile:
    outFile.writelines(list(map(lambda x: x[0] + '\n', output[0:n if len(output) > n else -1])))
