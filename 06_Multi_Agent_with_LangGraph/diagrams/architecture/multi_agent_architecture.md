# Multi-Agent System Architecture

This document contains the Mermaid diagram for the hierarchical multi-agent workflow system.

## Architecture Diagram

```mermaid
flowchart TD
    %% Meta-Supervisor Level
    MetaSupervisor[🎯 Meta-Supervisor<br/>Routes between teams]
    
    %% Research Team Subgraph (First step in workflow)
    subgraph ResearchTeam["🔍 Research Team"]
        ResearchSupervisor[📋 Research Supervisor<br/>Manages research workflow]
        SearchAgent[🔎 Search Agent<br/>Tavily web search]
        RAGAgent[📚 RAG Agent<br/>Document retrieval]
        
        ResearchSupervisor --> SearchAgent
        ResearchSupervisor --> RAGAgent
        SearchAgent --> ResearchSupervisor
        RAGAgent --> ResearchSupervisor
    end
    
    %% Authoring Team Subgraph (Second step in workflow)
    subgraph AuthoringTeam["✍️ Authoring Team"]
        AuthoringSupervisor[📝 Authoring Supervisor<br/>Manages writing workflow]
        DocWriter[📄 DocWriter<br/>Creates content]
        NoteTaker[📝 NoteTaker<br/>Research & outlines]
        CopyEditor[✏️ CopyEditor<br/>Grammar & style]
        
        AuthoringSupervisor --> DocWriter
        AuthoringSupervisor --> NoteTaker
        AuthoringSupervisor --> CopyEditor
        DocWriter --> AuthoringSupervisor
        NoteTaker --> AuthoringSupervisor
        CopyEditor --> AuthoringSupervisor
    end
    
    %% External Data Sources
    subgraph DataSources["🗄️ Data Sources"]
        TavilyAPI[🌐 Tavily API<br/>Web search]
        QdrantDB[💾 Qdrant Vector DB<br/>Previous responses]
        PDFDocs[📄 PDF Documents<br/>How people use AI]
    end
    
    %% Tools & File System
    subgraph Tools["🛠️ Authoring Team Tools"]
        FileSystem[📁 File System<br/>create_outline, write_document<br/>edit_document, read_document]
        ReferenceTool[🔍 Reference Tool<br/>reference_previous_responses]
    end
    
    %% Main Flow
    MetaSupervisor --> ResearchTeam
    MetaSupervisor --> AuthoringTeam
    
    %% Research Team Connections
    SearchAgent -.-> TavilyAPI
    RAGAgent -.-> PDFDocs
    RAGAgent -.-> QdrantDB
    
    %% Authoring Team Connections  
    AuthoringTeam -.-> Tools
    NoteTaker -.-> QdrantDB
    
    %% Styling
    classDef supervisor fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    classDef agent fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef datasource fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef tool fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class MetaSupervisor,ResearchSupervisor,AuthoringSupervisor supervisor
    class SearchAgent,RAGAgent,DocWriter,NoteTaker,CopyEditor agent
    class TavilyAPI,QdrantDB,PDFDocs datasource
    class FileSystem,ReferenceTool tool
```

## Key Components

### 🎯 Meta-Supervisor Level
- **Meta-Supervisor**: Routes tasks between the Research and Authoring teams

### 🔍 Research Team
- **Research Supervisor**: Manages the research workflow
- **Search Agent**: Uses Tavily API for web search
- **RAG Agent**: Retrieves information from documents and previous responses

### ✍️ Authoring Team  
- **Authoring Supervisor**: Manages the writing workflow
- **DocWriter**: Creates content using file tools
- **NoteTaker**: Creates outlines and references previous work
- **CopyEditor**: Handles grammar, spelling, and style

### 🗄️ Data Sources
- **Tavily API**: Web search capabilities
- **Qdrant Vector DB**: Previous cohort responses
- **PDF Documents**: "How people use AI" dataset

### 🛠️ Authoring Team Tools
- **File System**: Document creation, editing, reading tools (Authoring Team only)
- **Reference Tool**: Access to previous responses (Authoring Team only)

## Flow Characteristics
- **Hierarchical**: Meta-supervisor → Team supervisors → Individual agents
- **Bidirectional**: Agents report back to their supervisors
- **Tool Integration**: Research Team uses web search and RAG; Authoring Team uses file system and reference tools
- **Color-coded**: Different node types have distinct styling
