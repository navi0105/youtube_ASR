from transformers import AutoTokenizer, AutoModelForTokenClassification, TokenClassificationPipeline

def sentence_segment(texts, model_dir):
    model = AutoModelForTokenClassification.from_pretrained(model_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    pipeline = TokenClassificationPipeline(model=model, tokenizer=tokenizer)

    result = ""
    cls_output = pipeline(texts)
    for text, output in zip(texts, cls_output):
        char_idx = 0
        text_len = len(text)
        for char, out in zip(text, output):
            result += char
            char_idx += 1
            label = int(out["entity"][-1])
            if label == 1 and char_idx < text_len:
                result += '\n'
        result += '\n'

    return result
        