**# AI Health Prediction System**



**## Project Overview**



**The \*\*AI Health Prediction System\*\* is a web-based application that uses machine learning and image analysis to support preliminary health assessments. It combines symptom-based disease prediction with chest X-ray image analysis for pneumonia detection and severity estimation.**



**The application provides a simple interface where users can select symptoms or upload a chest X-ray image and view the model's prediction.**



**## Key Features**



**- \*\*Symptom-Based Disease Prediction:\*\* Allows users to select symptoms and receive a predicted health condition based on the implemented prediction model.**

**- \*\*Pneumonia Detection:\*\* Analyzes uploaded chest X-ray images to predict whether pneumonia may be present.**

**- \*\*Severity Estimation:\*\* Provides a predicted pneumonia severity level based on the image model's output.**

**- \*\*Web Interface:\*\* Provides a user-friendly frontend built with HTML and CSS.**

**- \*\*Flask Backend:\*\* Handles application routes, user inputs, image processing, and model integration.**



**## Technologies Used**



**- \*\*Programming Language:\*\* Python**

**- \*\*Backend:\*\* Flask**

**- \*\*Frontend:\*\* HTML, CSS**

**- \*\*Machine Learning:\*\* TensorFlow / CNN-based image classification**

**- \*\*Image Processing:\*\* Pillow, NumPy**

**- \*\*Additional Libraries:\*\* scikit-learn**



**## System Workflow**



**### 1. Symptom-Based Prediction**

**1. The user selects symptoms through the web interface.**

**2. The application processes the selected symptoms.**

**3. The trained prediction model generates a predicted condition.**

**4. The result is displayed on the application.**



**### 2. Pneumonia Detection**

**1. The user uploads a chest X-ray image.**

**2. The application processes the image into the format expected by the model.**

**3. The image classification model analyzes the image.**

**4. The application displays the predicted pneumonia status and, where supported, the estimated severity.**



**## Project Objectives**



**- Explore how machine learning can be integrated into a web application.**

**- Build separate workflows for symptom-based prediction and medical image classification.**

**- Connect trained models to a Flask backend.**

**- Present model predictions through an accessible web interface.**

**- Understand the practical challenges of preprocessing input data and deploying machine learning models.**



**## Skills Demonstrated**



**- Python programming**

**- Flask application development**

**- Machine learning model integration**

**- CNN-based image classification**

**- Image preprocessing**

**- HTML and CSS**

**- Model inference and prediction display**

**- Connecting frontend inputs with backend logic**



**## How to Run**



**1. Clone or download this repository.**

**2. Create and activate a Python virtual environment.**

**3. Install the dependencies listed in the project's `requirements.txt` file.**

**4. Ensure the trained model files and any required datasets are placed in their expected locations.**

**5. Configure the application settings and required environment variables.**

**6. Start the Flask application using the project's entry-point**

