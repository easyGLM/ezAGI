# easyAGI (c) PYTHAI augmented generative intelligence<br />
# framework for enhancing LLM with reasoning

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
│   │   │   ├── SimpleCoder/  # simple coding agent with bash, python and markdown skills
│   │   │   └── ez/  # easy action event controller
│   │   ├── mindX/  # Core functionalities for the MindX submodule.
│   │   │   ├── intr/  # internal reasoning
│   │   │   ├── agents/  # tools as agents
│   │   │   └── control/  # control mechanisms for internal reasoning outputs from mastermind orchestration
│   │   ├── ez/  # core features easy action events
│   │   ├── tests/  # tests for EasyAGI.
│   │   ├── decisions/  # decision-making components.
│   │   ├── memory/  # storage for memory-related data including short term, long term and episodic memory
│   │   │   ├── truth/  # truth data storage for consistent information for SimpleMind training into fact
│   │   │   └── logs/  # logs for tracking memory-related processes and reasoning outputs to be considered for training
│   │   └── mindx/  # executable environment folder to allow internal reasoning, SimpleCoder and agents to create agents for agency
│   │       ├── intr/  # internal reasoning and information retrieval from thoughts
│   │       └── training/  # training processes for models, including SimpleMind with coach.
│   ├── webmind/  # handles web-based data access and processing.
│   │   ├── data_access/  # Data access modules.
│   │   └── tests/  # tests for webMind.
│   ├── webmindML/  # Machine Learning functionalities for web data.
│   │   ├── data_processing/  # Data processing modules.
│   │   └── tests/  # tests for webMindML.
│   ├── openmind/  # open-source components from fundamentalAGI, agi and internal reasoning
│   └── common/  # common utilities and configurations shared across submodules.
│       ├── utils/  # utility functions.
│       ├── configs/  # Configuration files.
│       └── tests/  # Common tests.
├── data/  # Data storage for various stages of processing.
│   ├── raw/  # raw data files.
│   ├── processed/  # processed data files.
│   ├── external/  # external data sources.
│   └── interim/  # intermediate data states.
├── scripts/  # scripts for setup, deployment, training, and evaluation.
│   ├── setup/  # setup and installation scripts.
│   ├── deployment/  # deployment scripts.
│   ├── training/  # training scripts for models.
│   └── evaluation/  # evaluation scripts.
├── configs/  # configuration files for different components.
│   ├── database/  # database configuration files.
│   ├── models/  # model-specific configuration files.
│   └── application/  # application configuration files.
├── tests/  # tests for ensuring code quality and functionality.
│   ├── integration/  # Integration tests.
│   ├── unit/  # Unit tests.
│   └── e2e/  # End-to-end tests.
├── logs/  # Logs for various processes.
│   ├── training/  # logs for training processes.
│   ├── evaluation/  # logs for evaluation processes.
│   └── application/  # application logs.
├── models/  # Storage for model files.
│   ├── trained/  # trained model files from coach using SimpleMind
│   ├── checkpoints/  # checkpoints during training.
│   └── export/  # exported model files from coach
├── results/  # Storage for results and reports.
│   ├── figures/  # graphical results.
│   ├── tables/  # Tabular results.
│   └── reports/  # comprehensive reports.
└── resources/  # Additional resources like images and templates.
    ├── images/  # image files.
    ├── gfx/  # graphics and CSS and styling files.
    └── templates/  # templates for various uses.
```


# <a href="https://github.com/easyGLM/easyAGI/blob/main/requirements.txt">requirements</a><br />
python > 3.7<br />
 <a href="https://console.groq.com/docs/quickstart">groq API key</a> or <br />
 <a href="https://openai.com/index/openai-api/">openai API key</a> <br />

 llama3 integration develoment underway
 
 # INSTALL

```bash
git clone https://github.com/pythaiml/funAGI/
cd funAGI
python3 -m venv agi
source agi/bin/activate
pip install -r requirements.txt
# activate command line interaction (useful as coding agent)
python3 funAGIcli.py
# activate easyAGI.py with internal reasoning (EXPERIMENTAL)
python3 easyAGI.py
```

