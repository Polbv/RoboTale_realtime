from transformers import TextClassificationPipeline, AutoModelForSequenceClassification, AutoTokenizer

# Load the fine-tuned model and tokenizer
model_name = "ahmettasdemir/distilbert-base-uncased-finetuned-emotion"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Create the text classification pipeline
pipeline = TextClassificationPipeline(model=model, tokenizer=tokenizer)

# Example text to classify
text = " “Hi there! How are you today? How old are you, and what kind of stories do you like?"

# Perform text classification
result = pipeline(text)

# Print the predicted label
predicted_label = result[0]['label']
print("Predicted Emotion:", predicted_label)