# Command Center Slice 1+2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the Command Center shell so it is driven by one normalized backend read model, updates live during committee runs, and replaces the old Overview flow cleanly.

**Architecture:** Keep Step 7 as the owner of the read model and static fallback artifacts. Keep Step 6 as a thin UI that loads one payload, merges live mission events in one store, and renders focused components for inbox, mission board, surveillance, exceptions, and takeover mode.

**Tech Stack:** FastAPI, Python 3.11+, pytest, React 19, Vite, Vitest, Testing Library, existing SSE endpoints

---

## File Structure

- `step7-automation/axe_orchestrator/projector.py`
  Purpose: normalize current artifacts into `command-center.json` and `missions/index.json`
- `step7-automation/axe_orchestrator/api.py`
  Purpose: serve `/api/command-center` and keep static fallback artifacts fresh after refreshes
- `step7-automation/tests/test_command_center_projector.py`
  Purpose: projector contract tests
- `step7-automation/tests/test_mission_index.py`
  Purpose: mission lifecycle index tests
- `step7-automation/tests/test_api.py`
  Purpose: API endpoint coverage
- `step6-dashboard/src/lib/command-center/store.js`
  Purpose: one loader + merge point for normalized command-center state
- `step6-dashboard/src/lib/command-center/stream.js`
  Purpose: subscribe to committee SSE and translate events into store updates
- `step6-dashboard/src/lib/command-center/store.test.jsx`
  Purpose: store load + merge tests
- `step6-dashboard/src/components/CommandCenter.jsx`
  Purpose: top-level composition only, no raw artifact parsing
- `step6-dashboard/src/components/command-center/DecisionInbox.jsx`
  Purpose: render normalized inbox items
- `step6-dashboard/src/components/command-center/LiveMissionBoard.jsx`
  Purpose: render mission rows and selection
- `step6-dashboard/src/components/command-center/FirmExceptions.jsx`
  Purpose: render degraded/stale issues only
- `step6-dashboard/src/components/command-center/WatcherGrid.jsx`
  Purpose: render watcher status summaries
- `step6-dashboard/src/components/command-center/SurveillanceBoard.jsx`
  Purpose: render surveillance alerts
- `step6-dashboard/src/components/command-center/MissionTakeover.jsx`
  Purpose: render selected mission details, stream/disconnect state, evidence links
- `step6-dashboard/src/components/CommandCenter.test.jsx`
  Purpose: command-center composition tests
- `step6-dashboard/src/components/command-center/MissionTakeover.test.jsx`
  Purpose: takeover behavior tests
- `step6-dashboard/src/App.jsx`
  Purpose: make Command Center the real Overview replacement

---

### Task 1: Harden The Backend Read Model

**Files:**
- Modify: `step7-automation/axe_orchestrator/projector.py`
- Modify: `step7-automation/axe_orchestrator/api.py`
- Test: `step7-automation/tests/test_command_center_projector.py`
- Test: `step7-automation/tests/test_mission_index.py`
- Test: `step7-automation/tests/test_api.py`

- [ ] **Step 1: Write the failing backend tests for missing lifecycle fields**

```python
def test_build_mission_index_marks_active_and_terminal_states(tmp_path):
    # running mission keeps ended_at=None
    # failed mission maps to failed
    # success mission maps to completed
    ...
```

- [ ] **Step 2: Run the backend tests to verify failure**

Run:
```bash
/home/tiger/.openclaw/workspace/projects/Axe-Capital/.venv/bin/python -m pytest \
  tests/test_command_center_projector.py \
  tests/test_mission_index.py \
  tests/test_api.py -q
```

Expected:
- at least one new assertion fails on missing lifecycle or fallback fields

- [ ] **Step 3: Extend the projector with the missing normalized fields**

Add fields directly in `projector.py`:

```python
mission = {
    "run_id": run_id,
    "status": _mission_status(run.get("status")),
    "started_at": run.get("started_at"),
    "updated_at": run.get("ended_at") or run.get("started_at"),
    "ended_at": run.get("ended_at"),
    "headline": run.get("summary") or "",
    "latest_summary": run.get("summary") or "",
    "source_updated_at": run.get("ended_at") or run.get("started_at"),
    "staleness_state": "fresh",
}
```

- [ ] **Step 4: Keep the static fallback artifacts written from one function**

Use the writer shape below and do not duplicate file writes elsewhere:

```python
def write_command_center_artifacts(public: Path) -> None:
    payload = build_command_center_payload(public)
    mission_index = build_mission_index(public)
    (public / "command-center.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    ...
```

- [ ] **Step 5: Run the backend tests to verify green**

Run:
```bash
/home/tiger/.openclaw/workspace/projects/Axe-Capital/.venv/bin/python -m pytest \
  tests/test_command_center_projector.py \
  tests/test_mission_index.py \
  tests/test_api.py -q
```

