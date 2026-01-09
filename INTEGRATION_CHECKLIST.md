# Quick Integration Checklist

Use this checklist to quickly integrate mutation testing, code quality checks, and dependency management into your CI/CD pipeline.

## Pre-Integration Checklist

- [ ] GitHub repository with Actions enabled
- [ ] Python project with test suite
- [ ] `requirements.txt` or `pyproject.toml` present
- [ ] Test files follow naming convention (`test_*.py`)

## Step-by-Step Integration

### Phase 1: Reusable Actions

- [ ] Create `.github/actions/setup-python-uv/action.yml`
- [ ] Create `.github/actions/mutation-test-module/action.yml`
- [ ] Test actions locally or in a test workflow

### Phase 2: Module Detection

- [ ] Create `.github/scripts/detect-modules.py`
- [ ] Configure `SOURCE_DIR` for your project structure
- [ ] Test module detection: `python .github/scripts/detect-modules.py`
- [ ] Verify output is valid JSON array

### Phase 3: Code Quality Checks

- [ ] Add `uv-lock-check` job (or skip if not using UV)
- [ ] Add `ruff-check` job
- [ ] Add `ruff-format-check` job
- [ ] Add `gitleaks-check` job
- [ ] Configure Ruff: Create `ruff.toml` or add to `pyproject.toml`
- [ ] Test each check locally

### Phase 4: Unit Tests

- [ ] Add `unit-tests` job
- [ ] Configure dependencies: `needs: [uv-lock-check, ruff-check, ...]`
- [ ] Add test execution and coverage reporting
- [ ] Verify tests run successfully

### Phase 5: Mutation Testing

- [ ] Add `mutation-setup` job
- [ ] Configure module detection output
- [ ] Add `mutation-test` job with matrix strategy
- [ ] Configure module paths and test commands
- [ ] Add artifact upload for each module
- [ ] Test mutation testing locally first

### Phase 6: Aggregation & Reporting

- [ ] Add `mutation-aggregate` job
- [ ] Configure artifact download
- [ ] Add summary generation using `cr-report`
- [ ] Add artifact upload for aggregated reports
- [ ] Test aggregation locally

### Phase 7: GitHub Pages Deployment

- [ ] Add `deployment` job
- [ ] Configure GitHub Pages permissions
- [ ] Add index page generation
- [ ] Configure artifact download
- [ ] Add Pages deployment steps
- [ ] Enable GitHub Pages in repository settings (if automatic fails)

### Phase 8: PR Notifications (Optional)

- [ ] Add `mutation-notify` job
- [ ] Configure PR comment generation
- [ ] Test notification format
- [ ] Verify PR comments appear correctly

## Configuration Checklist

### Project Structure Adaptation

- [ ] Identify source directory (`src/`, `app/`, `lib/`, etc.)
- [ ] Identify test directory (`tests/`, `test/`, etc.)
- [ ] Update `detect-modules.py` with correct paths
- [ ] Update `mutation-test-module` action with correct paths
- [ ] Verify module paths match your project structure

### Dependency Management

- [ ] Choose package manager: UV, pip, or poetry
- [ ] If using UV: Create/update `pyproject.toml` and `uv.lock`
- [ ] If using pip: Ensure `requirements.txt` is up-to-date
- [ ] If using poetry: Configure Poetry installation step
- [ ] Test dependency installation locally

### Mutation Testing Configuration

- [ ] Install Cosmic-Ray: `pip install cosmic-ray` or `uv pip install cosmic-ray`
- [ ] Test cosmic-ray commands locally
- [ ] Configure timeout in cosmic-ray config (default: 10.0 seconds)
- [ ] Adjust test command to disable coverage (`-p no:cov`)
- [ ] Test baseline: `cosmic-ray baseline config.toml`
- [ ] Test execution: `cosmic-ray exec config.toml db.sqlite`

### Code Quality Configuration

- [ ] Create `ruff.toml` or add `[tool.ruff]` to `pyproject.toml`
- [ ] Configure Ruff rules and line length
- [ ] Test Ruff locally: `ruff check .` and `ruff format --check .`
- [ ] Create `.gitleaksignore` if needed
- [ ] Test Gitleaks locally: `gitleaks detect --source .`

## Testing Checklist

### Local Testing

- [ ] Run code quality checks locally
- [ ] Run unit tests locally
- [ ] Test module detection script
- [ ] Test mutation testing on one module
- [ ] Verify HTML report generation
- [ ] Test artifact creation (simulate)

### Workflow Testing

- [ ] Push to feature branch
- [ ] Create pull request
- [ ] Verify all code quality checks pass
- [ ] Verify unit tests pass
- [ ] Verify mutation testing runs
- [ ] Check artifacts are created
- [ ] Verify PR comment appears (if configured)
- [ ] Merge to main/master
- [ ] Verify GitHub Pages deployment
- [ ] Check Pages URL is accessible

## Troubleshooting Checklist

### If Code Quality Checks Fail

- [ ] Check Ruff configuration
- [ ] Run `ruff format .` locally to auto-fix
- [ ] Update `uv.lock` if UV check fails
- [ ] Review Gitleaks findings

### If Mutation Testing Fails

- [ ] Verify module paths are correct
- [ ] Check test command runs successfully
- [ ] Verify cosmic-ray is installed
- [ ] Check baseline tests pass
- [ ] Increase timeout if tests are slow
- [ ] Verify database files are created

### If Deployment Fails

- [ ] Check GitHub Pages is enabled
- [ ] Verify permissions are set correctly
- [ ] Check artifact names match
- [ ] Verify index.html is generated
- [ ] Check Pages environment is configured

## Post-Integration Checklist

- [ ] Document project-specific configurations
- [ ] Update README with CI/CD information
- [ ] Set up branch protection rules (optional)
- [ ] Configure required status checks (optional)
- [ ] Monitor workflow execution times
- [ ] Review and optimize timeouts
- [ ] Set up notifications for failures (optional)

## Quick Reference

### Key Files to Create/Modify

```
.github/
├── workflows/
│   └── ci.yml                    # Main workflow
├── actions/
│   ├── setup-python-uv/
│   │   └── action.yml           # Python + UV setup
│   └── mutation-test-module/
│       └── action.yml           # Mutation testing
└── scripts/
    └── detect-modules.py         # Module detection
```

### Key Commands

```bash
# Module detection
python .github/scripts/detect-modules.py

# Code quality
uv tool run ruff check .
uv tool run ruff format --check .
uv lock --check
gitleaks detect --source .

# Mutation testing
cosmic-ray init config.toml db.sqlite
cosmic-ray baseline config.toml
cosmic-ray exec config.toml db.sqlite
cr-report db.sqlite --show-pending
cr-html db.sqlite > report.html
```

### Key Configuration Points

1. **Source Directory**: Update `SOURCE_DIR` in `detect-modules.py`
2. **Module Paths**: Update `module-path` in mutation-test action
3. **Test Paths**: Update `test-path` in mutation-test action
4. **Timeouts**: Adjust in cosmic-ray config files
5. **Permissions**: Ensure `pages: write` for deployment

## Success Criteria

✅ All code quality checks pass  
✅ Unit tests pass with coverage  
✅ Mutation testing runs for all modules  
✅ HTML reports are generated  
✅ Reports are deployed to GitHub Pages  
✅ PR comments show mutation results (if configured)  
✅ Workflow completes in reasonable time  

---

**Next Steps**: See `MUTATION_TESTING_INTEGRATION_GUIDE.md` for detailed documentation.

