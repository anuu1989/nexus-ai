"""
LoRA (Low-Rank Adaptation) System for NexusAI
Implements fine-tuning capabilities for language models
"""

import os
import json
import torch
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib

# LoRA and fine-tuning dependencies
try:
    from transformers import (
        AutoTokenizer, AutoModelForCausalLM, 
        TrainingArguments, Trainer, DataCollatorForLanguageModeling
    )
    from peft import (
        LoraConfig, get_peft_model, TaskType, 
        PeftModel, PeftConfig
    )
    from datasets import Dataset
    import accelerate
except ImportError as e:
    print(f"LoRA dependencies not installed: {e}")
    print("Install with: pip install transformers peft accelerate datasets")

class LoRASystem:
    """Advanced LoRA system for fine-tuning language models"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.base_model = None
        self.tokenizer = None
        self.lora_models = {}  # Store multiple LoRA adapters
        self.training_data = []
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize base model
        self._initialize_base_model()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default LoRA configuration"""
        return {
            'base_model': 'microsoft/DialoGPT-medium',  # Smaller model for demo
            'lora_r': 16,  # Rank of adaptation
            'lora_alpha': 32,  # LoRA scaling parameter
            'lora_dropout': 0.1,
            'target_modules': ['c_attn', 'c_proj'],  # For GPT-2 based models
            'task_type': TaskType.CAUSAL_LM,
            'max_length': 512,
            'training_args': {
                'output_dir': './lora_models',
                'num_train_epochs': 3,
                'per_device_train_batch_size': 4,
                'gradient_accumulation_steps': 2,
                'warmup_steps': 100,
                'learning_rate': 5e-4,
                'logging_steps': 10,
                'save_steps': 500,
                'evaluation_strategy': 'steps',
                'eval_steps': 500,
                'save_total_limit': 3,
                'load_best_model_at_end': True,
                'metric_for_best_model': 'eval_loss',
                'greater_is_better': False,
                'dataloader_pin_memory': False,
                'fp16': torch.cuda.is_available(),
            }
        }
    
    def _initialize_base_model(self):
        """Initialize the base model and tokenizer"""
        try:
            model_name = self.config['base_model']
            print(f"Loading base model: {model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.base_model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                low_cpu_mem_usage=True
            )
            
            print(f"✅ Base model loaded successfully on {self.device}")
            
        except Exception as e:
            print(f"❌ Error loading base model: {e}")
            # Try a smaller fallback model
            try:
                self.tokenizer = AutoTokenizer.from_pretrained('gpt2')
                self.tokenizer.pad_token = self.tokenizer.eos_token
                self.base_model = AutoModelForCausalLM.from_pretrained('gpt2')
                print("✅ Fallback model (GPT-2) loaded successfully")
            except Exception as fallback_error:
                print(f"❌ Fallback model failed: {fallback_error}")
    
    def create_lora_adapter(self, adapter_name: str, custom_config: Dict[str, Any] = None) -> str:
        """Create a new LoRA adapter"""
        try:
            if not self.base_model:
                raise Exception("Base model not loaded")
            
            # Merge custom config with defaults
            lora_config_dict = {
                'r': custom_config.get('lora_r', self.config['lora_r']),
                'lora_alpha': custom_config.get('lora_alpha', self.config['lora_alpha']),
                'lora_dropout': custom_config.get('lora_dropout', self.config['lora_dropout']),
                'target_modules': custom_config.get('target_modules', self.config['target_modules']),
                'task_type': self.config['task_type'],
                'bias': 'none'
            }
            
            # Create LoRA configuration
            lora_config = LoraConfig(**lora_config_dict)
            
            # Create PEFT model
            peft_model = get_peft_model(self.base_model, lora_config)
            
            # Store adapter
            adapter_id = hashlib.md5(f"{adapter_name}{datetime.now()}".encode()).hexdigest()[:8]
            self.lora_models[adapter_id] = {
                'name': adapter_name,
                'model': peft_model,
                'config': lora_config_dict,
                'created_at': datetime.now().isoformat(),
                'trained': False,
                'training_data_count': 0
            }
            
            print(f"✅ Created LoRA adapter '{adapter_name}' with ID: {adapter_id}")
            return adapter_id
            
        except Exception as e:
            print(f"❌ Error creating LoRA adapter: {e}")
            return None
    
    def add_training_data(self, data: List[Dict[str, str]], adapter_id: str = None):
        """Add training data for LoRA fine-tuning"""
        try:
            formatted_data = []
            
            for item in data:
                if 'input' in item and 'output' in item:
                    # Format as conversation
                    text = f"Human: {item['input']}\nAssistant: {item['output']}"
                elif 'text' in item:
                    # Direct text input
                    text = item['text']
                else:
                    continue
                
                formatted_data.append({
                    'text': text,
                    'adapter_id': adapter_id,
                    'added_at': datetime.now().isoformat()
                })
            
            self.training_data.extend(formatted_data)
            
            # Update adapter training data count
            if adapter_id and adapter_id in self.lora_models:
                self.lora_models[adapter_id]['training_data_count'] += len(formatted_data)
            
            print(f"✅ Added {len(formatted_data)} training examples")
            
        except Exception as e:
            print(f"❌ Error adding training data: {e}")
    
    def train_lora_adapter(self, adapter_id: str, training_args: Dict[str, Any] = None) -> bool:
        """Train a LoRA adapter"""
        try:
            if adapter_id not in self.lora_models:
                raise Exception(f"Adapter {adapter_id} not found")
            
            adapter_info = self.lora_models[adapter_id]
            peft_model = adapter_info['model']
            
            # Get training data for this adapter
            adapter_data = [
                item for item in self.training_data 
                if item.get('adapter_id') == adapter_id or item.get('adapter_id') is None
            ]
            
            if not adapter_data:
                raise Exception("No training data available")
            
            print(f"Training adapter '{adapter_info['name']}' with {len(adapter_data)} examples")
            
            # Prepare dataset
            dataset = self._prepare_dataset(adapter_data)
            
            # Setup training arguments
            train_args = self.config['training_args'].copy()
            if training_args:
                train_args.update(training_args)
            
            train_args['output_dir'] = os.path.join(train_args['output_dir'], adapter_id)
            training_arguments = TrainingArguments(**train_args)
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False,
                pad_to_multiple_of=8
            )
            
            # Create trainer
            trainer = Trainer(
                model=peft_model,
                args=training_arguments,
                train_dataset=dataset,
                data_collator=data_collator,
                tokenizer=self.tokenizer,
            )
            
            # Train the model
            print("🚀 Starting training...")
            trainer.train()
            
            # Save the adapter
            adapter_path = os.path.join(train_args['output_dir'], 'final_adapter')
            trainer.save_model(adapter_path)
            
            # Update adapter info
            adapter_info['trained'] = True
            adapter_info['model_path'] = adapter_path
            adapter_info['trained_at'] = datetime.now().isoformat()
            
            print(f"✅ Training completed for adapter '{adapter_info['name']}'")
            return True
            
        except Exception as e:
            print(f"❌ Error training LoRA adapter: {e}")
            return False
    
    def _prepare_dataset(self, data: List[Dict[str, str]]) -> Dataset:
        """Prepare dataset for training"""
        try:
            texts = [item['text'] for item in data]
            
            # Tokenize texts
            tokenized = self.tokenizer(
                texts,
                truncation=True,
                padding=True,
                max_length=self.config['max_length'],
                return_tensors='pt'
            )
            
            # Create dataset
            dataset = Dataset.from_dict({
                'input_ids': tokenized['input_ids'],
                'attention_mask': tokenized['attention_mask'],
                'labels': tokenized['input_ids'].clone()
            })
            
            return dataset
            
        except Exception as e:
            print(f"❌ Error preparing dataset: {e}")
            return None
    
    def load_lora_adapter(self, adapter_path: str, adapter_name: str) -> str:
        """Load a trained LoRA adapter from disk"""
        try:
            if not os.path.exists(adapter_path):
                raise Exception(f"Adapter path does not exist: {adapter_path}")
            
            # Load the adapter
            peft_model = PeftModel.from_pretrained(self.base_model, adapter_path)
            
            # Create adapter ID
            adapter_id = hashlib.md5(f"{adapter_name}{adapter_path}".encode()).hexdigest()[:8]
            
            # Store adapter
            self.lora_models[adapter_id] = {
                'name': adapter_name,
                'model': peft_model,
                'model_path': adapter_path,
                'created_at': datetime.now().isoformat(),
                'trained': True,
                'loaded_from_disk': True
            }
            
            print(f"✅ Loaded LoRA adapter '{adapter_name}' from {adapter_path}")
            return adapter_id
            
        except Exception as e:
            print(f"❌ Error loading LoRA adapter: {e}")
            return None
    
    def generate_with_adapter(self, prompt: str, adapter_id: str, max_length: int = 200) -> str:
        """Generate text using a specific LoRA adapter"""
        try:
            if adapter_id not in self.lora_models:
                raise Exception(f"Adapter {adapter_id} not found")
            
            adapter_info = self.lora_models[adapter_id]
            model = adapter_info['model']
            
            # Tokenize input
            inputs = self.tokenizer.encode(prompt, return_tensors='pt').to(self.device)
            
            # Generate
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_length=max_length,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode output
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the input prompt from the output
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
            
        except Exception as e:
            print(f"❌ Error generating with adapter: {e}")
            return ""
    
    def list_adapters(self) -> List[Dict[str, Any]]:
        """List all available LoRA adapters"""
        adapters = []
        for adapter_id, info in self.lora_models.items():
            adapters.append({
                'id': adapter_id,
                'name': info['name'],
                'trained': info['trained'],
                'created_at': info['created_at'],
                'training_data_count': info.get('training_data_count', 0),
                'config': info.get('config', {})
            })
        return adapters
    
    def delete_adapter(self, adapter_id: str) -> bool:
        """Delete a LoRA adapter"""
        try:
            if adapter_id not in self.lora_models:
                return False
            
            adapter_info = self.lora_models[adapter_id]
            
            # Delete model files if they exist
            if 'model_path' in adapter_info and os.path.exists(adapter_info['model_path']):
                import shutil
                shutil.rmtree(adapter_info['model_path'], ignore_errors=True)
            
            # Remove from memory
            del self.lora_models[adapter_id]
            
            print(f"✅ Deleted adapter '{adapter_info['name']}'")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting adapter: {e}")
            return False
    
    def get_adapter_info(self, adapter_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an adapter"""
        if adapter_id not in self.lora_models:
            return None
        
        info = self.lora_models[adapter_id].copy()
        
        # Add model parameters count
        if 'model' in info:
            try:
                trainable_params = sum(p.numel() for p in info['model'].parameters() if p.requires_grad)
                total_params = sum(p.numel() for p in info['model'].parameters())
                info['trainable_params'] = trainable_params
                info['total_params'] = total_params
                info['trainable_percentage'] = (trainable_params / total_params) * 100
            except:
                pass
            
            # Remove model object from info (not serializable)
            del info['model']
        
        return info
    
    def export_adapter(self, adapter_id: str, export_path: str) -> bool:
        """Export a LoRA adapter for sharing"""
        try:
            if adapter_id not in self.lora_models:
                return False
            
            adapter_info = self.lora_models[adapter_id]
            model = adapter_info['model']
            
            # Save the adapter
            model.save_pretrained(export_path)
            
            # Save metadata
            metadata = {
                'name': adapter_info['name'],
                'config': adapter_info.get('config', {}),
                'created_at': adapter_info['created_at'],
                'base_model': self.config['base_model'],
                'training_data_count': adapter_info.get('training_data_count', 0)
            }
            
            with open(os.path.join(export_path, 'metadata.json'), 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ Exported adapter to {export_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting adapter: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get LoRA system statistics"""
        try:
            trained_adapters = sum(1 for info in self.lora_models.values() if info['trained'])
            total_training_data = len(self.training_data)
            
            return {
                'base_model': self.config['base_model'],
                'total_adapters': len(self.lora_models),
                'trained_adapters': trained_adapters,
                'untrained_adapters': len(self.lora_models) - trained_adapters,
                'total_training_examples': total_training_data,
                'device': str(self.device),
                'cuda_available': torch.cuda.is_available()
            }
            
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {}

# Global LoRA instance
lora_system = None

def get_lora_system() -> LoRASystem:
    """Get or create global LoRA system instance"""
    global lora_system
    if lora_system is None:
        lora_system = LoRASystem()
    return lora_system

def initialize_lora():
    """Initialize LoRA system"""
    try:
        global lora_system
        lora_system = LoRASystem()
        print("✅ LoRA system initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing LoRA system: {e}")
        return False