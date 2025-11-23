# ResearchMate: AI-Powered Neuroscience Paper Summarizer

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B)
![Gemini API](https://img.shields.io/badge/AI-Google%20Gemini%202.0-8E75B2)
![Status](https://img.shields.io/badge/Status-Beta-orange)

**ResearchMate** is a streamlined web application designed to accelerate academic research. By leveraging Google's **Gemini 2.0 Flash AI**, it processes scientific papers (PDFs) and extracts structured, actionable insights, allowing researchers to understand key findings.

---
## Demo

![ResearchMate Dashboard Demo](assets/demo_dashboard.png)
![ResearchMate Dashboard Demo](assets/demo_dashboard1.png)


## Tech Stack

*   **Frontend:** [Streamlit](https://streamlit.io/) (Python framework for data apps).
*   **AI Model:** [Google Gemini 2.0 Flash](https://deepmind.google/technologies/gemini/) via `google-genai` SDK.
*   **PDF Processing:** PyMuPDF (`fitz`).
*   **Environment Management:** `python-dotenv`.

## Installation & Setup

Follow these steps to run the project locally:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/biancanegribello/researchmate.git
    cd researchmate
    ```

2.  **Create a virtual environment (Optional but recommended):**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    *   Create a `.env` file in the root directory.
    *   Add your Google Gemini API Key:
    ```text
    GEMINI_API_KEY=your_api_key_here
    ```

5.  **Run the application:**
    ```bash
    streamlit run main.py
    ```
