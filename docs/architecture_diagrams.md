# GNU MLOps Pipeline - Architecture Diagrams

This document contains architecture diagrams for training, data flow, MLflow, and Databricks integration.

---

## 0. High-Level Architecture (System Overview)

```mermaid
graph TB
    subgraph "Data Layer"
        A1[Raw Data Sources] --> A2[Data Preprocessing]
        A2 --> A3[Processed Datasets]
    end
    
    subgraph "MLOps Core"
        A3 --> B1[Model Training]
        B1 --> B2[Model Evaluation]
        B2 --> B3[Model Registry]
    end
    
    subgraph "MLflow Platform"
        B1 --> C1[Experiment Tracking]
        B3 --> C2[Model Versioning]
        C1 --> C3[MLflow Backend]
        C2 --> C3
    end
    
    subgraph "Deployment Layer"
        B3 --> D1[Staging Environment]
        B3 --> D2[Production Environment]
    end
    
    subgraph "Inference Services"
        D2 --> E1[Single Inference API]
        D2 --> E2[Batch Inference Service]
        A3 --> E2
    end
    
    subgraph "Automation"
        F1[30-Day Scheduler] --> B1
        G1[CI/CD Pipeline] --> B1
        G1 --> D1
        G1 --> D2
    end
    
    subgraph "Monitoring & Operations"
        E1 --> H1[Prediction Logs]
        E2 --> H1
        D2 --> H2[Model Monitoring]
        H1 --> H3[Dashboards]
        H2 --> H3
    end
    
    style B1 fill:#4CAF50
    style C3 fill:#0194E2
    style D2 fill:#FF6B6B
    style E1 fill:#FF9800
    style E2 fill:#FF9800
    style F1 fill:#9C27B0
```

---

## 1. Training Architecture

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

---

## 2. Data Flow Architecture

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

---

## 3. MLflow Architecture

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

---

## 4. Databricks Integration Architecture

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

---

## 5. Complete MLOps Pipeline Architecture

```mermaid
graph TB
    subgraph "Data Layer"
        A1[Raw Data] --> A2[Preprocessing Scripts]
        A2 --> A3[Training Data]
        A2 --> A4[Test Data]
        A2 --> A5[Inference Data]
    end
    
    subgraph "Training Layer"
        A3 --> B1[Model Training]
        B1 --> B2[Model Evaluation]
        B2 --> B3[Model Registration]
    end
    
    subgraph "MLflow Tracking"
        B1 --> C1[Log Metrics]
        B1 --> C2[Log Parameters]
        B1 --> C3[Save Artifacts]
        C1 --> C4[MLflow Backend]
        C2 --> C4
        C3 --> C4
    end
    
    subgraph "Model Registry"
        B3 --> D1[Model Versioning]
        D1 --> D2[Stage Management]
        D2 --> D3[Staging]
        D2 --> D4[Production]
    end
    
    subgraph "Deployment Layer"
        D3 --> E1[Staging Deployment]
        D4 --> E2[Production Deployment]
    end
    
    subgraph "Inference Layer"
        A5 --> F1[Single Inference]
        A5 --> F2[Batch Inference]
        E2 --> F1
        E2 --> F2
        F1 --> F3[Predictions]
        F2 --> F3
    end
    
    subgraph "Retraining Layer"
        G1[30-Day Scheduler] --> G2[Check Last Training]
        G2 --> G3[Retrain Model]
        G3 --> G4[Compare Performance]
        G4 -->|Better| G5[Auto Deploy]
        G4 -->|Worse| G6[Keep Current]
    end
    
    style B1 fill:#4CAF50
    style C4 fill:#0194E2
    style D1 fill:#FF6B6B
    style F1 fill:#FF9800
    style F2 fill:#FF9800
    style G3 fill:#9C27B0
```

---

## 6. GitHub Actions CI/CD Pipeline

```mermaid
graph LR
    A[Git Push] --> B[GitHub Actions Trigger]
    B --> C[Checkout Code]
    C --> D[Setup Python]
    D --> E[Install Dependencies]
    E --> F{Train Model}
    F -->|Success| G[Deploy to Staging]
    F -->|Failure| H[Notify Team]
    G --> I{Tests Pass?}
    I -->|Yes| J[Deploy to Production]
    I -->|No| K[Rollback]
    J --> L[Update Model Registry]
    L --> M[Notify Success]
    
    style F fill:#4CAF50
    style G fill:#FF9800
    style J fill:#FF6B6B
```

---

## 7. Model Lifecycle Management

```mermaid
stateDiagram-v2
    [*] --> Training: Start Training
    Training --> Registered: Model Registered
    Registered --> None: Initial Version
    None --> Staging: Deploy to Staging
    Staging --> Production: Promote to Production
    Staging --> GNU_Production: Deploy to GNU_Production
    Production --> GNU_Production: Deploy to GNU_Production
    GNU_Production --> Archived: Archive Old Model
    Staging --> Archived: Archive Failed Model
    Production --> Archived: Archive Deprecated
    Archived --> [*]: Delete
    
    note right of Training
        Train with latest data
        Evaluate performance
        Log metrics to MLflow
    end note
    
    note right of Staging
        Test in staging environment
        Validate predictions
        Monitor performance
    end note
    
    note right of Production
        Live production model
        Serving real requests
        Monitored continuously
    end note
```

---

## 8. Data Preprocessing Pipeline

```mermaid
graph TD
    A[Raw Data Input] --> B{Data Type?}
    B -->|Titanic| C[Titanic Preprocessing]
    B -->|Diabetes| D[Diabetes Preprocessing]
    B -->|Other| E[Generic Preprocessing]
    
    C --> F[Handle Missing Values]
    D --> F
    E --> F
    
    F --> G[Feature Engineering]
    G --> H[One-Hot Encoding]
    H --> I[Feature Scaling]
    I --> J[Train/Test Split]
    
    J --> K[Training Dataset]
    J --> L[Test Dataset]
    J --> M[Inference Dataset]
    
    K --> N[Save to data/training/]
    L --> O[Save to data/testing/]
    M --> P[Save to data/inference_input/]
    
    style C fill:#4CAF50
    style D fill:#4CAF50
    style F fill:#FF9800
    style I fill:#0194E2
```

---

## Usage Instructions

### For PowerPoint/Keynote:
1. Copy the Mermaid diagram code
2. Use online tools like:
   - [Mermaid Live Editor](https://mermaid.live/)
   - [Mermaid.ink](https://mermaid.ink/)
3. Export as PNG/SVG
4. Insert into your presentation

### For Markdown Presentations:
- Use tools like Marp, Reveal.js, or GitHub that support Mermaid natively

### For Documentation:
- These diagrams render automatically in GitHub, GitLab, and many documentation tools

---

## Diagram Descriptions

1. **Training Architecture**: Shows the complete training pipeline from data sources to model registry
2. **Data Flow Architecture**: Illustrates how data moves through the system
3. **MLflow Architecture**: Details MLflow components and storage backends
4. **Databricks Integration**: Shows how local and Databricks environments interact
5. **Complete MLOps Pipeline**: End-to-end view of the entire system
6. **GitHub Actions CI/CD**: Automated deployment pipeline
7. **Model Lifecycle Management**: State diagram of model stages
8. **Data Preprocessing Pipeline**: Data transformation workflow

