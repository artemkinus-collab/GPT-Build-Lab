# Security Policy

## Scope

GPT Build Lab is currently a prototype. It stores draft build descriptions in the visitor's browser and does not yet execute user-submitted builds.

## Reporting a concern

Please do not publish passwords, access tokens, private keys, signing keys, keystores, or personal data in issues or pull requests. If a sensitive value was accidentally committed, revoke or rotate it first; deleting it from the latest commit does not guarantee that it is gone from Git history.

For a security concern, contact the repository owner privately through GitHub rather than posting exploit details publicly.

## Safe use

- Treat all imported project descriptions and repository URLs as untrusted input.
- Keep workflow permissions minimal.
- Do not run unreviewed third-party build scripts with privileged credentials.
- Use repository or environment secrets only when a future workflow genuinely needs them.
- Review workflow and dependency updates before merging.
