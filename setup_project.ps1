# Create folders
$folders = @(
    "cloud-anomalous-login-detection/api/routes",
    "cloud-anomalous-login-detection/api/utils",
    "cloud-anomalous-login-detection/worker",
    "cloud-anomalous-login-detection/models",
    "cloud-anomalous-login-detection/data",
    "cloud-anomalous-login-detection/dashboard/components",
    "cloud-anomalous-login-detection/security",
    "cloud-anomalous-login-detection/scripts",
    "cloud-anomalous-login-detection/notebooks",
    "cloud-anomalous-login-detection/docs/demo_screenshots"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Force -Path $folder | Out-Null
}

# Create files
$files = @(
    "cloud-anomalous-login-detection/README.md",
    "cloud-anomalous-login-detection/one_pager.pdf",
    "cloud-anomalous-login-detection/docker-compose.yml",
    "cloud-anomalous-login-detection/requirements.txt",
    "cloud-anomalous-login-detection/.gitignore",

    "cloud-anomalous-login-detection/api/Dockerfile",
    "cloud-anomalous-login-detection/api/main.py",
    "cloud-anomalous-login-detection/api/schemas.py",

    "cloud-anomalous-login-detection/worker/Dockerfile",
    "cloud-anomalous-login-detection/worker/worker.py",
    "cloud-anomalous-login-detection/worker/features.py",
    "cloud-anomalous-login-detection/worker/rules.py",
    "cloud-anomalous-login-detection/worker/ensemble.py",
    "cloud-anomalous-login-detection/worker/config.py",

    "cloud-anomalous-login-detection/models/isolation_forest.joblib",
    "cloud-anomalous-login-detection/models/autoencoder.pth",
    "cloud-anomalous-login-detection/models/scaler.pkl",

    "cloud-anomalous-login-detection/data/generate_synthetic.py",
    "cloud-anomalous-login-detection/data/sample_events.json",

    "cloud-anomalous-login-detection/dashboard/app.py",
    "cloud-anomalous-login-detection/dashboard/utils.py",

    "cloud-anomalous-login-detection/security/fingerprint.js",
    "cloud-anomalous-login-detection/security/geoip_enrich.py",
    "cloud-anomalous-login-detection/security/LICENSES.md",
    "cloud-anomalous-login-detection/security/alerts.py",

    "cloud-anomalous-login-detection/scripts/send_event.py",
    "cloud-anomalous-login-detection/scripts/run_demo.sh",
    "cloud-anomalous-login-detection/scripts/replay_scenarios.py",

    "cloud-anomalous-login-detection/notebooks/model_dev.ipynb",

    "cloud-anomalous-login-detection/docs/architecture.png"
)

foreach ($file in $files) {
    if (-not (Test-Path $file)) {
        New-Item -ItemType File -Path $file | Out-Null
    }
}

Write-Host "✅ Project structure created successfully!"
