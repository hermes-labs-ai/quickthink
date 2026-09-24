# Research documentation checks

Run `scripts/check_research_hygiene.sh` from the repository root to check
required research documents and the run references in the registry index.
The script reports missing documents and broken references. A passing result
establishes documentation structure only; it does not validate experiment
methods, measurements, or conclusions.

Preserve actual model configuration, results, and limitations when repairing
links. See `docs/SESSION_CLOSEOUT_CHECKLIST.md` for contribution guidance.

## Historical archive limitations

The current archive is incomplete: the routing-policy file and 20 run traces
referenced by the registry are absent from this checkout. The checker therefore
reports missing documents and broken references even before a contributor makes
changes. These failures are evidence of unavailable records, not a passing
reproduction of those experiments.

Keep the checker strict and the historical rows intact. Restore records only
from a verifiable source; do not generate substitute results or remove references
just to obtain a passing check. Changes to available material should not add new
missing references. The registry explains which historical status labels it
preserves.
