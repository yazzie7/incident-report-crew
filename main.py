import argparse
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process

load_dotenv()  # reads .env into environment variables (OPENAI_API_KEY, etc.)


def parse_args():
    parser = argparse.ArgumentParser(description="Generate an incident report using two CrewAI agents.")
    parser.add_argument("incident", type=str, help="Description of the incident, in quotes.")
    return parser.parse_args()


# --- Agent 1: reads the raw incident and extracts structured signal ---
analyst_agent = Agent(
    role="Incident Analyst",
    goal="Extract the key facts, assumptions, and signal from a raw incident description.",
    backstory=(
        "You are a senior SRE who has triaged hundreds of production incidents. "
        "You are precise, skeptical of vague claims, and always separate confirmed "
        "facts from assumptions before drawing conclusions."
    ),
    allow_delegation=False,
    verbose=True,
)

# --- Task 1: assigned to the Analyst Agent ---
analysis_task = Task(
    description=(
        "Analyze the following incident report and extract:\n"
        "1. Confirmed facts (only what is explicitly stated)\n"
        "2. Assumptions or unknowns (things implied but not confirmed)\n"
        "3. The key signal most likely to point toward the root cause\n\n"
        "Incident: {incident}"
    ),
    expected_output=(
        "A structured breakdown with three labeled sections: Facts, Assumptions, Key Signal."
    ),
    agent=analyst_agent,
)

# --- Agent 2: turns the analysis into a decision-ready report ---
action_agent = Agent(
    role="Incident Response Lead",
    goal="Turn an incident analysis into a concise, actionable markdown report for the on-call team.",
    backstory=(
        "You are an incident commander who has run dozens of postmortems. "
        "You write tersely, prioritize the next 3 concrete actions a team should "
        "take, and are honest about your confidence level given the evidence available."
    ),
    allow_delegation=False,
    verbose=True,
)

# --- Task 2: assigned to the Action Agent, consumes Task 1's output via `context` ---
action_task = Task(
    description=(
        "Using the Analyst's breakdown of facts, assumptions, and key signal, write the "
        "final incident report in markdown with exactly these sections:\n"
        "## Incident Summary\n(3-5 lines)\n"
        "## Suspected Causes\n(3 bullets)\n"
        "## Suggested Next Actions\n(3 bullets)\n"
        "## Confidence\n(Low, Medium, or High, with a one-line reason)"
    ),
    expected_output=(
        "Raw markdown (no code fences, no preamble) in exactly this shape:\n\n"
        "## Incident Summary\n"
        "<3-5 lines>\n\n"
        "## Suspected Causes\n"
        "- <cause 1>\n- <cause 2>\n- <cause 3>\n\n"
        "## Suggested Next Actions\n"
        "- <action 1>\n- <action 2>\n- <action 3>\n\n"
        "## Confidence\n"
        "<Low|Medium|High> - <one-line reason>"
    ),
    agent=action_agent,
    context=[analysis_task],  # <-- this is what feeds Task 1's output into Task 2
)

# --- Crew: ties the agents + tasks together, runs them in order ---
crew = Crew(
    agents=[analyst_agent, action_agent],
    tasks=[analysis_task, action_task],
    process=Process.sequential,
    verbose=True,
)


def main():
    args = parse_args()
    result = crew.kickoff(inputs={"incident": args.incident})
    print("\n--- INCIDENT REPORT ---\n")
    print(result.raw)  # .raw is the final task's plain text/markdown output


if __name__ == "__main__":
    main()