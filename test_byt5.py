
from src.model_byt5.tokenizer import Tokenizer_byt5
from src.model_byt5.model import Transformer_byt5
from convert import hf_model_weight_name_mapping
import torch
import json
from collections import OrderedDict
import time
def test_tokenizer(input):
    tk = Tokenizer_byt5()
    print('--------------------------------')
    print('input: ', input)
    tokens = tk.text2tokens(input)
    print('tokens: ', tokens)
    ids = tk.tokens2ids(tokens)
    print('ids: ', ids)
    tokens2 = tk.ids2tokens(ids)
    # print('tokens2: ', tokens2)
    assert tokens == tokens2 

    output = tk.tokens2text(tokens2)
    print('output: ', output)

    output_cleaned = tk.text_clean_special_tokens(output)
  

    input_cleaned = tk.text_clean_special_tokens(input)
    print('output_cleaned: ', output_cleaned)

    assert input_cleaned == output_cleaned
    with open('tokenizer_config.json', 'w') as f:
        f.write(json.dumps(tk.get_config(), indent=4))

def tokenizer_tests():
    test_tokenizer('qwew<pad>qeqwewqe</s>qwewqeqw<unk>ewqe')
    test_tokenizer('hello world!')
    test_tokenizer('你好世界！')
    test_tokenizer('你好世界！hello world! \n1 \t !@#$%^&* <<<<extra_id_119>123456')
    test_tokenizer('Life is like a box of chocolates.')

# tokenizer_tests()

def test_model():
    print('--------------------------------')
    model = Transformer_byt5()
   
    print(model)
    input_ids = torch.tensor([list("12345".encode("utf-8"))]) + 3  # add 3 for special tokens
    labels = torch.tensor([list("12345".encode("utf-8"))]) + 3  # add 3 for special tokens
    out_infos = model(input_ids, labels)
    print(out_infos)
    print(sum(p.numel() for p in model.parameters() if p.requires_grad))
    torch.save(model.state_dict(), './test_models/byt5-small/pytorch_model_my.bin')

# test_model()

def test_model_with_weights():
    state_dict = torch.load('./test_models/byt5-small/pytorch_model.bin')
    state_dict_new = OrderedDict()
    for name, tensor_ in state_dict.items():
        new_name = hf_model_weight_name_mapping(name)
        if new_name:
            state_dict_new[hf_model_weight_name_mapping(name)] = tensor_
    model = Transformer_byt5()
    model.load_state_dict(state_dict_new)
    model = model.eval()
    input_ids = torch.tensor([list("12345".encode("utf-8"))]) + 3  # add 3 for special tokens
    labels = torch.tensor([list("12345".encode("utf-8"))]) + 3  # add 3 for special tokens


    # t0 = time.time()
    # out_infos = model(input_ids, labels)
    # t1 = time.time()
    # print(out_infos['loss'], 'deltaT', t1 - t0)


    t0 = time.time()
    n = 1
    for i in range(n):
        out_infos = model(input_ids, labels=labels)
    t1 = time.time()
    print(out_infos['loss'], 'deltaT', (t1 - t0) / n)
    
test_model_with_weights()    