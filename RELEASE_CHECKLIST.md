# Release checklist

Before any GitHub publication:

1. Generate and inspect the proposed file list; never stage the full directory blindly.
2. Confirm that `90_local_only/`, `03_experiments/outputs/`, third-party source trees, caches, logs, and binaries are ignored.
3. Search tracked content for API keys, credentials, usernames, private paths, and accidental model responses.
4. Verify every paper, dataset, benchmark, and external-tool artifact has an explicit redistribution license.
5. Ensure the README describes the cascade correctly: dynamic results feed static analysis; it is not a simple slice intersection.
6. Ensure every headline metric links to a reviewed report or structured result and clearly states its validation level.
7. Re-run documented commands or state the required environment and any unresolved limitation.
8. Review the contribution statement so it distinguishes original work from external tools and datasets.
