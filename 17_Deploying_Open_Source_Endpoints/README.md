
<p align = "center" draggable=”false” ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719" 
     width="200px"
     height="auto"/>
</p>

## <h1 align="center" id="heading">Session 17: Deploying Open Source Endpoints</h1>

| 📰 Session Sheet | ⏺️ Recording     | 🖼️ Slides        | 👨‍💻 Repo         | 📝 Homework      | 📁 Feedback       |
|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|
| [Session 17: Deploying Open-Source Endpoints](https://www.notion.so/Session-17-Deploying-Open-Source-Endpoints-26acd547af3d803c9ca1f809b2d24a15) |[Recording!](https://us02web.zoom.us/rec/share/5p0fdcNcY61A9W0CqkBgGDHZP4CFgaArrQuV5odXndLs6VnJXx_JaYnQyNeTo1Nv.lgKhnecFkff3okzf) (JF5JkZk@) | [Session 17 Slides](https://www.canva.com/design/DAG3xfshte8/05rU_he3VcR7dz4r_2ky2Q/edit?utm_content=DAG3xfshte8&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton) | You are here! | [Session 17 Assignment: Endpoints](https://forms.gle/8F3D6dSFMxzVdtsJ8) | [AIE8 Feedback 11/4](https://forms.gle/EnczDh7hbwud4qSp9)

**⚠️!!! PLEASE BE SURE TO SHUTDOWN YOUR DEDICATED ENDPOINT ON TOGETHER AI WHEN YOU'RE FINISHED YOUR ASSIGNMENT !!!⚠️**

# Build 🏗️

In today's assignment, we'll be creating Together AI endpoints, and then building an Agentic RAG application.

- 🤝 Breakout Room #1
    - Set-up Open Source Endpoint (Instructions [here](./ENDPOINT_SETUP.md)) ((This process may take 15-20min.))
    - Test Endpoint and Embeddings with the `endpoint_slammer.ipynb` notebook.

- 🤝 Breakout Room #2
    - Use the Open Source Endpoints to build an Agentic RAG LangGraph application (use Session 14/15 code to get started)

       > NOTE: You should look toward: [ChatTogether](https://python.langchain.com/docs/integrations/chat/together/), and [TogetherEmbeddings](https://python.langchain.com/docs/integrations/text_embedding/together/) for help on how to build these endpoints into your application!

      > NOTE: You will have to add libraries to your `pyproject.toml` with `uv add`. You could also bring in a previous environment.

# Ship 🚢

The completed notebook and your RAG app/notebook!

<details>
<summary>🚧 Advanced Build 🚧 (OPTIONAL - <i>open this section for the requirements</i>)</summary>

Use RAGAS to evaluate your open-source powered app against an OpenAI `gpt-4.1-mini` powered Agentic RAG app.
</details>

### Deliverables

- A short Loom of either:
  - the notebook and the RAG application you built for the Main Homework Assignment; or
  - the notebook you created for the Advanced Build

# Share 🚀

Make a social media post about your final application!

### Deliverables

- Make a post on any social media platform about what you built!

Here's a template to get you started:

```
🚀 Exciting News! 🚀

I am thrilled to announce that I have just built and shipped an Agentic RAG application powered by open-source endpoints! 🎉🤖

🔍 Three Key Takeaways:
1️⃣ 
2️⃣ 
3️⃣ 

Let's continue pushing the boundaries of what's possible in the world of AI and question-answering. Here's to many more innovations! 🚀
Shout out to @AIMakerspace !

#LangChain #QuestionAnswering #RetrievalAugmented #Innovation #AI #TechMilestone

Feel free to reach out if you're curious or would like to collaborate on similar projects! 🤝🔥
```

# Submitting You Homework [OPTIONAL]

## Main Homework Assignment

Follow these steps to prepare and submit your homework assignment:
1. Create a branch of your `AIE8` repo to track your changes. Example command: `git switch -c s17-assignment`
2. Follow the instructions in `ENDPOINT_SETUP.md` 
> _**NOTE: Make sure you select an Auto-shutdown!**_
3. Replace both `model` values in `endpoint_slammer.ipynb` with the `gpt-oss` endpoint you created in Step 2 
4. Run the code cells in `endpoint_slammer.ipynb`
5. Respond to the question at the end of the `ENDPOINT_SETUP.md`
6. Build a sample RAG
7. Commit, and push your changes to your `origin` repository. _NOTE: Do not merge them into your main branch_
8. Record a Loom video reviewing what you have learned from this session
9. Make sure to include all of the following on your Homework Submission Form:
    + The GitHub URL to the `17_Deploying_Open_Source_Endpoints` folder _on your assignment branch (not main)_
    + The URL to your Loom Video
    + Your Three Lessons Learned/Not Yet Learned
    + The URLs to any social media posts (LinkedIn, X, Discord, etc.) ⬅️ _easy Extra Credit points!_

**⚠️!!! PLEASE BE SURE TO SHUTDOWN YOUR DEDICATED ENDPOINT ON TOGETHER AI WHEN YOU'RE FINISHED YOUR ASSIGNMENT !!!⚠️**

## OPTIONAL: Advanced Build Assignment
<details>
<summary><i>(Open this section for the requirements)</i></summary>

Follow these steps to prepare and submit your homework assignment:
1. Create a branch of your `AIE8` repo to track your changes. Example command: `git switch -c s17-assignment`
2. Complete and evaluate your open-source powered app against an OpenAI `gpt-4.1-mini` powered Agentic RAG app using RAGAS.
3. Commit and push your application code to your `origin` repository. _NOTE: Do not merge it into your main branch_
4. Record a Loom video reviewing the results
5. Make sure to include all of the following on your Homework Submission Form:
    + The GitHub URL to the `17_Deploying_Open_Source_Endpoints` folder _on your assignment branch_
    + The URL to your Loom Video
    + Your Three Lessons Learned/Not Yet Learned
    + The URLs to any social media posts (LinkedIn, X, Discord, etc.) ⬅️ _easy Extra Credit points!_
</details>
