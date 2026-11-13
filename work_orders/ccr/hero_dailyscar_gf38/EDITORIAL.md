DailyScar: Field Notebook of Measured AI Failures.
Field records of operational drift, brittle verification, and shop-floor recovery.

### ACCESS CONTROL
#### The Unanswered Door
An automated bridge received three successive access denials and treated them as deliberate operator rejections, cycling immediately into retry spam. In reality, the operator had simply stepped away from the console. The automated client escalated retries against an empty desk instead of pausing to queue the pending work for later review.

**Law:** An unanswered prompt is not a policy refusal.  
**Instead:** Queue pending permissions when a human is away rather than spamming the approval bridge.

### CAPACITY PLANNING
#### Shoveling the Wrong Drive
When throughput lagged, the agent proposed moving 105 gigabytes of data across drives onto solid-state storage. The operator halted the migration: the bottleneck was elsewhere in the processing chain, and the transfer would have consumed hours without resolving the actual delay.

**Law:** Price the bottleneck before moving the data.  
**Instead:** Profile the actual constraint before staging a multi-gigabyte data transfer.

### EPHEMERAL STORAGE
#### Stranded in the Sandbox
A 2.7 megabyte deliverable shipped cleanly to external storage, but its build script remained behind on the temporary runner. A routine sweep was about to purge the ephemeral environment, which held the sole existing copy of the generator that produced the artifact.

**Law:** A deliverable is not archived until its generator leaves ephemeral disk.  
**Instead:** Sweep the builder into source control before calling the generated artifact complete.

### VERIFICATION GATES
#### The Ghost Patch
A shift handoff logged a backup script as patched and operational across the environment. In truth, nobody had run or inspected the modification on either target tree. The phantom fix remained logged as healthy until the script failed during live operation.

**Law:** A handoff that records an unverified fix is worse than one that records an open defect.  
**Instead:** Require verified execution proof before marking any handoff item resolved.

### NETWORK TELEMETRY
#### The Egress Wall
An agent ran diagnostic probes against cloud endpoints from inside an isolated sandbox. Every outbound request met an HTTP 403 error. The agent logged both production accounts as expired or dead, failing to realize the runner itself blocked outbound network egress by design.

**Law:** Runner network policy looks identical to credential failure from the inside.  
**Instead:** Distinguish local egress containment from upstream authentication errors before declaring remote services dead.

### BUFFER BOUNDARIES
#### Missing at Four Hundred Bytes
An automated rail monitor reported a required model missing from the provider catalog and raised an outage alert. The provider had returned the complete inventory, but the monitoring probe sliced the incoming response at 400 bytes, discarding the tail where the model name was listed.

**Law:** A truncated status buffer turns a healthy service into an alert.  
**Instead:** Read the complete payload before checking whether an item exists in the registry.

### BATCH RUNNERS
#### The Double Launcher
A batch generation process dispatched 204 automated node calls across five rounds. The runner was accidentally launched twice simultaneously, with the background instance continuing to overwrite and clobber restored source files an hour later while failing three out of four quality gates.

**Law:** Concurrency without single-instance locks turns a code generator into a demolition crew.  
**Instead:** Enforce process mutual exclusion before triggering multi-call batch generators.

### PATH VALIDATION
#### The Substring Perimeter
A filesystem safety guard checked whether file operations were contained within an authorized temporary directory. The verification relied on a naive substring match against the target path string, allowing unauthorized writes outside the designated tree to slip past unnoticed.

**Law:** Substring matching is not path containment.  
**Instead:** Resolve real paths to their canonical target and verify directory prefix boundaries.