# Security Policy
Security of the Crafty Controller application is our top priority. As such, we take any and all security reports not already noted as out-of-scope or an accepted risk.

## Reporting a vulnerability
All reporting of security issues should be done through **confidential** issues in [GitLab](https://gitlab.com/crafty-controller/crafty-4/-/issues). Please follow the existing reporting template and ensure that the report includes all of the following:
- Crafty version.
- Install method and OS.
- Steps to reproduce security issue.
- Relevant screenshots or recordings.
- Other information you find relevant to the report.

## What to expect
Your issue will be reviewed by one of our team members, typically 72 hours depending on availability. As all Crafty staff are volunteers, time to response and time to patch availability may vary. We appreciate your patience as we work to improve the security posture of Crafty Controller.
### Review process
1. Team will perform initial triage and either confirm the issue or request further information
2. Issue is confirmed as legitimate, marked as duplicate, or marked as not applicable.
3. Scope of fix required is determined and a timeline is established.
4. Timeline of fix is communicated with reporter.
5. CVE number registered if applicable and security advisory written by Crafty team with credits to the reporter.
6. An official patch, the CVE submission, and the security advisory are published.
7. Full disclosure of the issue (including root cause, PoC if applicable, and the original issue) is published after 7 days since patch release or as long as is appropriate to allow adequate time for users to patch. Deviations from the standard 7-day disclosure will be communicated in advance.

### Bounties
Crafty Controller is a volunteer-run project entirely sustained by donations that support the infrastructure used to operate the project. As such, we are unable to sustain a monetary bug bounty program. All security reporters will be credited in the security advisory, CVE submission, and vulnerability disclosure.

## Resolution time

We take security of Crafty very seriously and will strive to resolve reported issues and publish a fix in a timely manner. As all of the Crafty team is made up of volunteers, we may not always reach these targets, but will do everything possible to ensure we do. We have the following resolution objectives for security issues based on vulnerability criticality:

- Critical (CVSSv3 9.0 or higher) - 7 days
- High (CVSSv3 7.0-9.0) - 30 days
- Medium (CVSSv3 4.0-6.9) - 60 days
- Low (CVSSv3 3.9 or lower) - 90 days or as needed

We follow the criticality definitions as defined by [NIST](https://nvd.nist.gov/vuln-metrics/cvss), but hints are provided in this document for convenience. We reserve the right to increase or decrease criticality based on sensitivity of the underlying portion of Crafty. For example, attacks against authentication likely merit higher criticality where attacks only affecting backup availability may merit lower criticality.

## Accepted Risks
### Server Process Execution
Crafty, by design, allows users to run essentially any software in their server. Attacks that use the server startup process (such as running cryptominers or spawning other malicious child processes) are considered accepted risks in Crafty. Super user permission is required to modify server execution commands, and file permissions are required to modify server files. Vulnerabilities found that bypass or work around these permissions can be submitted and reviewed.
