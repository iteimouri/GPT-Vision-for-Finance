import streamlit as st
import os
import requests
import base64
from PIL import Image

# Function to encode the image from a file path
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to save the uploaded file
def save_uploaded_file(directory, file):
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, file.name)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    return file_path

# Function to send the request to OpenAI API
def get_image_analysis(api_key, base64_image, question):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']


def main():
    st.title("Image Analysis Application")

    
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], key="file_uploader")

    if uploaded_file is not None:
        
        file_path = save_uploaded_file('data', uploaded_file)

        # Encode the uploaded image
        base64_image = encode_image(file_path)

        # Session state to store the base64 encoded image
        if 'base64_image' not in st.session_state or st.session_state['base64_image'] != base64_image:
            st.session_state['base64_image'] = base64_image

        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image.', use_column_width=True)

    question = st.text_input("Enter your question about the image:", key="question_input")

    submit_button = st.button("Submit Question")

    
    api_key = os.getenv("OPENAI_API_KEY")

    if submit_button and question and 'base64_image' in st.session_state and api_key:
        # Get the analysis from OpenAI's API
        response = get_image_analysis(api_key, st.session_state['base64_image'], question)
        st.write(response)
    elif submit_button and not api_key:
        st.error("API key not found. Please set your OpenAI API key.")

if __name__ == "__main__":
    main()
