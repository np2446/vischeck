# VisCheck - File Upload and AI Analysis App

VisCheck is a comprehensive web application designed for users to upload chart images and CSV datasets, process them via an AI backend, and receive dynamically generated insights. The project leverages modern technologies with a focus on usability, aesthetics, and performance, making it suitable for enterprise-level applications.

---

## Features

### Frontend
- **File Upload with Validation**:
  - Supports uploading of chart images, chart data (CSV), and full datasets (CSV).
  - Provides real-time confirmation of uploaded files.
  - Allows users to remove uploaded files and re-upload as needed.
- **Dynamic AI Responses**:
  - Displays AI-generated insights using a simulated typing animation.
  - Responses are rendered in Markdown with clean styling and left alignment.
- **User Feedback**:
  - Shows a progress bar while awaiting AI responses.
  - Displays error messages for failed uploads or processing issues.
- **Responsive Design**:
  - Built using Material-UI with Microsoft Fluent Design principles.
  - Fully compatible with devices of all sizes.

### Backend
- **AI-Powered Processing**:
  - Processes uploaded chart images and CSV data to generate insightful responses.
  - Utilizes `analysis.py` for data parsing and analysis.
- **RESTful API**:
  - Built with Flask to handle file uploads and interact with the AI processing layer.

---

## Technology Stack

### Frontend
- **React**: Framework for building the user interface.
- **Material-UI**: Provides a modern and responsive design with Microsoft's Fluent Design system.
- **PapaParse**: For parsing CSV files on the client-side.
- **Axios**: Handles HTTP requests to the Flask backend.
- **React Markdown**: Renders AI responses in Markdown format.
- **Custom Typing Animation**: Simulates real-time AI response streaming.

### Backend
- **Flask**: Lightweight web framework for the backend.
- **Python**: Core programming language for data processing and analysis.
- **Custom Analysis Module**: The `analysis.py` script contains logic for processing CSV data and generating AI insights.

---

## Installation

### Prerequisites
- Node.js (for running the frontend)
- Python 3.x (for running the backend)
- npm (for managing JavaScript dependencies)

### Steps

1. **Clone the Repository**:
2. 
   ```bash
   git clone https://github.com/np2446/vischeck.git
   cd vischeck

3. **Setup the Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   touch .env
   nano .env # create env vars `OPENAI_KEY` and `PASSWORD`
   python app.py

4. **Setup the Frontend**:
   ```bash
    cd ../frontend
    npm install
    npm start

5. **Access the Application**:
    - Open `http://localhost:3000` in your browser to use the application.\

---

## File Structure
- **frontend/**: Contains React code for the user interface.
  - `FileUpload.js`: Main component for file uploads and interactions.
- **backend/**:
  - `app.py`: Flask API for handling requests.
  - `analysis.py`: Logic for processing CSV data and images.
- **README.md**: Project documentation.

---

## Usage
1. Upload a chart image and relevant CSV files (chart data and full dataset).
2. Click "Submit" to process the data via the AI backend.
3. View the dynamically generated response with Markdown formatting.

---

## Dependencies

### Frontend
- React
- Material-UI
- Axios
- React-Markdown

### Backend
- Flask
- Pandas

---

## Contributing
Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request.

---


