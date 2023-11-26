from flask import Flask, render_template, request, jsonify
import requests
import base64
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import math
app = Flask(__name__)


API_URL = "https://xdwvg9no7pefghrn.us-east-1.aws.endpoints.huggingface.cloud"
API_KEY = "VknySbLLTUjbxXAXCjyfaFIPwUTCeRXbFSOjwRiCxsxFyhbnGjSFalPKrpvvDAaPVzWEevPljilLVDBiTzfIbWFdxOkYJxnOPoHhkkVGzAknaOulWggusSFewzpqsNWM"



def set_panel_text(base64_image, panel_text, x, y, scale, max_chars_per_line=20):
    image_data = base64.b64decode(base64_image)
    image = Image.open(BytesIO(image_data))

    # Create a drawing object
    draw = ImageDraw.Draw(image)

    # Load a default font
    font = ImageFont.load_default()

    # Calculate the text size
    text_width, text_height = draw.textsize(panel_text, font=font)

    # Set a constant padding for the bubble
    bubble_padding = 5
    # Split the panel text into lines based on the character limit
    lines = [panel_text[i:i + max_chars_per_line] for i in range(0, len(panel_text), max_chars_per_line)]


    # Calculate the size of the elliptical speech bubble to fit the text
    bubble_radius_x = text_width / 2 + bubble_padding  # Adjust the padding as needed
    bubble_radius_y =text_height / 2
    bubble_radius_y=bubble_radius_y*(len(lines)+2)
    # Calculate the size of the elliptical speech bubble to fit the text
    bubble_radius_x = (text_width / 2) * 0.0001
     # Adjust the padding as needed

    # Calculate the starting position for the text inside the bubble
    text_position = (x - text_width / 2, y - text_height / 2)

    # Calculate the horizontal shift needed to center the bubble around the text
    horizontal_shift = (text_width / 2) - (bubble_radius_x - bubble_padding)

    # Draw the elliptical speech bubble
    draw.ellipse([(text_position[0] - bubble_radius_x + horizontal_shift, text_position[1] - bubble_radius_y),
                  (text_position[0] + text_width + bubble_radius_x + horizontal_shift, text_position[1] + text_height + bubble_radius_y)],
                 fill="white", outline="black")

    
    # Add text to the speech bubble, centering within the elliptical bubble
    for i, line in enumerate(lines):
        line_width, line_height = draw.textsize(line, font=font)
        line_position = (x - line_width / 2 + horizontal_shift, y - text_height / 2 + i * line_height)
        draw.text(line_position, line, font=font, fill="black")

    # Save the modified image to BytesIO
    output_buffer = BytesIO()
    image.save(output_buffer, format="PNG")
    output_data = output_buffer.getvalue()

    # Encode the modified image to base64
    modified_image_base64 = base64.b64encode(output_data).decode('utf-8')

    return modified_image_base64


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_comic', methods=['POST'])
def generate_comic():
    data = request.json

    if 'inputs' not in data or len(data['inputs']) != 10:
        return jsonify({'error': 'Invalid input data'}), 400

    images = []

    for panel_data in data['inputs']:
        panel_text = panel_data.get('text', '')
        bubble_text = panel_data.get('bubbleText', '')

        x = 50
        y = 50
        scale = 1.0

        headers = {
            "Accept": "image/png",
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(API_URL, headers=headers, json={"inputs": f"{bubble_text}<br/>{panel_text}"})
        
        if response.status_code != 200:
            return jsonify({'error': 'Failed to generate comic'}), response.status_code

        image_base64 = base64.b64encode(response.content).decode('utf-8')

        # Add panel text to the generated image
        modified_image_base64 = set_panel_text(image_base64, panel_text, x, y, scale)

        images.append(modified_image_base64)

    # Return only the panel images
    return jsonify({'images': images})

if __name__ == '__main__':
    app.run(debug=True)