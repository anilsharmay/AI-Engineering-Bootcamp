<p align = "center" draggable=”false” ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719" 
     width="200px"
     height="auto"/>
</p>

## <h1 align="center" id="heading">Session 18: On Prem Agents</h1>

### [Quicklinks](https://github.com/AI-Maker-Space/AIE7/00_AIM_Quicklinks)

| 🤓 Pre-work | 📰 Session Sheet | ⏺️ Recording     | 🖼️ Slides        | 👨‍💻 Repo         | 📝 Homework      | 📁 Feedback       |
|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|

# Build 🏗️

First, let's pull and run our DeepSeek-R1 distilled model through Ollama.

### Mac

1. Download the Ollama app for Mac [here](https://ollama.com/download).

2. Pull a local LLM from [Ollama](https://ollama.com/search). As an [example](https://ollama.com/library/deepseek-r1:8b):
```bash
ollama pull deepseek-r1:8b
```

### Windows

1. Download the Ollama app for Windows [here](https://ollama.com/download).

2. Pull a local LLM from [Ollama](https://ollama.com/search). As an [example](https://ollama.com/library/deepseek-r1:8b):
```powershell
ollama pull deepseek-r1:8b
```

### Testing

Once you'd completed that task - please run the `test_ollama.ipynb` notebook to confirm your Ollama instance is working correctly. 

### Ollama Deep Research

Once you've completed that step - please clone the [Local Deep Research repository](git@github.com:langchain-ai/local-deep-researcher.git) (outside of the AIE8 repository). 

```bash
cd ~
git clone git@github.com:langchain-ai/local-deep-researcher.git
```

Then you can follow the instructions in that README.md to launch the application. 

### Assignment: 

Add a local RAG instance powered by QDrant into the flow of the existing Agent. 

First, you'll need to: 

```bash
ollama pull mxbai-embed-large
```

Then you will need to: 

1) Launch [QDrant through Docker](https://qdrant.tech/documentation/quickstart/)
2) Create a VectorStore leveraging QDrant as a backend (you can use [this notebook](./qdrant_setup.ipynb) as inspiration)
3) Add a new node in the Agent Graph
4) Modify the graph to accomodate your new node. 




# Ship 🚢

- 5min. Loom Video

# Share 🚀
- Walk through your app and explain what you've completed in the Loom video
- Make a social media post about your final application and tag @AIMakerspace
- Share 3 lessons learned
- Share 3 lessons not learned

# Submitting You Homework [OPTIONAL]

## Main Homework Assignment

Follow these steps to prepare and submit your homework assignment:
1. Follow the instructions in this `README.md`for setting up your local environment to function as an "On-Prem" AI environment
2. Complete the `Assignment` detailed in this `README.md`
3. In order to push your completed assignment to your own GitHub account you will need to:
    + Create a new, completely empty repository on your GitHub account
    + Rename the existing `origin` git remote on your local system (`upstream` is a good name for it)
    + Add a git remote on your local system named `origin` which points to the empty repository you created on your GitHub account
    + Push your codebase to your repository (`git push origin HEAD` should do this for you)
5. Record a Loom video which:
    + Demonstrates your fully on-prem AI application
    + Reviews what you have learned from this session
6. Make sure to include all of the following on your Homework Submission Form:
    + The GitHub URL to the GitHub repository you created for the  `local-deep-researcher` repository you cloned from LangSmith during the assignment
    + The URL to your Loom Video
    + Your Three Lessons Learned/Not Yet Learned
    + The URLs to any social media posts (LinkedIn, X, Discord, etc.) ⬅️ _easy Extra Credit points!_
