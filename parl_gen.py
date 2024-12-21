import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf

def parl_loader():
    device = "cpu"

    model = ParlerTTSForConditionalGeneration.from_pretrained(
        "parler-tts/parler-tts-mini-multilingual-v1.1", 
        attn_implementation="eager").to(device)
    print(model.config)
    tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-mini-multilingual-v1.1")
    # print(tokenizer.get_vocab())
    description_tokenizer = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)

    return model, tokenizer, description_tokenizer

def describe_speaker(speaker="host", tone="happy", device="cpu"):
        # prompt = "A female speaker delivers fully excited and realistic speech with a moderate speed and pitch. The recording is of very high quality, with the speaker's voice sounding clear and very close up"
    description = f"A {speaker} delivers speech in slight {tone} tone and realistic speech with a moderate speed and pitch. The recording is of very high quality, with the speaker's voice sounding clear and very close up."

    # Create input_ids and attention_masks for description
    description_inputs = description_tokenizer(description, return_tensors="pt")
    input_ids = description_inputs.input_ids.to(device)
    description_attention_mask = description_inputs.attention_mask.to(device)
    
    return input_ids, description_attention_mask

def audio_generator(model, tokenizer, input_ids, description_attention_mask, device="cpu", prompt = "Hey!!! Pass an input to generate audio", file="default", speaker="female",tone="happy"):
    # Create input_ids and attention_masks for prompt
    prompt_inputs = tokenizer(prompt, return_tensors="pt")
    prompt_input_ids = prompt_inputs.input_ids.to(device)
    prompt_attention_mask = prompt_inputs.attention_mask.to(device)

    # Generate audio with attention masks
    generation = model.generate(
        input_ids=input_ids, 
        attention_mask=description_attention_mask,
        prompt_input_ids=prompt_input_ids,
        prompt_attention_mask=prompt_attention_mask
    )

    # Convert and save audio
    audio_arr = generation.cpu().numpy().squeeze()
    sf.write(f"audio/{file}.wav", audio_arr, model.config.sampling_rate)
model, tokenizer, description_tokenizer = parl_loader()
input_ids, description_attention_mask = describe_speaker("host")

# audio_generator(model=model, tokenizer=tokenizer, description_tokenizer=description_tokenizer, prompt='''It's a process of getting stronger, more confident, and more engaged.''', speaker="Sarah")