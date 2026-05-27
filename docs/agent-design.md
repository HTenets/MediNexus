# Agent Design

## BaseAgent

All agents extend `BaseAgent` providing:
- Tool calling interface
- Pre/post processing hooks
- Structured handover via `HandoverManifest`
- Identity verification pre-hook

## Agent Types

| Agent | Role | Status |
|-------|------|--------|
| TriageAgent | Symptom triage, department routing | Core |
| DoctorAgent | Diagnosis via Skill system | Core |
| ReviewAgent | Prescription safety review | Core |
| CoordinatorAgent | Multi-specialty consultation | Core |
| FollowupAgent | Post-visit scheduling & monitoring | Core |