Expected:
- `N passed`

- [ ] **Step 6: Commit**

```bash
git add \
  step7-automation/axe_orchestrator/projector.py \
  step7-automation/axe_orchestrator/api.py \
  step7-automation/tests/test_command_center_projector.py \
  step7-automation/tests/test_mission_index.py \
  step7-automation/tests/test_api.py
git commit -m "feat: harden command center read model"
```

---

### Task 2: Add Live Mission Streaming To The Store

**Files:**
- Create: `step6-dashboard/src/lib/command-center/stream.js`
- Modify: `step6-dashboard/src/lib/command-center/store.js`
- Modify: `step6-dashboard/src/App.jsx`
- Test: `step6-dashboard/src/lib/command-center/store.test.jsx`

- [ ] **Step 1: Write the failing store test for live SSE merges**

```jsx
it('merges committee stream events into the selected mission', () => {
  const next = mergeMissionEvent(state, {
    run_id: 'GOOG-1be743bb',
    status: 'running',
    latest_summary: 'risk review complete',
    updated_at: '2026-04-21T00:13:00Z',
  })
  expect(next.current_focus.latest_summary).toBe('risk review complete')
})
```

- [ ] **Step 2: Run the frontend store tests to verify failure**

Run:
```bash
npm test -- --run src/lib/command-center/store.test.jsx
```

Expected:
- new merge or subscribe test fails

- [ ] **Step 3: Add the stream helper**

Create `stream.js`:

```js
import { createCommitteeStream } from '../api'

export function subscribeToMission(runId, handlers) {
  if (!runId) return () => {}
  const source = createCommitteeStream(runId, handlers)
  return () => source?.close?.()
}
```

- [ ] **Step 4: Wire App-level subscription through the store**

Keep one subscription owner in `App.jsx`:

```jsx
useEffect(() => {
  if (!commandCenter?.current_focus?.run_id) return
  return subscribeToMission(commandCenter.current_focus.run_id, {
    onEvent(event) {
      setCommandCenter((current) => mergeMissionEvent(current, event))
    },
    onError(error) {
      setCommandCenter((current) => mergeMissionEvent(current, {
        run_id: current?.current_focus?.run_id,
        stream_error: error.message,
        updated_at: new Date().toISOString(),
      }))
    },
  })
}, [commandCenter?.current_focus?.run_id])
```

- [ ] **Step 5: Run the frontend store tests to verify green**

Run:
```bash
npm test -- --run src/lib/command-center/store.test.jsx
```

Expected:
- store tests pass

- [ ] **Step 6: Commit**

```bash
git add \
  step6-dashboard/src/lib/command-center/store.js \
  step6-dashboard/src/lib/command-center/stream.js \
  step6-dashboard/src/lib/command-center/store.test.jsx \
  step6-dashboard/src/App.jsx
git commit -m "feat: stream live mission updates into command center"
```

---

### Task 3: Split The Command Center Into Focused Components

**Files:**
- Modify: `step6-dashboard/src/components/CommandCenter.jsx`
- Create: `step6-dashboard/src/components/command-center/DecisionInbox.jsx`
- Create: `step6-dashboard/src/components/command-center/LiveMissionBoard.jsx`
- Create: `step6-dashboard/src/components/command-center/FirmExceptions.jsx`
- Create: `step6-dashboard/src/components/command-center/WatcherGrid.jsx`
- Create: `step6-dashboard/src/components/command-center/SurveillanceBoard.jsx`
- Create: `step6-dashboard/src/components/command-center/MissionTakeover.jsx`
- Test: `step6-dashboard/src/components/CommandCenter.test.jsx`
- Test: `step6-dashboard/src/components/command-center/MissionTakeover.test.jsx`

- [ ] **Step 1: Write the failing Mission Takeover test**

```jsx
it('shows disconnect state when the mission stream drops', () => {
  render(<MissionTakeover mission={{ run_id: 'GOOG-1be743bb', stream_error: 'Committee stream disconnected' }} />)
  expect(screen.getByText('Committee stream disconnected')).toBeInTheDocument()
})
```

- [ ] **Step 2: Run the component tests to verify failure**

Run:
```bash
npm test -- --run src/components/CommandCenter.test.jsx src/components/command-center/MissionTakeover.test.jsx
```

Expected:
- `MissionTakeover` import or assertion fails

- [ ] **Step 3: Create the focused components**

Use `CommandCenter.jsx` as composition only:

```jsx
<DecisionInbox items={payload.decision_inbox} />
<LiveMissionBoard missions={payload.live_missions} selectedRunId={selectedRunId} onSelect={setSelectedRunId} />
<FirmExceptions items={payload.firm_exceptions} />
<WatcherGrid items={payload.watchers} />
<SurveillanceBoard items={payload.surveillance_alerts} />
<MissionTakeover mission={selectedMission} />
```

- [ ] **Step 4: Make Mission Takeover show real live state**

