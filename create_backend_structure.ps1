# === Créer toute la structure backend ===

$base = "backend"
$folders = @(
    # --- DATA ---
    "data/raw", "data/processed", "data/models/production",
    "data/models/staging", "data/models/archived", "data/samples",
    # --- SRC ---
    "src/core", "src/database/repositories", "src/database/migrations/versions",
    "src/ml/models", "src/ml/training", "src/ml/inference",
    "src/ml/preprocessing", "src/ml/explainability",
    "src/etl/extractors", "src/etl/transformers", "src/etl/loaders",
    "src/api/routes", "src/api/middlewares", "src/api/schemas",
    "src/services", "src/utils",
    # --- TESTS ---
    "tests/unit", "tests/integration", "tests/e2e",
    # --- AUTRES ---
    "notebooks", "configs", "scripts", "docs"
)

# Crée les dossiers
foreach ($f in $folders) {
    New-Item -ItemType Directory -Force -Path "$base\$f" | Out-Null
}

# --- Fichiers DATA ---
New-Item "$base\data\raw\.gitkeep" -ItemType File | Out-Null
New-Item "$base\data\raw\README.md" -ItemType File | Out-Null
New-Item "$base\data\processed\.gitkeep" -ItemType File | Out-Null
New-Item "$base\data\processed\transactions_train.csv" -ItemType File | Out-Null
New-Item "$base\data\processed\transactions_test.csv" -ItemType File | Out-Null
New-Item "$base\data\models\production\fraud_model_v1.pkl" -ItemType File | Out-Null
New-Item "$base\data\models\production\preprocessing_pipeline.pkl" -ItemType File | Out-Null
New-Item "$base\data\models\production\model_metadata.json" -ItemType File | Out-Null
New-Item "$base\data\models\staging\fraud_model_v2.pkl" -ItemType File | Out-Null
New-Item "$base\data\models\archived\fraud_model_v0.pkl" -ItemType File | Out-Null
New-Item "$base\data\samples\sample_normal.json" -ItemType File | Out-Null
New-Item "$base\data\samples\sample_fraud.json" -ItemType File | Out-Null

# --- Fichiers PYTHON init ---
Get-ChildItem "$base\src" -Recurse -Directory | ForEach-Object {
    New-Item "$($_.FullName)\__init__.py" -ItemType File -Force | Out-Null
}

# --- Fichiers de config et racine backend ---
$rootFiles = @(
    ".env.example", ".gitignore", "requirements.txt", "requirements-dev.txt",
    "pyproject.toml", "setup.py", "alembic.ini", "pytest.ini", "Makefile", "README.md"
)
foreach ($f in $rootFiles) {
    New-Item "$base\$f" -ItemType File | Out-Null
}

# --- Fichiers de configuration ---
New-Item "$base\configs\api_config.yaml" -ItemType File | Out-Null
New-Item "$base\configs\ml_config.yaml" -ItemType File | Out-Null
New-Item "$base\configs\database_config.yaml" -ItemType File | Out-Null
New-Item "$base\configs\logging_config.yaml" -ItemType File | Out-Null

# --- Fichiers notebooks ---
for ($i = 1; $i -le 6; $i++) {
    $names = @("exploratory_data_analysis", "feature_engineering", "model_training", "model_evaluation", "hyperparameter_tuning", "production_testing")
    New-Item "$base\notebooks\0${i}_$($names[$i-1]).ipynb" -ItemType File | Out-Null
}

# --- Fichiers scripts ---
$scriptFiles = @("setup_db.py", "train_model.py", "generate_synthetic_data.py", "migrate_db.py", "deploy.sh")
foreach ($f in $scriptFiles) {
    New-Item "$base\scripts\$f" -ItemType File | Out-Null
}

# --- Fichiers docs ---
$docFiles = @("architecture.md", "api_reference.md", "ml_models.md", "deployment.md")
foreach ($f in $docFiles) {
    New-Item "$base\docs\$f" -ItemType File | Out-Null
}

Write-Host "✅ Structure complète du dossier backend créée avec succès !"
