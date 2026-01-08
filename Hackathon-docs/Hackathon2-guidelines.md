HACKATHON II GUIDELINES

**PHASE I**

**Important Details to look into when completing:**

1) No manual coding is allowed so make sure to use *Spec-kit* and *Claude Code*.  
2) Implement all 5 basic Level features \[Add, Delete, Update, View, Mark Complete\]  
3) Tech Stack \---- UV, Python 3.13+, Claude Code and Spec-kit Plus.  
4) Follow the correct order of commands \---- Specify, Plan, Tasks, Implement.

\[If you have not installed Spec-kit plus yet, run the following command to install and then start from step 1 to initialize the folder:

pip install specifyplus  
\]

**Step \# 1:**

* Initialize Spec-Kit in your required folder using:  
    
  sp init .

**Step \# 2:**

* Write global constitution for the whole To-Do requirements (You may refer to any LLM for generating your prompts)  
* *Example Prompt:*  
    
  /sp.constitution Create a single global constitution for the entire "Evolution of Todo" project  
  covering Phase I through Phase V.  
    
  This constitution must define:  
    
  1\. Spec-Driven Development as mandatory  
     \- No agent may write code without approved specs and tasks  
     \- All work must follow: Constitution → Specs → Plan → Tasks → Implement  
    
  2\. Agent Behavior Rules  
     \- No manual coding by humans  
     \- No feature invention  
     \- No deviation from approved specifications  
     \- Refinement must occur at spec level, not code level  
    
  3\. Phase Governance  
     \- Each phase is strictly scoped by its specification  
     \- Future-phase features must never leak into earlier phases  
     \- Architecture may evolve only through updated specs and plans  
    
  4\. Technology Constraints  
     \- Python for backend  
     \- Next.js for frontend (later phases)  
     \- FastAPI, SQLModel, Neon DB  
     \- OpenAI Agents SDK, MCP  
     \- Docker, Kubernetes, Kafka, Dapr (later phases)  
    
  5\. Quality Principles  
     \- Clean architecture  
     \- Stateless services where required  
     \- Clear separation of concerns  
     \- Cloud-native readiness  
    
  This constitution must remain stable across all phases  
  and act as the supreme governing document for all agents.

**Step \# 3:**

* Now write a prompt to make specs.  
* Specs → WHAT  
* *Example Prompt:*  
    
  /sp.specify Create the Phase I specification for the "Evolution of Todo" project.  
    
  Phase I Scope:  
  \- In-memory Python console application  
  \- Single user  
  \- No persistence beyond runtime  
    
  Required Features (Basic Level ONLY):  
  1\. Add Task  
  2\. View Task List  
  3\. Update Task  
  4\. Delete Task  
  5\. Mark Task Complete / Incomplete  
    
  Specification must include:  
  \- Clear user stories for each feature  
  \- Task data model (fields and constraints)  
  \- CLI interaction flow (menu-based)  
  \- Acceptance criteria for each feature  
  \- Error cases (invalid ID, empty task list)  
    
  Strict Constraints:  
  \- No databases  
  \- No files  
  \- No authentication  
  \- No web or API concepts  
  \- No advanced or intermediate features  
  \- No references to future phases  
    
  This specification must comply with the global constitution  
  and fully define WHAT Phase I must deliver.

**Step \# 4:**

* Now give a prompt for planning.  
* Plan → HOW  
* *Example Prompt:*  
    
  /sp.plan Create the Phase I technical plan for the Todo in-memory Python console application.  
    
  The plan must be derived strictly from the Phase I specification and global constitution.  
    
  Include:  
  1\. High-level application structure (single Python program)  
  2\. In-memory data structures to store tasks  
  3\. Task identification strategy (ID generation)  
  4\. CLI control flow (menu loop, user input handling)  
  5\. Separation of responsibilities (data handling vs CLI)  
  6\. Error handling strategy for invalid input and missing tasks  
    
  Constraints:  
  \- No databases  
  \- No file storage  
  \- No web frameworks  
  \- No external services  
  \- No future phase concepts  
    
  The plan must not introduce new features.  
  It must only describe HOW the approved Phase I requirements will be implemented.

**Step \# 5:**

* Now generate tasks to follow the plan.  
* Tasks → WORK UNITS  
* *Example Prompt:*  
    
  /sp.task Break the Phase I technical plan into atomic implementation tasks.  
    
  Each task must include:  
  \- Task ID  
  \- Clear description  
  \- Preconditions  
  \- Expected output  
  \- Artifacts to be created or modified  
  \- Explicit references to the Phase I specification and plan sections  
    
  Tasks must cover:  
  1\. Task data model and in-memory storage  
  2\. CLI menu and application loop  
  3\. Add task functionality  
  4\. View task list functionality  
  5\. Update task functionality  
  6\. Delete task functionality  
  7\. Mark task complete/incomplete  
  8\. Input validation and error handling  
  9\. Application startup and exit flow  
    
  Rules:  
  \- Tasks must be small, testable, and sequential  
  \- Do NOT introduce new features  
  \- Do NOT include future phases  
  \- Tasks must be sufficient to fully implement Phase I

**Step \# 6:**

* Now implement all the working BUT make sure all the specs and tasks are correct and refine them if they are not because Implementing means code and changes in code may lead to errors.  
* Implement → CODE  
* *Example Prompt:*  
    
  /sp.implement Implement Phase I of the "Evolution of Todo" project.  
    
  Instructions:  
  \- Implement all tasks defined in speckit.tasks  
  \- Follow speckit.constitution strictly  
  \- Follow the Phase I specification and plan exactly  
  \- Generate a working Python console application  
  \- Use only in-memory data structures  
  \- Provide a menu-driven CLI interface  
  \- Handle invalid input and error cases gracefully  
    
  Rules:  
  \- Do NOT introduce new features  
  \- Do NOT include databases, files, or web components  
  \- Do NOT include future phase functionality  
  \- Code must be clear, simple, and readable  
  \- Python version: 3.13+  
    
  Output:  
  \- Generate all required Python source files  
  \- The application must run from the terminal  
  \- The application must fully satisfy Phase I acceptance criteria

This completes **Phase I end-to-end**, exactly as required by the hackathon. Now you may commit these on your GitHub repository and submit.

**Git commands:**

1) git init  
2) git remote add origin “YOUR REPOSITORY URL”  
3) git commit \-m “first commit”  
4) git branch \-M main  
5) git push \-u origin main

(If this document benefitted you in any way, do drop a follow on my social profiles and github too\! Thanks in advance.)

**GOOD LUCK\!**