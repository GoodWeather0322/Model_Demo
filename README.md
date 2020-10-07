# Model Demo

## Intro

- Model demo website made by Python Flask
- Demo some NLP models


## Model

- Chinese Maximum Matching Word Segmentation
- [Chinese News Article Generator](https://github.com/GoodWeather0322/Chinese-News-Generator)
- [Chinese POS tagging](https://github.com/GoodWeather0322/Chinese_POS)   

------

### Chinese Maximum Matching Word Segmentation

A Maximum Matching Algorithm implementation of Chinese Word Segmentation 

- forward & backward

### Chinese News Article Generator

A PyTorch implementation of Chinese News Article Generator with with [Huggingface Transformers](https://github.com/huggingface/transformers)

Model is based on Pretrained [GPT-2 Model](https://github.com/openai/gpt-2) and [BERT chinese tokenizer](https://github.com/google-research/bert), finetune by chinese news articles

- [GPT-2 Model](https://github.com/openai/gpt-2)
- [BERT chinese tokenizer](https://github.com/google-research/bert)
- Training Dataset (News articles & PTT articles)
    - CNA News
    - UDN News
    - CTS News
    - PTT Gossiping

### Chinese POS tagging
A PyTorch implementation of Chinese Part-of-Speech tagging with with [Huggingface Transformers](https://github.com/huggingface/transformers)

Model is based on Pretrained [Albert Model](https://github.com/google-research/albert) and [BERT chinese tokenizer](https://github.com/google-research/bert), finetune by chinese news articles

- [Pretrained Chinese Albert Model](https://github.com/brightmart/albert_zh)
- [BERT chinese tokenizer](https://github.com/google-research/bert)
- Use MONPA and CKIP for pre tagging
- Training Dataset (News articles & PTT articles) 
    - CNA News

