import json

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# SentinelAI: MuRIL Hinglish Fine-tuning\n",
                "\n",
                "**Run this notebook with a Google Colab GPU runtime.**\n",
                "\n",
                "This notebook fine-tunes `google/muril-base-cased` on the prepared Hinglish sentiment dataset."
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Environment Check & Dependency Installation"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "!pip install -q transformers datasets evaluate scikit-learn accelerate"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import torch\n",
                "import transformers\n",
                "import sys\n",
                "\n",
                "print(f\"Python version: {sys.version.split()[0]}\")\n",
                "print(f\"PyTorch version: {torch.__version__}\")\n",
                "print(f\"Transformers version: {transformers.__version__}\")\n",
                "\n",
                "device = \"cpu\"\n",
                "if torch.cuda.is_available():\n",
                "    device = \"cuda\"\n",
                "    print(\"CUDA availability: True\")\n",
                "    print(f\"GPU name: {torch.cuda.get_device_name(0)}\")\n",
                "    # get memory in GB\n",
                "    mem = torch.cuda.get_device_properties(0).total_memory / 1e9\n",
                "    print(f\"GPU memory: {mem:.2f} GB\")\n",
                "elif torch.backends.mps.is_available():\n",
                "    device = \"mps\"\n",
                "    print(\"MPS availability: True\")\n",
                "else:\n",
                "    print(\"CUDA availability: False\")\n",
                "\n",
                "print(f\"\\nUsing device: {device}\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Configuration"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import os\n",
                "\n",
                "# Path configuration\n",
                "# You can change this to point to Google Drive if mounted, e.g. '/content/drive/MyDrive/sentinelai/data/processed/hinglish'\n",
                "DATA_DIR = \"data/processed/hinglish\"\n",
                "\n",
                "TRAIN_PATH = os.path.join(DATA_DIR, \"train.tsv\")\n",
                "VALID_PATH = os.path.join(DATA_DIR, \"validation.tsv\")\n",
                "\n",
                "MODEL_NAME = \"google/muril-base-cased\"\n",
                "OUTPUT_DIR = \"models/hinglish_muril\"\n",
                "REPORTS_DIR = \"reports\"\n",
                "\n",
                "# Training configuration\n",
                "MAX_LENGTH = 128\n",
                "BATCH_SIZE = 16\n",
                "EVAL_BATCH_SIZE = 32\n",
                "LEARNING_RATE = 2e-5\n",
                "NUM_EPOCHS = 3\n",
                "WEIGHT_DECAY = 0.01\n",
                "WARMUP_RATIO = 0.1\n",
                "SEED = 42\n",
                "\n",
                "os.makedirs(OUTPUT_DIR, exist_ok=True)\n",
                "os.makedirs(REPORTS_DIR, exist_ok=True)\n",
                "\n",
                "import random\n",
                "import numpy as np\n",
                "random.seed(SEED)\n",
                "np.random.seed(SEED)\n",
                "torch.manual_seed(SEED)\n",
                "if torch.cuda.is_available():\n",
                "    torch.cuda.manual_seed_all(SEED)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Dataset Loading & Validation"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import pandas as pd\n",
                "\n",
                "def load_data(path):\n",
                "    if not os.path.exists(path):\n",
                "        raise FileNotFoundError(f\"File not found: {path}. Make sure to upload the dataset or mount Google Drive.\")\n",
                "    \n",
                "    df = pd.read_csv(path, sep='\\t', header=None, names=['id', 'text', 'label'])\n",
                "    # Basic validation\n",
                "    df = df.dropna(subset=['text', 'label'])\n",
                "    df['label'] = df['label'].astype(int)\n",
                "    return df\n",
                "\n",
                "train_df = load_data(TRAIN_PATH)\n",
                "valid_df = load_data(VALID_PATH)\n",
                "\n",
                "print(f\"Train size: {len(train_df)}\")\n",
                "print(f\"Validation size: {len(valid_df)}\")\n",
                "\n",
                "# Display label distribution\n",
                "print(\"\\nTrain Distribution:\\n\", train_df['label'].value_counts())\n",
                "print(\"\\nValidation Distribution:\\n\", valid_df['label'].value_counts())"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 4. Tokenization"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from transformers import AutoTokenizer\n",
                "from datasets import Dataset\n",
                "\n",
                "tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)\n",
                "\n",
                "train_dataset = Dataset.from_pandas(train_df)\n",
                "valid_dataset = Dataset.from_pandas(valid_df)\n",
                "\n",
                "def tokenize_function(examples):\n",
                "    return tokenizer(\n",
                "        examples[\"text\"],\n",
                "        padding=\"max_length\",\n",
                "        truncation=True,\n",
                "        max_length=MAX_LENGTH\n",
                "    )\n",
                "\n",
                "tokenized_train = train_dataset.map(tokenize_function, batched=True)\n",
                "tokenized_valid = valid_dataset.map(tokenize_function, batched=True)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 5. Model Initialization"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from transformers import AutoModelForSequenceClassification\n",
                "\n",
                "id2label = {0: \"negative\", 1: \"neutral\", 2: \"positive\"}\n",
                "label2id = {\"negative\": 0, \"neutral\": 1, \"positive\": 2}\n",
                "\n",
                "model = AutoModelForSequenceClassification.from_pretrained(\n",
                "    MODEL_NAME,\n",
                "    num_labels=3,\n",
                "    id2label=id2label,\n",
                "    label2id=label2id\n",
                ")\n",
                "model.to(device)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 6. Training & Evaluation Setup"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from transformers import TrainingArguments, Trainer\n",
                "import evaluate\n",
                "import numpy as np\n",
                "from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix\n",
                "\n",
                "def compute_metrics(eval_pred):\n",
                "    logits, labels = eval_pred\n",
                "    predictions = np.argmax(logits, axis=-1)\n",
                "    \n",
                "    acc = accuracy_score(labels, predictions)\n",
                "    macro_f1 = f1_score(labels, predictions, average='macro')\n",
                "    weighted_f1 = f1_score(labels, predictions, average='weighted')\n",
                "    macro_precision = precision_score(labels, predictions, average='macro')\n",
                "    macro_recall = recall_score(labels, predictions, average='macro')\n",
                "    \n",
                "    per_class_f1 = f1_score(labels, predictions, average=None)\n",
                "    per_class_precision = precision_score(labels, predictions, average=None)\n",
                "    per_class_recall = recall_score(labels, predictions, average=None)\n",
                "    \n",
                "    cm = confusion_matrix(labels, predictions)\n",
                "    \n",
                "    # Returning standard metrics for logging\n",
                "    # Trainer expects scalar values in this dictionary.\n",
                "    return {\n",
                "        \"accuracy\": acc,\n",
                "        \"macro_f1\": macro_f1,\n",
                "        \"weighted_f1\": weighted_f1,\n",
                "        \"macro_precision\": macro_precision,\n",
                "        \"macro_recall\": macro_recall,\n",
                "        \"f1_0\": per_class_f1[0],\n",
                "        \"f1_1\": per_class_f1[1],\n",
                "        \"f1_2\": per_class_f1[2],\n",
                "        \"prec_0\": per_class_precision[0],\n",
                "        \"prec_1\": per_class_precision[1],\n",
                "        \"prec_2\": per_class_precision[2],\n",
                "        \"rec_0\": per_class_recall[0],\n",
                "        \"rec_1\": per_class_recall[1],\n",
                "        \"rec_2\": per_class_recall[2],\n",
                "    }\n",
                "\n",
                "training_args = TrainingArguments(\n",
                "    output_dir=OUTPUT_DIR,\n",
                "    eval_strategy=\"epoch\",\n",
                "    save_strategy=\"epoch\",\n",
                "    learning_rate=LEARNING_RATE,\n",
                "    per_device_train_batch_size=BATCH_SIZE,\n",
                "    per_device_eval_batch_size=EVAL_BATCH_SIZE,\n",
                "    num_train_epochs=NUM_EPOCHS,\n",
                "    weight_decay=WEIGHT_DECAY,\n",
                "    warmup_ratio=WARMUP_RATIO,\n",
                "    load_best_model_at_end=True,\n",
                "    metric_for_best_model=\"macro_f1\",\n",
                "    seed=SEED,\n",
                "    fp16=torch.cuda.is_available() and torch.cuda.is_bf16_supported() == False, # Use fp16 if CUDA is available but bf16 is not\n",
                "    bf16=torch.cuda.is_available() and torch.cuda.is_bf16_supported(), # Use bf16 if supported\n",
                "    report_to=\"none\"\n",
                ")\n",
                "\n",
                "trainer = Trainer(\n",
                "    model=model,\n",
                "    args=training_args,\n",
                "    train_dataset=tokenized_train,\n",
                "    eval_dataset=tokenized_valid,\n",
                "    tokenizer=tokenizer,\n",
                "    compute_metrics=compute_metrics,\n",
                ")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 7. Training"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import time\n",
                "start_time = time.time()\n",
                "train_result = trainer.train()\n",
                "train_time = time.time() - start_time\n",
                "print(f\"Training took {train_time:.2f} seconds\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 8. Best Model Saving"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "trainer.save_model(OUTPUT_DIR)\n",
                "print(f\"Best model saved to {OUTPUT_DIR}\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 9. Metrics & Report Generation"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import json\n",
                "from datetime import datetime\n",
                "\n",
                "# Evaluate on validation set one last time to get the final confusion matrix and metrics directly\n",
                "eval_preds = trainer.predict(tokenized_valid)\n",
                "predictions = np.argmax(eval_preds.predictions, axis=-1)\n",
                "labels = eval_preds.label_ids\n",
                "\n",
                "metrics = eval_preds.metrics\n",
                "cm = confusion_matrix(labels, predictions).tolist()\n",
                "\n",
                "report = {\n",
                "    \"timestamp\": datetime.utcnow().isoformat() + \"Z\",\n",
                "    \"environment\": {\n",
                "        \"python_version\": sys.version,\n",
                "        \"pytorch_version\": torch.__version__,\n",
                "        \"transformers_version\": transformers.__version__,\n",
                "        \"device\": device,\n",
                "        \"gpu\": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None\n",
                "    },\n",
                "    \"model\": {\n",
                "        \"base_model\": MODEL_NAME\n",
                "    },\n",
                "    \"dataset\": {\n",
                "        \"train_size\": len(train_dataset),\n",
                "        \"validation_size\": len(valid_dataset)\n",
                "    },\n",
                "    \"configuration\": {\n",
                "        \"max_length\": MAX_LENGTH,\n",
                "        \"batch_size\": BATCH_SIZE,\n",
                "        \"learning_rate\": LEARNING_RATE,\n",
                "        \"num_epochs\": NUM_EPOCHS,\n",
                "        \"weight_decay\": WEIGHT_DECAY,\n",
                "        \"warmup_ratio\": WARMUP_RATIO,\n",
                "        \"seed\": SEED,\n",
                "        \"fp16\": training_args.fp16,\n",
                "        \"bf16\": training_args.bf16\n",
                "    },\n",
                "    \"results\": {\n",
                "        \"accuracy\": metrics[\"test_accuracy\"],\n",
                "        \"macro_f1\": metrics[\"test_macro_f1\"],\n",
                "        \"weighted_f1\": metrics[\"test_weighted_f1\"],\n",
                "        \"per_class\": {\n",
                "            \"0\": {\n",
                "                \"precision\": metrics[\"test_prec_0\"],\n",
                "                \"recall\": metrics[\"test_rec_0\"],\n",
                "                \"f1\": metrics[\"test_f1_0\"]\n",
                "            },\n",
                "            \"1\": {\n",
                "                \"precision\": metrics[\"test_prec_1\"],\n",
                "                \"recall\": metrics[\"test_rec_1\"],\n",
                "                \"f1\": metrics[\"test_f1_1\"]\n",
                "            },\n",
                "            \"2\": {\n",
                "                \"precision\": metrics[\"test_prec_2\"],\n",
                "                \"recall\": metrics[\"test_rec_2\"],\n",
                "                \"f1\": metrics[\"test_f1_2\"]\n",
                "            }\n",
                "        },\n",
                "        \"confusion_matrix\": cm\n",
                "    },\n",
                "    \"training_time_seconds\": train_time\n",
                "}\n",
                "\n",
                "with open(os.path.join(REPORTS_DIR, \"hinglish_muril_results.json\"), \"w\", encoding=\"utf-8\") as f:\n",
                "    json.dump(report, f, indent=4)\n",
                "\n",
                "md_content = f\"\"\"# Hinglish MuRIL Fine-tuning Report\n",
                "\n",
                "**Timestamp:** {report['timestamp']}\n",
                "**Base Model:** {MODEL_NAME}\n",
                "**Device:** {report['environment']['device']} ({report['environment']['gpu']})\n",
                "**Training Time:** {train_time:.2f} seconds\n",
                "\n",
                "## Configuration\n",
                "- max_length: {MAX_LENGTH}\n",
                "- batch_size: {BATCH_SIZE}\n",
                "- learning_rate: {LEARNING_RATE}\n",
                "- num_epochs: {NUM_EPOCHS}\n",
                "- weight_decay: {WEIGHT_DECAY}\n",
                "- warmup_ratio: {WARMUP_RATIO}\n",
                "- seed: {SEED}\n",
                "\n",
                "## Results\n",
                "- **Macro F1:** {metrics['test_macro_f1']:.4f}\n",
                "- **Accuracy:** {metrics['test_accuracy']:.4f}\n",
                "- **Weighted F1:** {metrics['test_weighted_f1']:.4f}\n",
                "\n",
                "### Comparison\n",
                "| Model | Accuracy | Macro F1 | Weighted F1 |\n",
                "|---|---|---|---|\n",
                "| TF-IDF + Logistic Regression | 0.6605 | 0.6641 | 0.6602 |\n",
                "| MuRIL | {metrics['test_accuracy']:.4f} | {metrics['test_macro_f1']:.4f} | {metrics['test_weighted_f1']:.4f} |\n",
                "\n",
                "### Per-Class Metrics\n",
                "**0 (Negative):** Precision: {metrics['test_prec_0']:.4f} | Recall: {metrics['test_rec_0']:.4f} | F1: {metrics['test_f1_0']:.4f}\n",
                "**1 (Neutral):** Precision: {metrics['test_prec_1']:.4f} | Recall: {metrics['test_rec_1']:.4f} | F1: {metrics['test_f1_1']:.4f}\n",
                "**2 (Positive):** Precision: {metrics['test_prec_2']:.4f} | Recall: {metrics['test_rec_2']:.4f} | F1: {metrics['test_f1_2']:.4f}\n",
                "\n",
                "### Confusion Matrix\n",
                "```\n",
                "{cm[0]}\n",
                "{cm[1]}\n",
                "{cm[2]}\n",
                "```\n",
                "\"\"\"\n",
                "\n",
                "with open(os.path.join(REPORTS_DIR, \"hinglish_muril_results.md\"), \"w\", encoding=\"utf-8\") as f:\n",
                "    f.write(md_content)\n",
                "\n",
                "print(\"Reports generated successfully.\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 10. Inference Smoke Test"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from transformers import pipeline\n",
                "\n",
                "classifier = pipeline(\"text-classification\", model=OUTPUT_DIR, tokenizer=OUTPUT_DIR)\n",
                "\n",
                "test_texts = [\n",
                "    \"ye product bilkul bekar hai\",\n",
                "    \"bahut badhiya service hai inki\"\n",
                "]\n",
                "\n",
                "print(\"Smoke Test Predictions:\")\n",
                "for text in test_texts:\n",
                "    result = classifier(text)[0]\n",
                "    print(f\"'{text}' -> {result['label']} (score: {result['score']:.4f})\")"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.10"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

import os
os.makedirs("notebooks", exist_ok=True)
with open("notebooks/hinglish_muril_finetuning.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)
print("Notebook created successfully.")
