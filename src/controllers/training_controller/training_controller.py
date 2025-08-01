import torch
import pandas as pd
from datasets import Dataset
from transformers import TrainingArguments, AutoTokenizer, AutoModelForCausalLM
from trl import SFTTrainer, SFTConfig
from peft import LoraConfig
from config.config import get_settings
import logging

class training_controller:
    def __init__(self,base_llm,db_client):
        self.base_llm = base_llm
        self.db_client = db_client
        self.settings = get_settings()
        self.logger = logging.getLogger('uvicorn')
        
        self.model = AutoModelForCausalLM.from_pretrained(self.base_llm, torch_dtype=torch.bfloat16).to("cuda")
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_llm)
        
    
    async def run(self):
        self.logger.info("Starting training process...")
        
        train_data = await self.prepare_data(type='train')
        eval_data = await self.prepare_data(type='val')
        
        if len(train_data) == 0 or len(eval_data) == 0:
            self.logger.error("No training or evaluation data found.")
            return False
        
        self.train(train_data,eval_data)
        
        self.logger.info("Training completed successfully.")
        
        return True
    
    def train(self,train_data,eval_data):
        
        sft_config = TrainingArguments(
            learning_rate=self.settings.LEARNING_RATE, # Learning rate for training. 
            num_train_epochs=self.settings.NUM_EPOCHS, #  Set the number of epochs to train the model.
            per_device_train_batch_size=self.settings.BATCH_SIZE, # Batch size for each device (e.g., GPU) during training. 
            gradient_accumulation_steps=8, # Number of steps before performing a backward/update pass to accumulate gradients.
            gradient_checkpointing=False, # Enable gradient checkpointing to reduce memory usage during training at the cost of slower training speed.
            logging_steps=10,  # Frequency of logging training progress (log every 10 steps).
            output_dir=self.settings.TRAINING_OUTPUT_DIR, # Directory to save the model and training artifacts.
            save_strategy="epoch", # Save the model at the end of each epoch.
            evaluation_strategy="epoch", # Evaluate the model at the end of each epoch.
            report_to="wandb", # Report training metrics to Weights & Biases for tracking.
            run_name=f"training_run_{self.base_llm}", # Name of the training run for tracking in Weights & Biases.
            logging_dir=self.settings.LOGGING_DIR, # Directory to save logs.
            bf16=True, # Use bfloat16 precision for training to reduce memory usage and speed up training on supported hardware.
            optim="adamw_torch", # Use the AdamW optimizer from PyTorch.
            lr_scheduler_type="cosine", # Use a cosine learning rate scheduler to adjust the learning rate during training.
            warmup_ratio=0.1 # Warmup ratio for the learning rate scheduler, which helps stabilize training in the initial phase.
            )
        
        sft_trainer = SFTTrainer(
            model=self.model,
            args=sft_config,
            train_dataset=train_data,
            eval_dataset=eval_data,
            processing_class=self.tokenizer,
            peft_config=LoraConfig()
        )
        
        sft_trainer.train()
        
        sft_trainer.save_model(self.settings.TRAINING_OUTPUT_DIR)
        self.logger.info(f"Model saved to {self.settings.TRAINING_OUTPUT_DIR}")
        
        return True        
    
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
        
        

