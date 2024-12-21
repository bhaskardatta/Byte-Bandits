import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf

def audio_generator(prompt = "Hey!!! Pass an input to generate audio"):
    device = "cpu"

    model = ParlerTTSForConditionalGeneration.from_pretrained("parler-tts/parler-tts-mini-multilingual-v1.1").to(device)
    tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-mini-multilingual-v1.1")
    description_tokenizer = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)

    # prompt = "A female speaker delivers fully excited and realistic speech with a moderate speed and pitch. The recording is of very high quality, with the speaker's voice sounding clear and very close up"
    description = "A female delivers speech in a happy mood and realistic speech with a moderate speed and pitch. The recording is of very high quality, with the speaker's voice sounding clear and very close up."

    # Create input_ids and attention_masks for description
    description_inputs = description_tokenizer(description, return_tensors="pt")
    input_ids = description_inputs.input_ids.to(device)
    description_attention_mask = description_inputs.attention_mask.to(device)

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
    sf.write("parler_tts_out.wav", audio_arr, model.config.sampling_rate)

audio_generator('''empowerment is authority it is a sign permission''')