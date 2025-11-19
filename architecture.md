graph TD
    A[User via CLI] --> B{main.py};
    B --> C[TranslationPipeline];
    C --> D[DocumentAnalyzer];
    D --> E{Analysis Result};
    C --> F[TranslationMemory];
    F --> G{TM Match?};
    G -- Yes --> H[Return from TM];
    G -- No --> I[PatentTranslator];
    I --> J{Translation Result};
    C --> K[PatentQAChecker];
    K --> L{QA Result};
    L -- Passed --> M[Save to TM];
    M --> N[Final Output];
    L -- Failed --> N;
    H --> N;

    subgraph "Core Components"
        direction LR
        C; D; F; I; K; M;
    end

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#ccf,stroke:#333,stroke-width:2px
    style N fill:#cfc,stroke:#333,stroke-width:2px
