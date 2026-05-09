# HireLens

## AI-Powered Resume Intelligence System

HireLens is an advanced ATS (Applicant Tracking System) resume scanner that leverages AI to provide comprehensive resume analysis, scoring, and optimization recommendations.

### Features

- **ATS Resume Scoring**: Get a percentage match score for your resume against job descriptions
- **Keyword Matching**: Identify matched and missing keywords from the job posting
- **Skill Gap Analysis**: Analyze matched and missing skills
- **AI-Powered Feedback**: Receive strengths, improvements, and ATS-specific tips

### Tech Stack

- **Frontend**: Streamlit
- **AI Engine**: Groq API (Llama 3.3 70B model)
- **Language**: Python

### Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/hirelens.git
   cd hirelens
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.streamlit/secrets.toml` file
   - Add your Groq API key:
     ```
     GROQ_API_KEY = "your_api_key_here"
     ```

4. Run the application:
   ```
   streamlit run app.py
   ```

### Deployment Guide (Streamlit Cloud)

1. Fork or clone this repository to your GitHub account.

2. Go to [Streamlit Cloud](https://share.streamlit.io/) and sign in with your GitHub account.

3. Click "New app" and select the repository.

4. Set the main file path to `app.py`.

5. Add your secrets in the app settings:
   - Go to "Secrets" and add:
     ```
     GROQ_API_KEY = "your_api_key_here"
     ```

6. Deploy the app.

### Usage

1. Paste your resume text in the "Resume" field.
2. Paste the job description in the "Job Description" field.
3. Click "Analyze Resume" to get the analysis.

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### License

This project is licensed under the MIT License.