# Examples

Runnable scripts that demonstrate one or more modules **without** using the full menu in `main.py`. Use them for quick demos, debugging, or learning the API.

## Scripts

| Script | What it shows | How to run |
|--------|----------------|------------|
| **demo_detection.py** | Mock sensor in manual, random, scenario, and interactive modes; detector events (VEHICLE_DETECTED / NO_VEHICLE). | `python examples/demo_detection.py` |
| **demo_database.py** | VehicleDB: add/remove vehicles, list all, fuzzy plate match. | `python examples/demo_database.py` |
| **demo_integration.py** | Detector + DB together: events logged to DB, then recent events listed. | `python examples/demo_integration.py` |

Run from the **project root** so imports resolve (`src` is on the path).

## Possible enhancements

- **demo_scenario.py** — Run a single scenario (e.g. `quick_pass`) non-interactively and print step-by-step output (useful for scripts or CI).
- **demo_fuzzy.py** — Call `check_plate_authorization()` from `src.fuzzy_logic` with a few plate strings and print authorized / best match / score.
- **demo_dashboard_api.py** — With the dashboard running, fetch `GET /api/events` and `GET /api/scenarios` and print a short summary (no browser needed).
