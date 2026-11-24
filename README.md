# GharDoc AI
**Scan, Diagnose, and Fix!**

AI home-inspection assistant for Pakistani families. Take a photo of a wall problem (dampness / seepage, cracks, peeling plaster, pipe leaks) and get a plain-language diagnosis, a risk level, recommended fixes, an estimated cost in PKR and questions to ask your mistri.

**Live demo:** [your streamlit link]  |  **Video:** [your video link]

## Why we built it
We faced a damp, cracking wall at home and could not tell how serious it was or what a fair repair price would be. To the best of our research, we did not find a Pakistani app that combines a photo diagnosis, a PKR estimate and a quote check.

## Features
- **Scan and Diagnose:** problem type, likely causes, green / yellow / red risk meter
- **Fix:** recommended fixes, who to call, estimated cost range in PKR, questions to ask the worker
- **Quote check** and **Crack tracker** (is it growing?)
- Diagnosis history, rate list, Pakistani material guide, seasonal checklists, emergency safety steps
- English, Roman Urdu and Urdu (right-to-left)

## How it works
1. A Google Gemini vision model reads the photo and returns structured JSON.
2. Safety rules in plain Python can only raise the risk level, never lower it.
3. The AI only picks job IDs. Prices come from our own rate table (`data/rates.csv`), never from the AI.

## Run locally
1. Python 3.10+ and `pip install -r requirements.txt`
2. Create `.streamlit/secrets.toml` (never commit it): `GEMINI_API_KEY = "your-key"`
3. `streamlit run app.py`

## Deploy
Streamlit Community Cloud: new app > `app.py`, then App settings > Secrets > add `GEMINI_API_KEY`.

## Data
Wall photos taken by the team. Rates collected from local contractors and waterproofing companies **Ultra Chemicals** and **Professional Sealers**. Rates are estimates and change with city and time.

## Testing
We tested the app on real wall photos taken by the team and compared the AI's answer with our own labels reviewed by visited comapnies.

| Measure | Result |
| --- | --- |
| Photos tested | [10] |
| Problem type identified correctly | [10] of [N] |
| Risk level matched our label | [10] of [N] |
| Deep cracks wrongly marked green | [2] |

## Real-world validation
We met two waterproofing companies, **Ultra Chemicals** and **Professional Sealers**, to learn current market rates and how they diagnose and fix dampness, seepage and cracks. Their answers shaped our rate table and the questions the app suggests to users.

Both companies liked the idea, encouraged us to continue, and expressed interest in working with us to digitise their own processes, such as site inspections, quotes and customer follow-up. This is an expression of interest, not a signed partnership.

## Limitations
Estimates only, not an engineer's report. Deep or growing cracks must be checked by a structural engineer. The AI can make mistakes, so the app raises the risk level when unsure.

## AI tools and our contribution
Photos are analysed with Google Gemini. AI assistants Chatgpt, Claude, Google AI, Lovable.ai helped draft code, documents and visuals. Our own work: choosing the problem, designing the features, taking and labelling photos, meeting contractors and collecting rates, testing, and writing the submission.

## What's next
Wood and other home problems, rates for more cities, voice input, login with city selection, saved history across devices.

## Team
Huma Nisar
, Kaneez Fatima
, Amina
