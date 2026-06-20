# CI/CD Pipeline Guide

This guide explains how to work with the automated CI/CD pipelines for the VendaMais Distribuidora platform.

## Overview

The CI/CD system consists of three workflows:

1. **PR Validation** — Runs on pull requests to verify code quality and tests
2. **Dev Deployment** — Automatically deploys to dev when code merges to main
3. **Staging/Production Deployment** — Manual (staging) and release-based (production) deployments

## Prerequisites

- Python 3.13+ installed locally
- Git and GitHub CLI (`gh` command)
- Azure CLI (`az` command) for production deployments

## Local Development

Before pushing code, run the quality checks locally to catch issues early:

```bash
# Install dev dependencies
pip install -r src/requirements-dev.txt

# Run linting
ruff check src/

# Run type checking
mypy src/

# Run tests with coverage
pytest tests/ --cov=src/
```

Configuration is in `pyproject.toml`.

## Pull Request Validation

When you open a pull request to `main`:

1. **Automatically triggered**: The `PR Validation` workflow runs
2. **Checks performed**:
   - Ruff linting (code style)
   - Mypy type checking (type safety)
   - Pytest unit tests (functional correctness)
   - Coverage reporting (code coverage metric)
3. **Result**: All checks must pass before merge is allowed

**If validation fails:**
- Read the error messages in the GitHub PR checks
- Fix the issues locally
- Push the fix to your branch
- Validation runs again automatically

**Common failures:**
- `E501: line too long` — Keep lines under 100 characters
- Type errors — Add type hints or use `# type: ignore` with a comment
- Test failures — Debug and fix the test locally

## Deploying to Dev

When code is merged to `main`:

1. **Automatically triggered**: The `Dev Deployment` workflow starts
2. **Steps**:
   - Checks out code
   - Installs dependencies (cached for speed)
   - Authenticates to Azure using OIDC
   - Deploys to `azfun-das2b-chris-dev` Function App
   - Runs health checks to verify deployment
3. **Result**: Dev environment is updated with the latest code

**Check deployment status:**
- Go to your GitHub repo → **Actions** → **Deploy to Dev**
- View logs to debug failures

## Deploying to Staging

To test in a staging environment before production:

1. Go to your GitHub repo → **Actions** → **Deploy to Staging/Production**
2. Click **Run workflow**
3. Select `staging` from the environment dropdown
4. Click **Run workflow**

**What happens:**
- Latest code from `main` is deployed to `azfun-das2b-chris-staging`
- Health checks verify the deployment
- You can test the staging environment before promoting to production

## Deploying to Production

Production deployments are tied to GitHub Releases. To deploy to production:

1. **Create a release** using semantic versioning:
   ```bash
   # Example: promote the current main to v0.1.0
   gh release create v0.1.0 --target main --title "Release v0.1.0" --notes "Initial production release"
   ```

2. **Workflow triggers automatically**:
   - Release is detected
   - `Deploy to Staging/Production` workflow runs the production job
   - Code at that tag is deployed to `azfun-das2b-chris` (production)
   - Health checks verify deployment success

3. **Check status** in GitHub Actions → **Deploy to Staging/Production** → production job logs

**Important:**
- Only create releases for well-tested code from `main`
- Use semantic versioning: `v0.1.0`, `v1.0.0`, `v1.1.0`
- Each release is independently deployable and traceable

## Monitoring Deployments

### GitHub Actions

View workflow status in your repo:
- **Actions** tab shows all workflow runs
- Click a workflow to see detailed logs
- Coverage reports available as artifacts for PR validations

### Azure Function Apps

Monitor deployment success:
- Dev: `azfun-das2b-chris-dev.azurewebsites.net`
- Staging: `azfun-das2b-chris-staging.azurewebsites.net`
- Production: `azfun-das2b-chris.azurewebsites.net`

## Troubleshooting

### PR validation fails but code looks fine

1. Run checks locally first: `ruff check src/ && mypy src/ && pytest tests/`
2. Review the specific error in the PR checks
3. Use `# type: ignore` for known mypy issues with explanation
4. Disable specific ruff rules in `pyproject.toml` if needed

### Deployment fails with "Azure login failed"

- Secrets may be missing or misconfigured
- Check GitHub repo **Settings** → **Secrets** → verify `AZURE_CLIENT_ID_*` secrets exist
- Ensure OIDC federation is configured in Azure for the dev/staging/prod apps

### Health check fails after deployment

- Function App may not be fully started (needs 15+ seconds)
- Check that the Function App exists in Azure
- Verify the app name in the workflow matches Azure resource name

### Need to rollback a failed deployment

For dev (auto-deployed):
1. Revert the bad commit locally
2. Push to main
3. Dev Deployment workflow redeploys with old code

For staging/production (manual releases):
1. Create a new release at an older, known-good tag
2. This triggers production deployment to that version
3. Or wait for deployment to succeed before creating the next release

## Secrets and Environment Variables

Each environment uses distinct Azure credentials stored in GitHub Secrets:

- **Dev**: `AZURE_CLIENT_ID_DEV`, `AZURE_TENANT_ID_DEV`, `AZURE_SUBSCRIPTION_ID_DEV`
- **Staging**: `AZURE_CLIENT_ID_STAGING`, `AZURE_TENANT_ID_STAGING`, `AZURE_SUBSCRIPTION_ID_STAGING`
- **Production**: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`

These are used for OIDC authentication. Never expose or commit secrets.

## Performance

- **PR validation** typically takes 2-3 minutes (includes testing)
- **Dev deployment** takes 5-10 minutes (includes Azure build)
- **Staging/production** take 5-10 minutes depending on code size

Pip dependency caching reduces times on subsequent runs.

## Next Steps

- Read the design document for implementation details: `openspec/changes/improve-cicd-pipeline/design.md`
- For questions about the pipeline, check Azure Functions docs: https://learn.microsoft.com/en-us/azure/azure-functions/
- For GitHub Actions syntax, see: https://docs.github.com/en/actions
