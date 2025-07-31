import torch
import pandas as pd
from datasets import Dataset
from transformers import TrainingArguments, AutoTokenizer, AutoModelForCausalLM
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM, SFTConfig
from config.config import get_settings
import logging

class training_controller:
    def __init__(self,base_llm,db_client ):
        self.base_llm = base_llm
        self.db_client = db_client
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
        self.model = AutoModelForCausalLM.from_pretrained(self.base_llm, torch_dtype=torch.bfloat16).to("cuda")
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_llm, use_fast=True)
        
    
    def train(self,train_data,eval_data):
        
        sft_config = TrainingArguments(
            learning_rate=8e-5, # Learning rate for training. 
            num_train_epochs=2, #  Set the number of epochs to train the model.
            per_device_train_batch_size=1, # Batch size for each device (e.g., GPU) during training. 
            gradient_accumulation_steps=8, # Number of steps before performing a backward/update pass to accumulate gradients.
            gradient_checkpointing=False, # Enable gradient checkpointing to reduce memory usage during training at the cost of slower training speed.
            logging_steps=2,  # Frequency of logging training progress (log every 2 steps).
            )
        
        sft_trainer = SFTTrainer(
            model=self.model,
            args=sft_config,
            train_dataset=train_data,
            eval_dataset=eval_data,
            processing_class=self.tokenizer,
        )
        
        sft_trainer.train()
        
    
    async def prepare_data(self,type):
        data = await  self.db_client.get_qa_pairs(type)
        
        dataset = [{
            "messages":[
                {"role": "user", "content": item.question},
                {"role": "assistant", "content": item.answer}
            ]
        } for item in data
        ]
        
        return Dataset.from_list(dataset)
        
        

