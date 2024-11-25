import streamlit as st
from PIL import Image
import pytesseract
from gtts import gTTS
from transformers import BlipProcessor, BlipForConditionalGeneration
import os

# Load the BLIP model for scene description
@st.cache_resource
def load_model():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    return processor, model

processor, model = load_model()

# Streamlit app layout
st.title("AI-Powered Assistance for Visually Impaired")
st.header("Upload an Image for Text-to-Speech and Personalized Assistance")

uploaded_file = st.file_uploader("Choose an image", type=["jpg", "png", "jpeg"])
if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Text-to-Speech (Extract Text from Image)
    st.subheader("Text-to-Speech Conversion")
    extracted_text = pytesseract.image_to_string(image)
    if extracted_text:
        st.write("Extracted Text: ", extracted_text)
        
        # Generate audio file for the extracted text
        tts = gTTS(extracted_text)
        tts.save("extracted_text.mp3")
        st.audio("extracted_text.mp3", format="audio/mp3")
    else:
        st.write("No text detected in the image.")

    # Scene Description using BLIP (Personalized Assistance)
    st.subheader("Scene Description")
    inputs = processor(images=image, return_tensors="pt")
    output = model.generate(**inputs)
    description = processor.decode(output[0], skip_special_tokens=True)

    # Show the scene description
    st.write("Description of the scene: ", description)

    # Personalized guidance based on scene description
    st.subheader("Personalized Guidance")
    if "wallet" in description.lower():
        guidance = "This looks like your wallet. Keep it safe!"
    elif "phone" in description.lower():
        guidance = "Your phone is on the table. Do you need to use it?"
    elif "book" in description.lower():
        guidance = "This seems to be a book. Would you like to read it?"
    elif "bottle" in description.lower():
        guidance = "This looks like a water bottle. Don't forget to hydrate!"
    else:
        guidance = "No specific guidance detected for the scene."

    st.write(guidance)
    
    # Generate audio file for the guidance
    guidance_tts = gTTS(guidance)
    guidance_tts.save("guidance.mp3")
    st.audio("guidance.mp3", format="audio/mp3")
