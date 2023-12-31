
from src.model_byt5.tokenizer import Tokenizer_byt5
from src.model_byt5.model import Transformer_byt5
from convert import hf_model_weight_name_mapping
import torch
import json
from collections import OrderedDict
import time
from src.utils import print_model_info, delete_files_in_directory
from src.model_byt5.train import train_loop
import shutil
import os
model_weights_path = "./test_models/byt5-small/pytorch_model.bin"
model_config_path = "./test_models/byt5-small/config.json"

# model_weights_path = "./test_models/byt5-large/pytorch_model.bin"
# model_config_path = "./test_models/byt5-large/config.json"

config = None
with open(model_config_path, 'r') as f:
    config = json.load(f)


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

def test_model():
    print('--------------------------------')
    model = Transformer_byt5(config=config)
   
    # print(model)
    input_ids = torch.tensor([list("12345".encode("utf-8"))]) + 3  # add 3 for special tokens
    labels = torch.tensor([list("123".encode("utf-8"))]) + 3  # add 3 for special tokens
    out_infos = model(input_ids, labels)
    print(out_infos)
    print(sum(p.numel() for p in model.parameters() if p.requires_grad))
    torch.save(model.state_dict(), './test_models/byt5-small/pytorch_model_my.bin')

model = None

def test_model_forward(input_ids, labels, training):
    state_dict = torch.load(model_weights_path)
    state_dict_new = OrderedDict()
    for name, tensor_ in state_dict.items():
        new_name = hf_model_weight_name_mapping(name)
        if new_name:
            state_dict_new[hf_model_weight_name_mapping(name)] = tensor_
    global model  
    if model is None:
        model = Transformer_byt5(config=config)
        model.load_state_dict(state_dict_new)

    if training:
        model = model.train()  
    else:
        model = model.eval()
    # input_ids = torch.tensor([list(str_in.encode("utf-8"))]) + 3  # add 3 for special tokens
    # labels = torch.tensor([list(str_out.encode("utf-8"))]) + 3  # add 3 for special tokens

    t0 = time.time()
    n = 1
    for i in range(n):
        print('model.training', model.training)
        torch.manual_seed(0)
        _, loss = model(input_ids, labels=labels)
    t1 = time.time()
    print(loss, 'deltaT', (t1 - t0) / n)


def test_model_1(training):
    inputs = ["hello world"]
    outputs = ['你好世界']
    batches = [[inputs, outputs]]
    for it in batches:
        input_ids = []
        for x in it[0]:
            input_ids.append([y + 3 for y in x.encode("utf-8")])
        label_ids = []
        for x in it[1]:
            label_ids.append([y + 3 for y in x.encode("utf-8")])  
        input_ids = torch.tensor(input_ids)
        label_ids = torch.tensor(label_ids)
        test_model_forward(input_ids, label_ids, training) 

def test_model_generate(input_ids, use_cache=False, max_length=200):
    state_dict = torch.load(model_weights_path)
    state_dict_new = OrderedDict()
    for name, tensor_ in state_dict.items():
        new_name = hf_model_weight_name_mapping(name)
        if new_name:
            state_dict_new[hf_model_weight_name_mapping(name)] = tensor_
    global model        

    if model is None:
        model = Transformer_byt5(config=config)
        model.load_state_dict(state_dict_new)
    model = model.eval()

    t0 = time.time()
    n = 1
    for i in range(n):
        out_ids = model.generate(input_ids, max_length=max_length, use_cache=use_cache)

    t1 = time.time()
    print('deltaT', (t1 - t0) / n)
    return out_ids
    

tk = Tokenizer_byt5()
# test_model_generate(input_ids=torch.tensor([tk.text2ids('hello world!'), tk.text2ids('hello world!')]))
# test_model_generate(input_ids=torch.tensor([tk.text2ids('一条大')]))
# test_model_generate(input_ids=torch.tensor([tk.text2ids('hello world')]), use_cache=False)

