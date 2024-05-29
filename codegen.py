from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import json
import google.generativeai as genai
import re
# Load environment variables from a .env file
load_dotenv()

# Configure generative AI with API key
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Create a Flask app
app = Flask(__name__)

# Define a route for generating content


@app.route('/generate', methods=['POST'])
def generate_content():
    # Get user inputs from request JSON
    inputParams = request.json.get('inputParams')
    outputParams = request.json.get('outputParams')
    description = request.json.get('description')

    if inputParams and outputParams and description:
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = '''You are building an API for a web application using Node.js, Express.js, and MongoDB. Your task is to generate the code for the route, model, and controller files based on the provided input parameters, output parameters, and a description of the endpoint. 
            Description: {description}
            Input Parameters: {inputParams}
            Output Parameters: {outputParams}
            Instructions:
                Based on the provided information, generate the code for the route, model, and controller files. The route file should contain the route definition, the model file should define the schema for the user, and the controller file should implement the functionality to update user information.
            Return the output in 3 variables : model, route and controller
            The output format should strictly be in a json format, given below
            {"route":route_content, "controller":controller_content, "model":model_content}
            Also dont give the output in markdown format, it should be raw
            '''
            response = model.generate_content(prompt)
            parsed_data = json.loads(response.text)

            # Extract route, controller, and model
            route_content = parsed_data.get('route')
            controller_content = parsed_data.get('controller')
            model_content = parsed_data.get('model')

            return ({"route": route_content, "model": model_content, "controller": controller_content})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'One or more inputs missing'}), 400


if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)
