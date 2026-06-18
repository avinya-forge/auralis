# Auralis Backlog

## 🎯 Current Sprint: Phase 7 Hybrid Intelligence

- **MILESTONE M2** | **PHASE 7: HYBRID INTELLIGENCE** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]

### Epic 6: Plugins & Security
> - **[ ] TASK:** net-001-p2p-security | **Loc:** src/modules/net/p2p_security.py | **Spec:** Implement P2PNetworkSecurity with libp2p and Noise | **Deps:** libp2p | **Hygiene:** [BLOCKED] | **LOC Estimate:** 150
### Epic 7: User Identity & Stats
> - **[ ] TASK:** id-004-stats-aggregator | **Loc:** src/modules/id/stats.py | **Spec:** Personal listening stats aggregation | **Deps:** src/utils/db_utils.py | **Hygiene:** [BLOCKED] | **LOC Estimate:** 60
> - **[ ] TASK:** id-005-profile-sync | **Loc:** src/modules/id/sync.py | **Spec:** Implement profile export/import (json) | **Deps:** json | **Hygiene:** [BLOCKED] | **LOC Estimate:** 80
### Epic 8: Cloud Backing
> - **[ ] TASK:** cld-002-aws-s3 | **Loc:** src/modules/cld/aws.py | **Spec:** Implement awsprovider for s3 backing | **Deps:** boto3 | **Hygiene:** [BLOCKED] | **LOC Estimate:** 90
> - **[ ] TASK:** cld-003-gdrive | **Loc:** src/modules/cld/gdrive.py | **Spec:** Implement googledriveprovider for drive backing | **Deps:** google-api | **Hygiene:** [BLOCKED] | **LOC Estimate:** 110
> ### Epic 9: System Maintenance
> > > ### Audit: DB/Auth/API Expansions
- **DB:** Validated schema expansions successfully integrate new multi-modal entities (Instruments, Gharanas) without data loss, meeting the Flat SSOT policy.
- **Auth:** Verified that external API endpoints correctly inherit generic Auth dependencies where applicable, maintaining isolation.
- **API:** Inspected streaming endpoints to ensure strict adherence to documented Swagger paths.

### [RESOLVE] Blockers
- **RESOLVE-NEW**: [BUG] `CloudSettingsWidget` is not integrated into `main_window.py` or any UI entry point. Cloud UI cannot be accessed.
- **RESOLVE-NEW**: [BUG] `validate_cloud_endpoint` in `cld-verify-connectivity` is never called. Needs integration into Cloud UI save/test flow.
- **RESOLVE-NEW**: [BUG] `prune_play_history` in `id-cleanup-history` is never scheduled or executed. Needs integration into an application lifecycle hook (e.g., startup/shutdown or a cron task).
