# -----------------------------------------------------------------------------------------------------------------

from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

# -----------------------------------------------------------------------------------------------------------------

def load_captioning_model() -> tuple[BlipProcessor, BlipForConditionalGeneration]:
    '''
    Loads the input processor and the model to generate image descriptions
    '''
    model = 'Salesforce/blip-image-captioning-large'
    processor = BlipProcessor.from_pretrained(model, use_fast=True)
    print('[AGENT] Image processor loaded')
    captioner = BlipForConditionalGeneration.from_pretrained(model)
    print('[AGENT] Image captioner loaded')
    return processor, captioner

# -----------------------------------------------------------------------------------------------------------------

def generate_caption(processor : BlipProcessor, captioner : BlipForConditionalGeneration, image : Image) -> str:
    '''
    Generates a caption for the image using the BLIP model
    '''
    text = 'a photograph of'
    inputs = processor(image, text, return_tensors="pt")
    temperature = 0.3
    top_p = 0.9
    outputs = captioner.generate(
        **inputs,
        do_sample=True,
        temperature=temperature,
        top_p=top_p,
        max_new_tokens=20,
        repetition_penalty=1.2
    )
    caption = processor.decode(outputs[0], skip_special_tokens=True)
    caption = caption.removeprefix('a photograph of ')
    return caption

# -----------------------------------------------------------------------------------------------------------------