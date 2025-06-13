# Longevity AI Application

> **AI-Powered Longevity Knowledge Assistant - Production Application**

A professional, production-ready application that provides evidence-based longevity advice using advanced AI and Retrieval Augmented Generation (RAG).

## 🧬 About

This application transforms cutting-edge longevity research into actionable health insights using:

- **Retrieval Augmented Generation (RAG)** for evidence-based responses
- **OpenAI GPT models** for intelligent conversation
- **Supabase vector database** for semantic search
- **FastAPI** for scalable REST API
- **Modern Python packaging** for professional development

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key
- Supabase account with pgvector enabled

### Installation

```bash
# Clone the repository
git clone https://github.com/ruthiel/longevity-ai-app.git
cd longevity-ai-app

# Create virtual environment
python -m venv longevity-ai-env
source longevity-ai-env/bin/activate  # On Windows: longevity-ai-env\Scripts\activate

# Install the application
pip install -r requirements.txt"

# Configure environment
cp .env
# Edit .env with your API keys
```

### Usage

#### Start the API server

```bash
longevity-ai serve

# Or directly with Python
python -m longevity_ai.api.app

# Interactive CLI chat
longevity-ai interactive

# Check application health
longevity-ai health
```

### 📁 Project Structure

```bash
longevity-ai-app`
├── longevity_ai/           # Main application package
│   ├── config/            # Configuration management
│   ├── core/              # Core models and exceptions
│   ├── data/              # Data loading and processing
│   ├── vectorstore/       # Vector database operations
│   ├── llm/               # Language model integration
│   ├── rag/               # RAG pipeline orchestration
│   ├── api/               # FastAPI REST API
│   ├── cli/               # Command-line interface
│   └── utils/             # Utility functions
├── tests/                 # Comprehensive test suite
├── scripts/               # Deployment and utility scripts
├── data/                  # Data storage
├── docs/                  # Documentation
└── frontend/              # Optional web interface
``` 

### 🔬 Research Origins

This production application is based on research and prototyping done in our research repository.
Research Repo: Jupyter notebooks, experimentation, data analysis
Production Repo: This repository - scalable application, APIs, deployment

### Run tests

pytest

### Start development server

longevity-ai serve --reload

### 📚 Documentation

API Documentation
Deployment Guide
Architecture Overview
User Guide

### 🤝 Contributing

Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
🙏 Acknowledgments

Built with LangChain for LLM applications
Powered by OpenAI for language models and embeddings
Vector storage by Supabase with pgvector
Web framework by FastAPI

Made with ❤️ for healthy longevity
