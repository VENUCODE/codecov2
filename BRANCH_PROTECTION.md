# Branch Protection Setup Guide

This repository uses a two-layer enforcement system to ensure tests pass and coverage meets the minimum threshold (75%) before code reaches the `master` branch:

1. **Local Enforcement**: Pre-push Git hook (can be bypassed)
2. **Remote Enforcement**: CI/CD + Branch Protection (cannot be bypassed)

**Coverage Requirement**: Test coverage must be at least **75%** to push or merge code.

## Layer 1: Local Pre-Push Hook

The pre-push hook runs tests locally before allowing a push. This provides immediate feedback and prevents pushing failing code.

### Setup

Run the setup script once after cloning:

**Linux/macOS:**
```bash
chmod +x setup-git-hooks.sh
./setup-git-hooks.sh
```

**Windows:**
```cmd
setup-git-hooks.bat
```

Or manually configure:
```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-push
```

### How It Works

- Before each `git push`, the hook runs `pytest` with coverage check
- If tests pass **AND** coverage is ≥75%, the push proceeds
- If tests fail **OR** coverage is <75%, the push is blocked with an error message

### Bypassing (Not Recommended)

The hook can be bypassed with:
```bash
git push --no-verify
```

**Warning**: Bypassing the hook will still be blocked by CI/CD branch protection if tests fail.

## Layer 2: CI/CD Branch Protection

GitHub branch protection rules enforce that CI checks must pass before merging pull requests.

### Required Setup

1. **Navigate to Repository Settings**
   - Go to your repository on GitHub
   - Click **Settings** → **Branches**

2. **Add Branch Protection Rule**
   - Click **Add rule** or edit existing rule for `master`
   - Configure the following:

   **Branch name pattern:**
   ```
   master
   ```

   **Protect matching branches:**
   - ✅ **Require a pull request before merging**
     - ✅ Require approvals: `1` (optional, adjust as needed)
     - ✅ Dismiss stale pull request approvals when new commits are pushed
   
   - ✅ **Require status checks to pass before merging**
     - ✅ Require branches to be up to date before merging
     - **Status checks that are required:**
       - `Test Reporting / test-and-report` (or the exact job name from your workflow)
   
   - ✅ **Require conversation resolution before merging** (optional but recommended)
   
   - ✅ **Do not allow bypassing the above settings** (recommended for admins)

3. **Save the Rule**

### How It Works

- When a pull request is opened or updated, CI runs automatically
- The workflow runs tests with coverage check (minimum 75% required)
- If tests fail **OR** coverage is below 75%, the CI check fails
- GitHub blocks merging until the check passes
- Even repository admins cannot bypass (if configured)

### Testing Branch Protection

1. Create a branch with failing tests OR low coverage (<75%)
2. Open a pull request targeting `master`
3. Verify that the PR shows a failing CI check
4. Attempt to merge - it should be blocked
5. Fix the tests and/or improve coverage to ≥75%, then push again
6. Once CI passes, merging should be allowed

## Workflow Configuration

The CI workflow (`.github/workflows/test-reporting.yml`) is configured to:

- ✅ Run on `pull_request` events (opened, synchronize, reopened)
- ✅ Run on pushes to `master`/`main` (for monitoring)
- ✅ Fail the workflow if tests fail **OR** coverage is below 75% (required for branch protection)
- ✅ Enforce minimum 75% test coverage using `--cov-fail-under=75`
- ✅ Publish test results using both reporting actions

## Enforcement Summary

| Action | Local Hook | CI/CD | Result |
|--------|-----------|-------|--------|
| `git push` (tests pass, coverage ≥75%) | ✅ Pass | N/A | Push succeeds |
| `git push` (tests fail OR coverage <75%) | ❌ Block | N/A | Push blocked |
| `git push --no-verify` (tests fail OR coverage <75%) | ⚠️ Bypassed | ❌ Fail | Push succeeds, but PR merge blocked |
| PR merge (tests pass, coverage ≥75%) | N/A | ✅ Pass | Merge allowed |
| PR merge (tests fail OR coverage <75%) | N/A | ❌ Fail | Merge blocked |

## Troubleshooting

### Hook Not Running

1. Verify hooks path: `git config core.hooksPath`
2. Should show: `.githooks`
3. Check hook is executable: `ls -l .githooks/pre-push`
4. Re-run setup script if needed

### CI Not Running on PRs

1. Check workflow file exists: `.github/workflows/test-reporting.yml`
2. Verify workflow syntax is valid
3. Check GitHub Actions tab for errors
4. Ensure workflow triggers include `pull_request`

### Branch Protection Not Working

1. Verify branch protection rule is enabled
2. Check required status check name matches workflow job name exactly
3. Ensure "Require branches to be up to date" is enabled
4. Verify workflow has `permissions: checks: write`

## Security Notes

- Local hooks are **not secure** - they can be bypassed with `--no-verify`
- Branch protection is the **real enforcement** layer
- Always require CI checks to pass before merging
- Consider requiring admin approval for bypassing protection rules

