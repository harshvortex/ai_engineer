# Level-7 Auto GitHub Engineer

An autonomous GitHub maintenance agent that intelligently maintains multiple repositories and generates human-like contribution activity.

## Architecture

Modular Python architecture for stability and maintainability.

- **`engine/analyzer.py`**: Analyzes repository structure, language, README quality, and inactivity metrics.
- **`engine/planner.py`**: Chooses the optimal next action using a weighted scoring algorithm.
- **`engine/executor.py`**: Safely performs updates such as `README.md` refreshes or `CHANGELOG.md` generation.
- **`engine/behavior.py`**: Introduces RNG logic such as daily execution skips or commit push delays to simulate human timings.
- **`engine/reporter.py`**: Prevents spam by logging recent tasks.

## Setup Instructions

1. **Deploy to GitHub:** Create this repository in your GitHub account.
2. **Setup Secrets:** Ensure you generate a Fine-Grained Personal Access Token (PAT) with Read/Write repository access. Navigate to `Settings -> Secrets and variables -> Actions` and setup `GH_TOKEN`.
3. **Configure the List:** Edit `config/repos.json` with the format `username/repository` for the codebases you want to maintain.

## Triggering Locally

You can run the script manually, passing an override setting to negate delays.

```bash
pip install -r requirements.txt
export GH_TOKEN=your_token_here
python main.py --no-delay
```
