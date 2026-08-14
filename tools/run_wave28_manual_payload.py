#!/usr/bin/env python3
from __future__ import annotations

import build_wave28_manual_payload as wave28

wave28.OPTIONS[637] = (
    "A normal fibrinogen value reliably excludes disseminated intravascular coagulation from consideration",
    "Fibrinogen must be profoundly reduced at presentation for disseminated intravascular coagulation",
    "Fibrinogen may fall with consumption, but a normal or elevated value does not exclude DIC",
    "Fibrinogen has no useful role when evaluating suspected disseminated intravascular coagulation",
)

if __name__ == "__main__":
    wave28.main()
