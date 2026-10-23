# AI Workshop Prohire

This repository contains the assignments and projects for the AI Workshop.

## Project Structure

- **`week1-assignment/`**:
  - Task 1: Testing Groq API connection (`task1_test_groq.py`)
  - Task 2: Pydantic User Profile validation (`task2_user_profile.py`)
  - Task 3: Structured JSON extraction with Instructor (`task3_instructor_json.py`)
- **`week3-assignment/`**:
  - **`backend/`**: FastAPI chatbot server with conversation memory and Groq LLM integration.
  - **`frontend/`**: React + Vite chat interface.

## Setup Instructions

### Week 1 Assignment
1. Navigate to `week1-assignment`:
   ```bash
   cd week1-assignment
   ```
2. Create `.env` from `.env.example`:
   ```bash
   cp .env.example .env
   # Add your GROQ_API_KEY
   ```
3. Run the scripts:
   ```bash
   python task1_test_groq.py
   python task2_user_profile.py
   python task3_instructor_json.py
   ```

### Week 3 Assignment

#### Backend (FastAPI)
1. Navigate to backend:
   ```bash
   cd week3-assignment/backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Create `.env` from `.env.example`:
   ```bash
   cp .env.example .env
   # Add your GROQ_API_KEY and optional GROQ_MODEL
   ```
3. Start the server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

#### Frontend (React + Vite)
1. Navigate to frontend:
   ```bash
   cd week3-assignment/frontend
   npm install
   ```
2. Start the dev server:
   ```bash
   npm run dev
   ```
