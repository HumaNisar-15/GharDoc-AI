"""All app settings in one place. Change values here instead of inside the code."""

# Supported interface languages: code -> display name. The first entry is not the default; see DEFAULT_LANG.
LANGUAGES = {"en": "English", "roman": "Roman Urdu", "ur": "اردو"}
DEFAULT_LANG = "en"
RTL_LANGS = {"ur"}

# Gemini models, tried in order. If one is busy or retired, the next one is used.
# If Google renames a model, update the name here (see ai.google.dev/gemini-api/docs/models).
MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-2.5-flash"]

MAX_IMAGE_PX = 1024          # photos are resized to this size before upload (saves quota)
MAX_SCAN_PHOTOS = 3          # maximum photos per diagnosis
RETRIES_PER_MODEL = 2        # attempts per model before moving to the next one
RETRY_WAIT_SEC = 2           # base wait between attempts (seconds)

CONF_MIN = 0.6               # below this AI confidence the risk level is raised by one step

QUOTE_LOW_FACTOR = 0.5       # a quote below min_rate * this factor is 'very low'
QUOTE_HIGH_FACTOR = 1.3      # a quote above max_rate * this factor is 'very high'

RATES_CSV = "data/rates.csv"
