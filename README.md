## LangGraph Chatbot mini projects

**Prerequisite**
You will need to have a Gemini API Key in order to run codes in this repository. you can [get it for free in Google AI Studio](https://aistudio.google.com/app/apikey).

Run below 3 commands:

```bash
$ git clone https://github.com/sophot/langgraph-projects.git
$ cd langgraph-projects
$ cp .env.example .env
```

Then copy and paste the API Key to '.env' file.


**I. Sync dependencies and update lockfile.**

```bash
$ uv sync
```

<br />

**II. Activate an independent environment to work with.**

```bash
$ source .venv/bin/activate
```

<br />

**III. Run**
Go to any project folder to run to interact with the chatbot.

**1. Simple Chatbot [[code]](1_simple_chatbot/main.py)**
- This chatbot doesn't have memory previous conversation. To the LLM, each question is independent from the other.
```bash
$ python 1_simple_chatbot/main.py
```
Output:
<img src="resources/simple_chatbot.png" alt="simple_chatbot_demo_image" style="border: 2px solid #ccc; border-radius: 8px; padding: 4px;" />
