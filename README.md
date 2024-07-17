# easyAGI (c) 2024 PYTHAI
# Augmented Generative Intelligence<br />
# a framework for enhancing LLM with reasoning

```csharp
PYTHAI/
├── docs/  # Documentation for various aspects of the project.
│   ├── white_papers/  white papers discussing theoretical aspects of easyAGI innovations
│   ├── technical_docs/  # technical documentation for developers
│   ├── user_guides/  # guides for end-users and UIUX integration
│   └── tutorials/  # step-by-step tutorials for various functionalities.
├── src/  # Source code for all submodules and main functionalities.
│   ├── easyAGI/  # contains submodules and features specific to EasyAGI.
│   │   ├── simplemind/  # code for the SimpleMind neural network and coach trainer
│   │   ├── mastermind/  # code for masterind orchestrator of agency
│   │   ├── automind/  # code for reasoning as automind
│   │   ├── automindx/  # automind agency environment
│   │   │   ├── SimpleCoder/  # simple coding agent with bash, python and markdown agent generation
│   │   │   └── ez/  # easy action event controller
│   │   ├── mindX/  # Core functionalities for the MindX submodule.
│   │   │   ├── decisions/  # internal reasoning
│   │   │   ├── agency/  # tools as agents orchestated by mastermind
│   │   │   └── control/  # control mechanisms for internal reasoning outputs from mastermind orchestration
│   │   ├── ez/  # core features easy javascript action events
│   │   ├── tests/  # tests for EasyAGI.
│   │   ├── decisions/  # decision-making components.
│   │   ├── memory/  # storage for memory-related data including short term, long term and episodic memory
│   │   │   ├── truth/  # truth data storage for consistent information for SimpleMind training into fact using coach
│   │   │   └── logs/  # logs for tracking memory-related processes and reasoning outputs to be considered for training
│   │   └── mindx/  # executable environment folder to allow internal reasoning, SimpleCoder and agents to create agents for agency
│   │       ├── intr/  # internal reasoning and information retrieval from thoughts
│   │       └── training/  # training processes for models, including SimpleMind with coach
│   ├── webmind/  # handles web-based data access and processing
│   │   ├── data_access/  # data access modules
│   │   └── tests/  # tests for webMind
│   ├── webmindML/  # Machine Learning functionalities for web data
│   │   ├── data_processing/  # Data processing modules
│   │   └── tests/  # tests for webMindML
│   ├── openmind/  # open-source components from fundamentalAGI, agi and internal reasoning
│   └── common/  # common utilities and configurations shared across submodules
│       ├── utils/  # utility functions
│       ├── configs/  # Configuration files
│       └── tests/  # Common tests
├── data/  # Data storage for various stages of processing
│   ├── raw/  # raw data files
│   ├── processed/  # processed data files
│   ├── external/  # external data sources
│   └── interim/  # intermediate data states
├── scripts/  # scripts for setup, deployment, training, and evaluation
│   ├── setup/  # setup and installation scripts
│   ├── deployment/  # deployment scripts
│   ├── training/  # training scripts for models
│   └── evaluation/  # evaluation scripts
├── configs/  # configuration files for different components
│   ├── database/  # database configuration files
│   ├── RAGE/  # retrieval augmented gerative engine including model-specific configuration files
│   └── application/  # application configuration files
├── tests/  # tests for ensuring code quality and functionality
│   ├── integration/  # Integration tests
│   ├── unit/  # unit tests
│   └── e2e/  # end-to-end tests
├── logs/  # logs for various processes
│   ├── training/  # logs for training processes
│   ├── evaluation/  # logs for evaluation processes
│   └── application/  # application logs
├── models/  # storage for model files
│   ├── trained/  # trained model files from coach using SimpleMind
│   ├── checkpoints/  # checkpoints during training
│   └── export/  # exported model files from coach
├── results/  # storage for results and reports
│   ├── figures/  # graphical results
│   ├── tables/  # tabular results
│   └── reports/  # comprehensive reports
└── resources/  # additional resources like images and templates
    ├── images/  # generated image files
    ├── gfx/  # graphics and CSS and styling files
    └── templates/  # templates for various uses
```


# <a href="https://github.com/easyGLM/easyAGI/blob/main/requirements.txt">requirements</a><br />
python > 3.7<br />
 <a href="https://console.groq.com/docs/quickstart">groq API key</a> or <br />
 <a href="https://openai.com/index/openai-api/">openai API key</a> <br />

 llama3 integration is being developed
 
 # INSTALL

```bash
git clone https://github.com/easyGLM/easyAGI/
cd easyAGI
python3 -m venv agi
source agi/bin/activate
pip install -r requirements.txt
# activate easyAGI.py with internal reasoning (EXPERIMENTAL)
python3 easyAGI.py
```

The easyAGI project is an augmented intelligence system designed to provide human-like reasoning and decision-making as output from exiting LLM. 


MASTERMIND

    Purpose: Acts as the central controller of the entire system.
    Functions:
        Automatically sets up necessary configurations.
        Manages different AI agents, ensuring they work together smoothly.
        Monitors system health and triggers self-repair actions if something goes wrong.

SimpleCoder

    Purpose: An AI agent that can write code in multiple programming languages.
    Functions:
        Generates code snippets for tasks like "Hello, World!" in languages such as Python, JavaScript, and more.
        Keeps a log of its activities for transparency and tracking.

BDI (Belief-Desire-Intention)

    Purpose: Implements a model to simulate human-like reasoning.
    Functions:
        Manages beliefs (what the AI knows), desires (goals the AI wants to achieve), and intentions (plans to achieve those goals).
        Provides detailed logging to track its reasoning process.

Self-Healing

    Purpose: Maintains the health of the AI system.
    Functions:
        Regularly checks CPU, memory, and disk usage.
        Can restart services or the entire system if needed to fix issues.
        Frees up disk space by removing unnecessary files.

Reasoning

    Purpose: Provides various logical reasoning strategies to support decision-making.
    Functions:
        Uses different types of reasoning like deductive (specific conclusions from general premises), inductive (general conclusions from specific observations), and more.
        Helps the AI make informed decisions based on logic and evidence.

LogicTables

    Purpose: Manages logical variables and expressions to support reasoning.
    Functions:
        Adds and manages logical statements.
        Generates truth tables to evaluate the validity of logical expressions.
        Stores valid conclusions for future reference.

SimpleMind

    Purpose: A minimalistic neural network designed for learning and long-term memory.
    Functions:
        Configurable neural network that can be trained on new data.
        Uses JAX for efficient mathematical computations.
        Supports parallel training to speed up the learning process.

Coach

    Purpose: Trains the SimpleMind neural network using stored beliefs.
    Functions:
        Loads and preprocesses beliefs from memory.
        Trains the neural network and saves the model for future use.
        Logs training sessions and results for transparency.

Integration

The easyAGI project integrates all these components under the MASTERMIND orchestrator, ensuring they work together seamlessly. Here’s how it works:

    Initialization: MASTERMIND sets up the system and loads different AI agents like SimpleCoder.
    Execution: Agents perform tasks such as writing code or making logical decisions.
    Monitoring: The system’s health is continuously checked, and self-repair actions are taken if necessary.
    Learning: The SimpleMind neural network is trained on stored data to improve its performance over time.
    Decision-Making: Using logical reasoning and validated truths, the AI system makes informed decisions.


easyAGI is a comprehensive Augmented Intelligence framework capable of reasoning, decision-making, self-healing, and learning capabilities providing an advanced and autonomous system. easyAGI is designed to simulate human-like intelligence and operate reliably, making it a powerful tool for various applications.

