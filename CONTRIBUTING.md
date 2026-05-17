# contributing

this project is organized so map qa, perception checks, and benchmark work can be extended independently.

before opening a change, run:

```bash
PYTHONPATH=backend pytest backend/tests
```

keep validation rules deterministic and avoid adding results that cannot be reproduced from source map or sample data. if a rule needs production map assumptions, document those assumptions near the rule and add a small test payload.
