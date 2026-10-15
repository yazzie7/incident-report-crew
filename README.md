# Incident Report Crew

A minimal CrewAI command-line app. Two agents work sequentially to turn an incident description into a short markdown report.

## How it works

1. **Incident Analyst** extracts facts, assumptions, and the key signal from the incident text (Task 1).
2. **Incident Response Lead** uses Task 1's output (via `context`) to write the final report (Task 2).

The report has four sections: Incident Summary, Suspected Causes, Suggested Next Actions, and Confidence.

Execution is sequential (`Process.sequential`): 2 agents, 2 tasks.

## Setup

```
python -m venv venv
venv\Scripts\Activate.ps1      # Git Bash: source venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env           # then add your OPENAI_API_KEY
```

## Run

```
python main.py "User reports checkout API latency jumped from 200ms to 4s after a deployment, and error rate increased to 12%"
```

## Run with Docker

```
docker build -t incident-crew .
docker run --env-file .env incident-crew "Checkout API latency jumped from 200ms to 4s after a deployment"
```

A real OpenAI API key is required to generate a report. Never commit `.env`.
