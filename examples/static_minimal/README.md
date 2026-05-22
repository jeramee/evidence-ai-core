# Static minimal example

This example is a local-only smoke walkthrough for `evidence-ai-core`.

Input files:

```text
inputs/request.txt
inputs/source_a.md
```

From the repository root, create a packet:

```powershell
evidence-ai-core create-static --request-file .\examples\static_minimal\inputs\request.txt --source .\examples\static_minimal\inputs\source_a.md --output-root .\examples\static_minimal\packets
```

The command prints the packet directory path. Replace `<packet_id>` below with that directory name:

```powershell
evidence-ai-core verify .\examples\static_minimal\packets\<packet_id> --pretty
evidence-ai-core summary .\examples\static_minimal\packets\<packet_id> --pretty
evidence-ai-core hash-summary .\examples\static_minimal\packets\<packet_id> --pretty
```

This example only demonstrates static packet mechanics. It does not execute notebooks, call models, run retrieval, contact networks, mutate source control, validate scientific claims, or promote state.
