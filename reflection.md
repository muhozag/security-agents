# Capstone Project: AI-Augmented Prompt Injection Defense

## Project Summary

For this capstone, I built and evaluated an AI-based alternative to a common Blue Team defense: rule-based prompt injection filtering. My ultimate goal was to use a real application I previously built (a resume-generation platform) as my test case, since it already had a production-style regex-based filter I could measure against.

The goal was to answer a specific question: can an AI reasoning-based filter catch disguised attacks that a traditional keyword filter misses, and can I prove that with actual numbers instead of just claiming it?

## Engineering Work Done

- Threat identification and defense evaluation (prompt injection, filter bypass techniques)
- API integration with a commercial LLM (Anthropic Claude) for a security use case
- Secure software design: contract-based architecture, input validation, defensive parsing
- Containerization (Docker) and image publishing
- CI/CD pipeline design (GitHub Actions): automated linting, testing, and security scanning
- Static analysis and vulnerability scanning (bandit, Trivy)
- Independent debugging and root-cause analysis across a full stack (Python, YAML config, Docker, CI/CD)

## What I Built

**Two components connected by a shared interface and no code dependencies:**

1. **Red Team CLI** — an attack simulation tool. It takes known malicious phrases and disguises each one using seven different techniques (lookalike Unicode characters, invisible characters, spacing tricks, sentence splitting, paraphrasing, base64 encoding, leetspeak), then fires all the disguised versions at a target filter and reports how many got through.

2. **Guardian Service** — a standalone web service, built with FastAPI, that judges whether text is trying to manipulate an AI system. Instead of matching known bad phrases, it asks Claude to reason about intent, so it isn't fooled by disguises the same way a keyword filter is. It's packaged as a Docker container so it can run independently of any one application.

I designed these as two separate, swappable pieces rather than one combined script, connected by a shared format both agree on (a "contract"). This means the attack tool isn't hardwired to only test my app; it can test any filter that speaks the same format.

## How I Built It

1. **Proved the concept first**, quickly and cheaply, before committing to a full build: reconstructed the logic of my app's existing filter and confirmed it really was vulnerable to disguised attacks (75-83% bypass rate).
2. **Designed the shared interface** both tools would use, so I could build and test each one independently.
3. **Built and tested both components locally**: started the Guardian Service, manually confirmed it was really working, then ran the full automated attack sweep against it.
4. **Set up continuous integration (CI)**: every code push automatically runs a linter, my test suite, and a security scan of my own code.
5. **Set up continuous deployment (CD)**: tagging a release automatically builds a Docker image, scans it for known vulnerabilities, and publishes it, so the end result is a real, runnable artifact, not just source code.
6. **Verified the published image works standalone**: pulled it down fresh and ran it, confirming it works without needing my local setup at all.

## Results

| Defense | Bypass Rate |
|---|---|
| Original regex-based filter | 75-83% |
| AI-based Guardian Service | 17% |

The Guardian Service caught every single disguised attack using lookalike characters or leetspeak, both of which completely fooled the regex filter. The one attack that did get through was a paraphrased sentence that could plausibly be read as harmless on its own, a genuinely interesting edge case rather than a simple miss, and a good example of the real tradeoff any AI-based filter faces between catching more attacks and not being overly suspicious of normal language.

## Challenges and Lessons

- **Claude sometimes wrapped its answers in markdown formatting** even when told not to, which broke my code the first time. I fixed it by adding a cleanup step before parsing the response, a good lesson confirming that you shouldn't fully trust model output to follow formatting instructions perfectly, even when clearly asked.
- ** When I initially asked Claude for the Trivy component to include in the CD yaml file, it recommended an outdated version of the tool ** and, while checking for the latest version, discovered that specific tool had been the target of a real supply-chain attack earlier in the year, attackers had published a malicious version that stole credentials (see reference 4 below). Catching this while building a security tool was a genuinely valuable lesson: the tools you use to check security also need to be checked themselves.
- **Vulnerability scanning found real issues in the base container image**, not in my own code, but in underlying system packages with no fix released yet. This highlighted once again the difference between "a vulnerability exists" and "a vulnerability I can actually do something about right now," and shaped how I configured my pipeline to fail builds only over fixable issues.

## How I Plan to Use This on My Real Application

This project tested a rebuilt copy of my app's filter logic, not the live production code to keep things moving quickly while the design was still changing. The next steps to actually deploy this for real:

1. Test the Red Team CLI directly against my app's real filter file to get a verified baseline, not an approximation.
2. Add the Guardian Service as a second check inside my app's existing AI generation pipeline, running after the current filter, not replacing it.
3. Fix a related gap I identified in my app: it currently sends all content to Claude as plain user text with no separation between instructions and untrusted data. Adding a proper system role should strengthen that boundary.
4. Figure out a real cost and speed budget, since this would now run on live user traffic, not just test scripts.
5. Decide what should happen if the Guardian Service is slow or down: let requests through anyway, or block them until it responds. That's a real product decision I didn't have to make during testing.

## Conclusion

This project demonstrates that an AI-reasoning-based security check can meaningfully outperform a traditional keyword filter against disguised attacks, backed by real, repeatable numbers rather than a general claim. It also gave me hands-on experience with the full lifecycle of a security tool: building it, testing it, automating its deployment, and catching real issues (including in my own tooling choices) along the way.

## References

1. OWASP Foundation. *OWASP Top 10 for Large Language Model Applications.* https://owasp.org/www-project-top-10-for-large-language-model-applications/
2. Anthropic. *Claude API Documentation.* https://docs.claude.com
3. FastAPI. *FastAPI Documentation.* https://fastapi.tiangolo.com
4. StepSecurity. *Trivy Compromised a Second Time: Malicious v0.69.4 Release, aquasecurity/setup-trivy, aquasecurity/trivy-action GitHub Actions Compromised.* https://www.stepsecurity.io/blog/trivy-compromised-a-second-time---malicious-v0-69-4-release
5. Aqua Security. *Trivy: Vulnerability and Misconfiguration Scanner.* https://github.com/aquasecurity/trivy