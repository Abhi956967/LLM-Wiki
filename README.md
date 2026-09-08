# 🧠 Abhishek Second Brain Wiki — Complete Architecture & User Manual

Welcome to **LLM Wiki (Personal Second Brain)**! This document is a complete, beginner-friendly, step-by-step manual explaining how the system works, how to start and operate it, how to add documents, and how Claude automatically compiles your personal Wikipedia.

---

## 📑 Table of Contents
1. [Architecture Overview](#-architecture-overview)
2. [Prerequisites & System Setup](#-prerequisites--system-setup)
3. [How to Start & Run the Project](#-how-to-start--run-the-project)
4. [Connecting Claude Desktop via MCP](#-connecting-claude-desktop-via-mcp)
5. [How to Add Documents & Generate Wiki Pages](#-how-to-add-documents--generate-wiki-pages)
6. [Navigating the Web Interface (Graph & Wiki)](#-navigating-the-web-interface)
7. [Troubleshooting & FAQs](#-troubleshooting--faqs)

---

## 🏛️ Architecture Overview

```
                      ┌─────────────────────────────────┐
                      │    Claude Desktop / Claude Code │
                      │   (AI Brain & Autonomous Agent) │
                      └──────────────┬──────────────────┘
                                     │  Model Context Protocol (MCP)
                                     ▼
                      ┌─────────────────────────────────┐
                      │   LLM Wiki MCP Server (mcp/)    │
                      │     (Read, Search, Write Tools) │
                      └──────────────┬──────────────────┘
                                     │
         ┌───────────────────────────┴───────────────────────────┐
         │                                                       │
         ▼                                                       ▼
┌─────────────────────────────────┐             ┌─────────────────────────────────┐
│     FastAPI Backend (api/)      │             │     Next.js Web App (web/)      │
│  - Document Ingestion & Chunking│             │  - Interactive 2D Graph Viewer  │
│  - Hybrid Search (BM25 + Vector)│ ◄────────── │  - Wikipedia-style Page Reader  │
│  - Citations & Cross-References │             │  - Document Source Viewer       │
└────────────────┬────────────────┘             └─────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│               Knowledge Workspace (MySecondBrain/)              │
│  ├── wiki/            -> Generated Markdown Wiki Pages          │
│  ├── 100_LLM_...md    -> Raw Source Documents & Notes           │
│  ├── resume.pdf       -> Uploaded PDFs, Word docs, spreadsheets │
│  └── .llmwiki/        -> SQLite Index (index.db) & Asset Cache  │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Prerequisites & System Setup

- **Operating System:** Windows 10/11, macOS, or Linux
- **Python:** `3.11+`
- **Node.js:** `v20+` or `v24+`

### One-Time Setup on Windows:

```powershell
# 1. Open PowerShell inside the project directory
cd "C:\Users\am600\OneDrive\Desktop\Project\Abhishek-Second-Brain-wiki"

# 2. Create Python virtual environment
python -m venv .venv

# 3. Activate virtual environment
.venv\Scripts\Activate.ps1

# 4. Install Python dependencies (including PDF extractor)
python -m pip install -r api/requirements.txt -r mcp/requirements.txt pypdf

# 5. Install Web Frontend dependencies
cd web
npm install
cd ..
```

---

## 🚀 How to Start & Run the Project

Whenever you want to use your Second Brain:

```powershell
# In the project directory:
.venv\Scripts\python llmwiki open "C:\Users\am600\MySecondBrain"
```

### What happens automatically:
1. Starts the **Python API** on `http://127.0.0.1:8000`.
2. Starts the **Next.js Web UI** on `http://localhost:3000`.
3. Opens your default web browser to the Knowledge Base interface.
4. Starts a real-time **file watcher** on your workspace folder.

---

## 🔌 Connecting Claude Desktop via MCP

1. Open **Claude Desktop**.
2. Go to **Settings** (`Ctrl + ,`) ➔ **Developer** ➔ **Edit Config**.
3. In `claude_desktop_config.json`, add the `mcpServers` block:

```json
{
  "mcpServers": {
    "llmwiki-mysecondbrain": {
      "command": "C:\\Users\\am600\\OneDrive\\Desktop\\Project\\Abhishek-Second-Brain-wiki\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\am600\\OneDrive\\Desktop\\Project\\Abhishek-Second-Brain-wiki\\llmwiki",
        "mcp",
        "C:\\Users\\am600\\MySecondBrain"
      ]
    }
  }
}
```
4. Restart Claude Desktop.
5. In Claude's chat input bar, verify the **`llmwiki-mysecondbrain`** connector is toggled **ON** (blue).

---

## 📂 How to Add Documents & Generate Wiki Pages

### 1. Adding Files:
Simply copy and paste any files into your folder:
📍 **`C:\Users\am600\MySecondBrain`**
- **PDFs:** Research papers, cheat sheets, ebooks, resumes.
- **Markdown / Text:** `.md`, `.txt` notes.
- **Documents:** Word (`.docx`), PowerPoint (`.pptx`), Excel (`.xlsx`, `.csv`).

### 2. Asking Claude to Generate Wiki Pages:
In Claude Desktop, prompt Claude:
> *"Read the guide, check the newest source files in my workspace, and compile comprehensive wiki pages with cross-links and source citations."*

Claude will read the files over MCP and generate structured, cross-referenced Markdown files in `C:\Users\am600\MySecondBrain\wiki\`.

---

## 🌐 Navigating the Web Interface

Open `http://localhost:3000` in your browser:

1. **Left Sidebar (Wiki Pages):**
   - Click on any page (e.g. `Overview`, `LLM Foundations`, `RAG`, etc.) to read the compiled notes.
   - Click internal markdown links (`[Topic](page.md)`) to jump between concepts.
   - Click footnote citations (`[^1]`) to jump straight to the source document page!

2. **Graph View (2D Knowledge Graph):**
   - Click the **Graph Icon** in the top navigation bar.
   - You can drag, zoom, and explore connections between concepts.
   - **Clicking any node** immediately opens that specific wiki page or source document.
   - Click **`Sources`** in the top-right corner of the graph to toggle source document nodes.
   - Click **`Rebuild`** if you ever edit files manually to refresh all cross-references.

3. **Files / Sources Tab:**
   - Click **`Sources`** at the bottom-left or top bar to view raw uploaded files.

---

## 🛠️ Troubleshooting & FAQs

### Q: What if a PDF takes long or fails to upload?
- Local mode uses pure-Python `pypdf` extraction, which runs in < 1 second.
- You do not need to use the web upload button: you can directly copy-paste files into `C:\Users\am600\MySecondBrain` and run:
  ```powershell
  .venv\Scripts\python llmwiki reindex "C:\Users\am600\MySecondBrain"
  ```

### Q: Why did the graph say "No citations found"?
- Graph references are created from internal markdown links (e.g. `[Transformers](transformers-and-internals.md)`) and citations (e.g. `[^1]: paper.pdf, p.5`).
- Click the **`Rebuild`** button in the top-right of the Graph view to refresh references anytime.

### Q: How do I stop the servers?
- In your PowerShell window, press **`Ctrl + C`**.

---

⭐ *Built and maintained with AI by Abhishek Maurya.*
