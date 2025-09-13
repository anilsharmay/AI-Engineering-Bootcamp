<p align = "center" draggable=”false” ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719" 
     width="200px"
     height="auto"/>
</p>

<h1 align="center" id="heading">Assignment 1: Vibe Checking</h1>


### Main Assignment

In the following assignment, you are required to take the app that you created for the AIE8 challenge (from [this repository](https://github.com/AI-Maker-Space/The-AI-Engineer-Challenge)) and conduct what is known, colloquially, as a "vibe check" on the application. 

You will be required to submit a link to your GitHub, as well as screenshots of the completed "vibe checks" through the provided Google Form!

> NOTE: This will require you to make updates to your personal class repository, instructions on that process can be found [here](https://github.com/AI-Maker-Space/AIE8/tree/main/00_Setting%20Up%20Git)!


#### 🏗️ Activity #1:

Please evaluate your system on the following questions:

1. Explain the concept of object-oriented programming in simple terms to a complete beginner. 
    
    <p align = "center" draggable=”false” ><img src="screenshots/1_Knowledge.png" 
     width="400px"
     height="auto"/>
    </p>

    - Aspect Tested: 
        - Accuracy 
    - Obervations:
        - The responses answered the question accurately using appropriate analogies 
        - The text formatting seems to be broken e.g., markdown formatting

2. Read the following paragraph and provide a concise summary of the key points.
Copied text from the Engadget article about all announcements made at the recent Apple event - [Link](https://www.engadget.com/mobile/smartphones/everything-apple-revealed-at-the-iphone-17-launch-event-iphone-air-iphone-17-pro-airpods-pro-3-and-more-171028663.html)

    <p align = "center" draggable=”false” ><img src="screenshots/2_Summarizing.gif" 
     width="400px"
     height="auto"/>
    </p> 

    - Aspect Tested: 
        - Accuracy
        - If all main details and products are captured
    - Observations:
        - All essential details captured
        - (Surprised!) The MS DOS theme is maintained in the formatting of the response
3. Write a short, imaginative story (100–150 words) about a robot finding friendship in an unexpected place.

    <p align = "center" draggable=”false” ><img src="screenshots/3_Creative Generation.png" 
     width="400px"
     height="auto"/>
    </p>

    - Aspect Tested:
        - Task completion
        - Creativity
    - Observations:
        - Tasks are being completed
        - Acceptable stories
        - The DOS theme is being applied to the response format sporadically.
4. If a store sells apples in packs of 4 and oranges in packs of 3, how many packs of each do I need to buy to get exactly 12 apples and 9 oranges?

    <p align = "center" draggable=”false” ><img src="screenshots/4_Logic.png" 
     width="400px"
     height="auto"/>
    </p>

    - Aspect Tested:
        - Logic and Reasoning abilities
    - Observations:
        - The step  by step reasoning logic is accurate
        - The final answer is accurate
        - Same formatting issues with markup

5. Rewrite the following paragraph in a professional, formal tone: 

Picked up text from a Reddit post about Pixel 10 to be re-written in formal tone - [LINK](https://www.reddit.com/r/GooglePixel/comments/1mw2i0i/pixel_10_seems_to_be_the_right_direction_dont/).

<p align = "center" draggable=”false” ><img src="screenshots/5_Rewrite.gif" 
        width="400px"
        height="auto"/>
    </p>

    - Aspect Tested:
        - Task completion
        - Accuracy
        - Refining the output
    - Observations:
        - The rewriting task was completed with acceptable quality
        - The app doesnt seem to have "memory" to improve on previously generated output
        - The output lost the "first person" tone that was part of the input text

This "vibe check" now serves as a baseline, of sorts, to help understand what holes your application has.

#### A Note on Vibe Checking

>"Vibe checking" is an informal term for cursory unstructured and non-comprehensive evaluation of LLM-powered systems. The idea is to loosely evaluate our system to cover significant and crucial functions where failure would be immediately noticeable and severe.
>
>In essence, it's a first look to ensure your system isn't experiencing catastrophic failure.

#### ❓Question #1:

What are some limitations of vibe checking as an evaluation tool?
##### ✅ Answer:
- Subjective: There aren't any formal requirements, criteria, or constraints. What is acceptable for one might not be true for others. Leaves room for personal interpretation and biases. 
- The final "judgement" is not transparent and cannot be explained to others.
- Does not quantify any metrics around accuracy or performance,
- Prone to weigh aesthetics and presentation more over actual performance. e.g., in the group exercise about explaining OOP concepts, the formatting errors impacted judgement of the app, ignoring the fact that the content was accurate and on point. 
- Hard to establish quality or reproduce the testing without manual, human intervention, as they involve personal "intuition".
- No way to compare different implementations as there are no comparative metrics. 

### 🚧 Advanced Build (OPTIONAL):

Please make adjustments to your application that you believe will improve the vibe check you completed above, then deploy the changes to your Vercel domain [(see these instructions from your Challenge project)](https://github.com/AI-Maker-Space/The-AI-Engineer-Challenge/blob/main/README.md) and redo the above vibe check.

> NOTE: You may reach for improving the model, changing the prompt, or any other method.

#### 🏗️ Activity #1
##### Adjustments Made:
- _describe adjustment(s) here_

##### Results:
1. _Comment here how the change(s) impacted the vibe check of your system_
2. 
3. 
4. 
5.


## Submitting Your Homework
### Main Assignment (Activity #1 only)
Follow these steps to prepare and submit your homework:
1. Pull the latest updates from upstream into the main branch of your AIE8 repo:
    - For your initial repo setup see [00_Setting Up Git/README.md](https://github.com/AI-Maker-Space/AIE8/tree/main/00_Setting%20Up%20Git)
    - To get the latest updates from AI Makerspace into your own AIE8 repo, run the following commands:
    ```
    git checkout main
    git pull upstream main
    git push origin main
    ```
2. **IMPORTANT:** Start Cursor from the `01_Prototyping Best Practices & Vibe Check` folder (you can also use the _File -> Open Folder_ menu option of an existing Cursor window)
3. Create a branch of your `AIE8` repo to track your changes. Example command: `git checkout -b s01-assignment`
4. Edit this `README.md` file (the one in your `AIE8/01_Prototyping Best Practices & Vibe Check` folder)
5. Perform a "Vibe check" evaluation your AI-Engineering-Challenge system using the five questions provided above 
6. For each Activity question:
    - Define the “Aspect Tested”
    - Comment on how your system performed on it. 
7. Provide an answer to `❓Question #1:` after the `✅ Answer:` prompt
8. Add, commit and push your modified `README.md` to your origin repository.

>(NOTE: You should not merge the new document into origin's main branch. This will spare you from update challenges for each future session.)

When submitting your homework, provide the GitHub URL to the tracking branch (for example: `s01-assignment`) you created on your AIE8 repo.

### The Advanced Build:
1. Follow all of the steps (Steps 1 - 8) of the Main Assignment above
2. Document what you changed and the results you saw in the `Adjustments Made:` and `Results:` sections of the Advanced Build's Assignment #1
3. Add, commit and push your additional modifications to this `README.md` file to your origin repository.

When submitting your homework, provide the following on the form:
+ The GitHub URL to the tracking branch (for example: `s01-assignment`) you created on your AIE8 repo.
+ The public Vercel URL to your updated Challenge project on your AIE8 repo.
