# Architecture Diagrams - Export Guide

This guide helps you export the architecture diagrams for use in PowerPoint presentations.

## Quick Export Methods

### Method 1: Mermaid Live Editor (Recommended)
1. Go to https://mermaid.live/
2. Copy the Mermaid code from `architecture_diagrams.md`
3. Paste into the editor
4. Click "Actions" → "Download PNG" or "Download SVG"
5. Insert into PowerPoint

### Method 2: Mermaid.ink API
Use this URL format to generate images:
```
https://mermaid.ink/img/<base64_encoded_mermaid_code>
```

### Method 3: VS Code Extension
1. Install "Markdown Preview Mermaid Support" extension
2. Open `architecture_diagrams.md`
3. Right-click on diagram → "Copy Image"
4. Paste into PowerPoint

### Method 4: Online Tools
- **Kroki.io**: https://kroki.io/
- **Mermaid Chart**: https://www.mermaidchart.com/
- **Draw.io**: Import Mermaid code

## Individual Diagram Files

For easier access, here are direct links to export each diagram:

### 1. Training Architecture
```mermaid
graph TB
    subgraph "Data Sources"
        A[Local CSV Files] --> B[Data Preprocessing]
        C[Databricks Tables] --> B
        D[S3 Buckets] --> B
    end
    
    subgraph "Training Pipeline"
        B --> E[Data Validation]
        E --> F[Feature Engineering]
        F --> G[Train/Test Split]
        G --> H[Feature Scaling]
        H --> I[Model Training]
    end
    
    subgraph "MLflow Tracking"
        I --> J[Log Metrics]
        I --> K[Log Parameters]
        I --> L[Log Artifacts]
        J --> M[MLflow Tracking Server]
        K --> M
        L --> M
    end
    
    subgraph "Model Registry"
        M --> N[Register Model]
        N --> O[Model Versioning]
        O --> P[Stage Management]
        P --> Q[Production Model]
    end
    
    style I fill:#4CAF50
    style M fill:#0194E2
    style Q fill:#FF6B6B
```

### 2. Data Flow Architecture
```mermaid
graph LR
    subgraph "Data Ingestion"
        A1[Raw Data Sources] --> A2[Data Validation]
        A2 --> A3[Data Cleaning]
    end
    
    subgraph "Data Processing"
        A3 --> B1[Feature Extraction]
        B1 --> B2[Feature Engineering]
        B2 --> B3[Data Transformation]
    end
    
    subgraph "Storage"
        B3 --> C1[Training Data]
        B3 --> C2[Test Data]
        B3 --> C3[Inference Data]
    end
    
    subgraph "Model Training"
        C1 --> D1[Model Training]
        C2 --> D2[Model Validation]
    end
    
    subgraph "Inference"
        C3 --> E1[Batch Inference]
        C3 --> E2[Single Inference]
        D1 --> E1
        D1 --> E2
    end
    
    subgraph "Output"
        E1 --> F1[Predictions CSV]
        E2 --> F2[Prediction Results]
    end
    
    style D1 fill:#4CAF50
    style E1 fill:#FF9800
    style E2 fill:#FF9800
```

### 3. MLflow Architecture
```mermaid
graph TB
    subgraph "MLflow Components"
        A[MLflow Tracking] --> B[Experiment Tracking]
        A --> C[Metric Logging]
        A --> D[Parameter Logging]
        A --> E[Artifact Storage]
        
        F[MLflow Models] --> G[Model Packaging]
        F --> H[Model Signatures]
        F --> I[Dependencies]
        
        J[Model Registry] --> K[Model Versioning]
        J --> L[Stage Transitions]
        J --> M[Model Lineage]
    end
    
    subgraph "Backend Storage"
        E --> N[SQLite Database]
        E --> O[Databricks Workspace]
        E --> P[Local File System]
        
        N --> Q[mlflow.db]
        O --> R[Databricks Artifacts]
        P --> S[mlruns/]
    end
    
    subgraph "Access Layer"
        T[MLflow UI] --> N
        T --> O
        U[Python API] --> N
        U --> O
        V[REST API] --> N
        V --> O
    end
    
    style A fill:#0194E2
    style J fill:#FF6B6B
    style T fill:#4CAF50
```

### 4. Databricks Integration
```mermaid
graph TB
    subgraph "Local Development"
        A1[Local Python Scripts] --> A2[MLflow Client]
        A2 --> A3{Environment Check}
    end
    
    subgraph "Databricks Workspace"
        A3 -->|Databricks Mode| B1[Databricks Host]
        B1 --> B2[Workspace Model Registry]
        B1 --> B3[Unity Catalog]
        
        B2 --> B4[Workspace Experiments]
        B3 --> B5[Catalog.schema.model]
        
        B4 --> B6[MLflow Tracking]
        B5 --> B6
    end
    
    subgraph "Local Fallback"
        A3 -->|SQLite Mode| C1[SQLite Database]
        C1 --> C2[Local MLflow]
        C2 --> C3[mlflow.db]
    end
    
    subgraph "Model Registry"
        B6 --> D1[Model Versions]
        C2 --> D1
        D1 --> D2[Staging Stage]
        D1 --> D3[Production Stage]
        D1 --> D4[GNU_Production Stage]
    end
    
    subgraph "Deployment"
        D2 --> E1[Staging Deployment]
        D3 --> E2[Production Deployment]
        D4 --> E3[GNU Production Deployment]
    end
    
    style B1 fill:#FF6B00
    style B3 fill:#FF6B00
    style C1 fill:#4CAF50
    style D1 fill:#0194E2
```

## PowerPoint Tips

1. **High Resolution**: Export as SVG for best quality, then convert to PNG at 300 DPI
2. **Consistent Colors**: Use the color scheme from the diagrams:
   - Green (#4CAF50): Training/Processing
   - Blue (#0194E2): MLflow/Tracking
   - Red (#FF6B6B): Production/Registry
   - Orange (#FF9800): Inference
   - Purple (#9C27B0): Retraining
3. **Fonts**: Use monospace fonts for code/text diagrams
4. **Layout**: Keep diagrams simple and uncluttered for presentations

## Alternative: Use Text Diagrams

If Mermaid doesn't work, use the simple text diagrams from `architecture_diagrams_simple.txt`:
- Copy the ASCII art
- Paste into PowerPoint
- Format with monospace font (Courier New, Consolas)
- Add colors manually

