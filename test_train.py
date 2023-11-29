
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

model = None
def test_train(device='cuda:5'):
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
    model = model.train()
    # print_model_info(model)

    with open('./datas/datas-v2.json', 'r') as f:
        datas = json.load(f)
    checkpoints_path = './checkpoints'
    # delete_files_in_directory(checkpoints_path)
    n_epoch = 20
    batch_size = 10
    train_loop(model, datas, checkpoints_path, n_epoch, batch_size, device=device)
    # train_loop(model, datas, checkpoints_path, n_epoch, batch_size, resume_path='./checkpoints-resume/last_loss')

test_train()