Include:

```jsx
{mission?.stream_error && (
  <div className="ui-badge text-red-300 border-red-700/60 bg-red-900/10">
    {mission.stream_error}
  </div>
)}
```

And render:
- run id
- status
- latest summary
- updated time
- placeholder evidence links block fed from normalized payload when available

- [ ] **Step 5: Run the component tests to verify green**

Run:
```bash
npm test -- --run src/components/CommandCenter.test.jsx src/components/command-center/MissionTakeover.test.jsx
```

Expected:
- all component tests pass

- [ ] **Step 6: Commit**

```bash
git add \
  step6-dashboard/src/components/CommandCenter.jsx \
  step6-dashboard/src/components/command-center \
  step6-dashboard/src/components/CommandCenter.test.jsx
git commit -m "refactor: split command center into focused surfaces"
```

---

### Task 4: Remove Overview Duplication And Verify The Shell

**Files:**
- Modify: `step6-dashboard/src/App.jsx`
- Modify: `step6-dashboard/src/components/AppSidebar.jsx`
- Test: `step6-dashboard/src/lib/command-center/store.test.jsx`
- Test: `step6-dashboard/src/components/CommandCenter.test.jsx`

- [ ] **Step 1: Write the failing test for fallback artifact load**

```jsx
it('falls back to /command-center.json when /api/command-center fails', async () => {
  ...
})
```

- [ ] **Step 2: Run the targeted frontend tests to verify failure**

Run:
```bash
npm test -- --run src/lib/command-center/store.test.jsx src/components/CommandCenter.test.jsx
```

Expected:
- fallback assertion fails before the final cleanup is wired

- [ ] **Step 3: Keep Overview fully delegated to Command Center**

`App.jsx` should keep this shape:

```jsx
{activeTab === 'overview' && (
  commandCenterError
    ? <div className="panel-card text-sm text-red-300">...</div>
    : <CommandCenter payload={commandCenter} />
)}
```

Do not reintroduce direct `portfolio.json` or `decision-latest.json` fetches into the Overview branch.

- [ ] **Step 4: Verify nav language is consistent**

Keep `AppSidebar.jsx` and `TAB_LABELS.overview` aligned:

```jsx
{ id: 'overview', label: 'Command Center', ... }
```

- [ ] **Step 5: Run full frontend verification**

Run:
```bash
npm test -- --run src/lib/command-center/store.test.jsx src/components/CommandCenter.test.jsx src/components/command-center/MissionTakeover.test.jsx
npm run build
```

Expected:
- tests pass
- Vite build succeeds

- [ ] **Step 6: Commit**

```bash
git add \
  step6-dashboard/src/App.jsx \
  step6-dashboard/src/components/AppSidebar.jsx \
  step6-dashboard/src/components/CommandCenter.test.jsx \
  step6-dashboard/src/lib/command-center/store.test.jsx
git commit -m "feat: make command center the real overview shell"
```

---

### Task 5: Final Review + QA Gate

**Files:**
- Modify: none expected unless review/QA finds issues
- Test input: `~/.gstack/projects/Default-to-AI-openclaw-workspace/tiger-main-eng-review-test-plan-20260421-070153.md`

- [ ] **Step 1: Run backend verification**

Run:
```bash
/home/tiger/.openclaw/workspace/projects/Axe-Capital/.venv/bin/python -m pytest \
  step7-automation/tests/test_command_center_projector.py \
  step7-automation/tests/test_mission_index.py \
  step7-automation/tests/test_api.py -q
```

Expected:
- backend tests pass

- [ ] **Step 2: Run frontend verification**

Run:
```bash
cd step6-dashboard
npm test -- --run \
  src/lib/command-center/store.test.jsx \
  src/components/CommandCenter.test.jsx \
  src/components/command-center/MissionTakeover.test.jsx
npm run build
```

Expected:
- frontend tests pass
- production build succeeds

- [ ] **Step 3: Run gstack review**

Run:
```text
/review
```

Expected:
- diff review findings addressed or accepted explicitly

- [ ] **Step 4: Run gstack QA**

Run:
```text
/qa
```

Expected:
- live shell flow checked against the QA artifact and fixed if needed

- [ ] **Step 5: Commit the final fixes**

```bash
git add step6-dashboard step7-automation
git commit -m "feat: finish command center slice 1 and 2"
```

---

## Spec Coverage Check

- normalized read model: covered in Task 1
- mission lifecycle contract: covered in Task 1
- live mission updates: covered in Task 2
- mission takeover behavior: covered in Task 3
- overview replacement: covered in Task 4
- review and QA gate: covered in Task 5

## Notes

- This plan deliberately excludes `Slice 3` runtime autonomy work.
- Do not add new scheduler, queue, or worker infrastructure in this plan.
- Keep the diff boring: one backend read model, one frontend store, focused components, tests first.