def test_generate1(use_cache):
    out_ids = test_model_generate(input_ids=torch.tensor([tk.text2ids('hello world!'), tk.text2ids('你好世界')]), use_cache=use_cache, max_length=200)
    """
    will print:
    the the the the the the the the the the the the the the the the the the the the the the the the the the the the the the the the the the the the the the the the the the the the the th </s>
    大好世界大好世界大好世界大好世界大好世界大好世界大好世界大好世界大好世界大好世界大好世界大好世界大好世界大好世界大好世界大</s>
    """
    for ids in out_ids.tolist():
        print(tk.ids2text(ids))


def test_generate2(use_cache):
    out_ids = test_model_generate(input_ids=torch.tensor([tk.text2ids('hello world!'), tk.text2ids('你好世界')]), use_cache=use_cache, max_length=200)
    """
    will print:

    """
    for ids in out_ids.tolist():
        print(tk.ids2text(ids))



# tokenizer_tests()
# test_model()
# tensor(5.0514, grad_fn=<NllLossBackward0>) deltaT 0.43586087226867676
test_model_1(False)
# test_generate2(False)
# test_generate2(True)

# def test_train():
#     state_dict = torch.load(model_weights_path)
#     state_dict_new = OrderedDict()
#     for name, tensor_ in state_dict.items():
#         new_name = hf_model_weight_name_mapping(name)
#         if new_name:
#             state_dict_new[hf_model_weight_name_mapping(name)] = tensor_
#     global model        

#     if model is None:
#         model = Transformer_byt5(config=config)
#         model.load_state_dict(state_dict_new)
#     model = model.train()
#     # print_model_info(model)

#     with open('./datas/datas-v2.json', 'r') as f:
#         datas = json.load(f)
#     checkpoints_path = './checkpoints'
#     # delete_files_in_directory(checkpoints_path)
#     n_epoch = 20
#     batch_size = 10
#     train_loop(model, datas, checkpoints_path, n_epoch, batch_size)
#     # train_loop(model, datas, checkpoints_path, n_epoch, batch_size, resume_path='./checkpoints-resume/last_loss')

# test_train()


def test_checkpoint(path, prompts, max_length=200):
    print('test_checkpoint path', path)
    input_ids=torch.tensor([[*tk.text2ids(prompts), 258]])
    state_dict = torch.load(path)
    model = Transformer_byt5(config=config)
    model.load_state_dict(state_dict)
    model = model.eval()
    t0 = time.time()
    out_ids = model.generate(input_ids, max_length=max_length, use_cache=True)
    # print('deltaT', (time.time() - t0))
    ids = out_ids.tolist()[0]
    # print(ids)
    print(prompts, ':', tk.ids2text(ids))

# test_checkpoint('./checkpoints-saved3/last_loss/pytorch_model.bin', 'hello world!')
# test_checkpoint('./checkpoints-saved3/last_loss/pytorch_model.bin', 'one sentence speech recognition')
# test_checkpoint('./checkpoints-saved3/last_loss/pytorch_model.bin', 'Audio classification')


# test_checkpoint('./checkpoints-saved3/minimal_loss/pytorch_model.bin', 'hello world!')
# test_checkpoint('./checkpoints-saved3/minimal_loss/pytorch_model.bin', 'Posture classification training and model usage')


def test_eval():
    prompts = ['hello world!',
               'one sentence speech recognition', 
               'Audio classification',
               'Posture classification training and model usage',
               '选一个字母',
               '选一个字母，让它旋转',
               '添加一个声音',
               '启动客户端']

    

    for prompt in prompts:
        test_checkpoint('./checkpoints/last_loss/pytorch_model.bin', prompt)

    for prompt in prompts:
        test_checkpoint('./checkpoints/minimal_loss/pytorch_model.bin', prompt)    
        


# test_eval()