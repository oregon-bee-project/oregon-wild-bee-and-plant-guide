## Contributing Guide
Create pull requests for all code/repo changes with well documented descriptions and documentation. The contributions are reviewed by at least 2 other members so that there are multiple pairs of eyes to compare to our definition of done.
## Code of Conduct
Productivity Issues can be raised by anyone on the team. The QA Lead (Dylan) assesses the issue and communicates to the team member. The Project Management Lead (Kellen) enforces through a PIP and improvement should be taken by the end of the current sprint.
Communication Issues can be raised by anyone on the team. The Point of Contact Lead (Zach) addresses the issue and communicates to the team member. Solution is enforced through communication at regular Team Meeting by the end of the current sprint.
## Getting Started
A local server version of the web application will be created where code only in our github will be used to run. Limited security will be enforced initially due to open-source nature of code and data.
## Branching & Workflow
Branch naming convention will be feature/feature-description, bugfix/bugfix-description.
After a branch is finished, the flow will be: open a PR → receive 1 or more reviews → merge.
## Issues & Planning
Issues are brought up in meetings, or over the communication medium. They will follow the what, why, where, and when format. They will be addressed by the responsible member at first and then elevated to the whole team.
## Commit Messages
Conventional Commits. They contain a small description of change on commit. Written in present tense.
## Code Style, Linting & Formatting
Prettier Formatting, Clang linting, clean code style.
## Testing
Unit and Integration Tests: Ensuring code functionality and preventing regressions.
## Pull Requests & Reviews
PRs should be limited to one focused feature or bugfix. When creating a PR, members should fill out the pull request template. PRs will require one review to merge.
## CI/CD
The enforcing CI jobs are:
Unit and Integration Tests: Ensuring code functionality and preventing regressions.
Code Quality Scans: Using tools to analyze code for maintainability and potential bugs.
Security Scans: Identifying vulnerabilities in code, dependencies, and configurations.
Linting and Formatting: Enforcing consistent code style.
Compliance Checks: Validating configurations against organizational or industry standards.
## Security & Secrets
Use .env for credentials and do not commit to repo. If a vulnerability or security issue arises, notify team members and create a GitHub issue if steps need to be taken to address the issue. 
## Documentation Expectations
README will be updated by sprint iteration to reflect the current state of code. Pull requests and commits will be documented properly to speak to the evolution of the work and explicit changes made.
## Release Process
Follow a vX.X.X versioning scheme. Changelogs will be generated after each release, and if a release generates issues/is problematic, we will roll back to the previous working release.
## Support & Contact
The maintainer contact channel will be in the Bee and Flower Data Exploration Discord server. Any new maintainers will be added to the chat and questions can be asked in the general channel. We expect responses to be made within 24 hours. 
