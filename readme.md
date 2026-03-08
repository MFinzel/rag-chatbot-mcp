# RAG Chatbot mit MCP Tooling

Dieses Projekt ist ein lokaler Prototyp für einen **RAG-Chatbot** mit **Tool-Integration über MCP**.

Der Chatbot verarbeitet PDF-Dokumente, speichert deren Embeddings in einer lokalen **ChromaDB** und liefert Antworten auf Basis der gefundenen Inhalte.  
Zusätzlich kann er Zusammenfassungen erstellen und diese über ein **MCP Mail Tool** per E-Mail versenden.

## Features

- PDF-Ingestion und Embedding-Erstellung
- lokale Vector Database mit ChromaDB
- RAG-basierte Antworten mit OpenAI
- natürlichsprachige Zusammenfassung von Dokumentinhalten
- E-Mail-Versand über MCP Tooling (SMTP)

## zukünftige Entwicklungen

- Crawler Service mit RSS-Feed Einbindung
- Containerisierung der Services für Microservices Architektur
- IaC Komponenten für Cluster-Betrieb

## Verwendung

- PDF in data speichern
- ingest_database.py einmalig ausführen mit **python .\ingest_database.py** 
- mcp_server start mit **fastmcp run mcp_server.py:mcp --transport http --port 8000**
- chatbot starten mit **python .\chatbot.py** und über local host aufrubar 
- z.B Dokument zusammenfassen lassen
- mit /mail Empfängermail | Betreff | Text  MCP Tool aufrufen und Zusammenfassung versenden 

## Architektur

```mermaid
flowchart TD
    A[PDF Dokumente] --> B[Ingest Script]
    B --> C[ChromaDB lokal]
    D[User im Chatbot] --> E[Gradio Chat UI]
    E --> F[RAG Retrieval]
    F --> C
    F --> G[OpenAI LLM]
    G --> H[Antwort / Zusammenfassung]
    H --> I[MCP Mail Tool]
    I --> J[SMTP Mail Versand]


    