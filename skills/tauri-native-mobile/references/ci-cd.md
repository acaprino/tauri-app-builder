# Shared build pipelines

Use target-compatible runners and separate native packaging from web/backend deployment. Default release builds do not require a custom Cargo release-profile block to become release builds; optimization settings are a separate choice.

Cache using complete relevant inputs, keep dependencies pinned, preserve symbols and artifact metadata, and make downstream jobs consume the artifact they actually validated. A signed binary and an updater signature solve different problems. Never assume a green frontend job validated mobile code.

For native pipelines, consult [mobile CI](ci-cd-mobile.md). For optional desktop packaging consult [desktop builds](build-deploy-desktop.md). Parallel jobs are a resource/latency decision, not a correctness rule.
