from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS: lets the grader's web page call your API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- The 4 layers (lowest to highest priority) ----
DEFAULTS = {
    "port": 8000, "workers": 1, "debug": False,
    "log_level": "info", "api_key": "default-secret-000",
}
YAML_LAYER = {"workers": 13, "log_level": "error"}
DOTENV_LAYER = {
    "APP_PORT": "8708", "NUM_WORKERS": "13", "APP_API_KEY": "key-9t0ncrijs5",
}
OS_ENV_LAYER = {"APP_WORKERS": "16", "APP_LOG_LEVEL": "warning"}


def clean_key(key: str) -> str:
    """APP_PORT -> port, NUM_WORKERS -> workers, etc."""
    key = key.strip().lower()
    if key.startswith("app_"):
        key = key[4:]
    if key == "num_workers":      # the alias rule
        key = "workers"
    return key


def coerce(key: str, value):
    """Turn values into the right type."""
    if key in ("port", "workers"):
        try:
            return int(value)
        except (ValueError, TypeError):
            return value
    if key == "debug":
        return str(value).strip().lower() in ("true", "1", "yes", "on")
    return str(value)


@app.get("/effective-config")
def effective_config(request: Request):
    config = {}

    # Apply layers from lowest to highest; later ones overwrite earlier ones
    for layer in (DEFAULTS, YAML_LAYER, DOTENV_LAYER, OS_ENV_LAYER):
        for k, v in layer.items():
            config[clean_key(k)] = v

    # ?set=key=value overrides (highest priority)
    for item in request.query_params.getlist("set"):
        if "=" in item:
            k, v = item.split("=", 1)   # split only on the FIRST "="
            config[clean_key(k)] = v

    # Fix types
    result = {k: coerce(k, v) for k, v in config.items()}

    # Hide the secret
    result["api_key"] = "****"
    return result
