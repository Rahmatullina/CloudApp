#!/usr/bin/python
from gensim.models.word2vec import Word2Vec
model_restored = Word2Vec.load('./pretrained.model')
output = model_restored.most_similar("bear")
n = 10
with open('output.txt','w')as outFile:
    outFile.writelines(list(map(lambda x: x[0] + '\n', output[0:n if len(output) > n else -1])))
