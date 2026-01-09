#!/bin/bash
# Generate HTML pages from templates for GitHub Pages deployment

set -e

TEMPLATES_DIR=".github/pages-templates"
PAGES_DIR="pages"
HISTORY_DIR="$PAGES_DIR/history"
COMMIT_SHA="${1:-${GITHUB_SHA}}"
COMMIT_SHORT="${COMMIT_SHA:0:7}"
SUMMARY_JSON="${2:-mutation-reports/mutation-summary.json}"

# Function to replace placeholders in template
replace_placeholders() {
  local template_file="$1"
  local output_file="$2"
  
  # Read template and replace placeholders
  sed \
    -e "s|{{MUTATION_SCORE}}|${MUTATION_SCORE}|g" \
    -e "s|{{TOTAL_JOBS}}|${TOTAL_JOBS}|g" \
    -e "s|{{TOTAL_COMPLETE}}|${TOTAL_COMPLETE}|g" \
    -e "s|{{TOTAL_KILLED}}|${TOTAL_KILLED}|g" \
    -e "s|{{TOTAL_SURVIVING}}|${TOTAL_SURVIVING}|g" \
    -e "s|{{COMMIT_SHORT}}|${COMMIT_SHORT}|g" \
    -e "s|{{TIMESTAMP}}|${TIMESTAMP}|g" \
    -e "s|{{MODULE_CARDS}}|${MODULE_CARDS}|g" \
    -e "s|{{HISTORY_ITEMS}}|${HISTORY_ITEMS}|g" \
    "$template_file" > "$output_file"
}

# Read summary JSON if available
if [ -f "$SUMMARY_JSON" ] && command -v jq &> /dev/null; then
  TOTAL_JOBS=$(jq -r '.summary.total_jobs // 0' "$SUMMARY_JSON")
  TOTAL_COMPLETE=$(jq -r '.summary.total_complete // 0' "$SUMMARY_JSON")
  TOTAL_KILLED=$(jq -r '.summary.total_killed // 0' "$SUMMARY_JSON")
  TOTAL_SURVIVING=$(jq -r '.summary.total_surviving // 0' "$SUMMARY_JSON")
  MUTATION_SCORE=$(jq -r '.summary.mutation_score // 0' "$SUMMARY_JSON")
  COMMIT_SHORT=$(jq -r '.commit_short // "'"${COMMIT_SHORT}"'"' "$SUMMARY_JSON")
  TIMESTAMP=$(jq -r '.timestamp // "'"$(date -u +"%Y-%m-%dT%H:%M:%SZ")"'"' "$SUMMARY_JSON")
else
  # Fallback: parse manually or use defaults
  if [ -f "$SUMMARY_JSON" ]; then
    TOTAL_JOBS=$(grep -o '"total_jobs":[0-9]*' "$SUMMARY_JSON" | grep -o '[0-9]*' | head -1 || echo "0")
    TOTAL_COMPLETE=$(grep -o '"total_complete":[0-9]*' "$SUMMARY_JSON" | grep -o '[0-9]*' | head -1 || echo "0")
    TOTAL_KILLED=$(grep -o '"total_killed":[0-9]*' "$SUMMARY_JSON" | grep -o '[0-9]*' | head -1 || echo "0")
    TOTAL_SURVIVING=$(grep -o '"total_surviving":[0-9]*' "$SUMMARY_JSON" | grep -o '[0-9]*' | head -1 || echo "0")
    MUTATION_SCORE=$(grep -o '"mutation_score":[0-9.]*' "$SUMMARY_JSON" | grep -o '[0-9.]*' | head -1 || echo "0")
    COMMIT_SHORT=$(grep -o '"commit_short":"[^"]*"' "$SUMMARY_JSON" | sed 's/"commit_short":"\([^"]*\)"/\1/' | head -1 || echo "${COMMIT_SHORT}")
    TIMESTAMP=$(grep -o '"timestamp":"[^"]*"' "$SUMMARY_JSON" | sed 's/"timestamp":"\([^"]*\)"/\1/' | head -1 || echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ")")
  else
    TOTAL_JOBS=0
    TOTAL_COMPLETE=0
    TOTAL_KILLED=0
    TOTAL_SURVIVING=0
    MUTATION_SCORE=0
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  fi
fi

# Create directories
mkdir -p "$PAGES_DIR"
mkdir -p "$HISTORY_DIR"
mkdir -p "$HISTORY_DIR/$COMMIT_SHORT"

# Check if mutation reports exist
if [ ! -d "mutation-reports" ] || [ -z "$(find mutation-reports -name 'report.html' 2>/dev/null)" ]; then
  echo "⚠️ No mutation reports found. Creating placeholder page."
  cp "$TEMPLATES_DIR/placeholder.html" "$PAGES_DIR/index.html"
  exit 0
fi

# Generate module cards HTML
MODULE_CARDS=""
if [ -d "mutation-reports" ]; then
  while IFS= read -r report_file; do
    # Extract module name
    module=$(echo "$report_file" | sed -E 's|^mutation-reports/+||' | sed -E 's|/report\.html$||' | sed -E 's|^mutation-reports/+||')
    module=$(basename "$module")
    
    if [ -n "$module" ] && [ "$module" != "mutation-reports" ] && [ "$module" != "." ] && [ "$module" != "report.html" ]; then
      MODULE_CARDS="${MODULE_CARDS}              <div class=\"module-card\">
                <a href=\"$module/report.html\">$module</a>
              </div>
"
    fi
  done < <(find mutation-reports -name "report.html" -type f)
fi

# Generate index page
replace_placeholders "$TEMPLATES_DIR/index.html" "$PAGES_DIR/index.html"

# Generate history items HTML
HISTORY_ITEMS=""
if [ -d "$HISTORY_DIR" ]; then
  for commit_dir in "$HISTORY_DIR"/*/; do
    if [ -d "$commit_dir" ] && [ -f "$commit_dir/summary.json" ]; then
      commit=$(basename "$commit_dir")
      
      if command -v jq &> /dev/null; then
        score=$(jq -r '.summary.mutation_score // 0' "$commit_dir/summary.json")
        jobs=$(jq -r '.summary.total_jobs // 0' "$commit_dir/summary.json")
        complete=$(jq -r '.summary.total_complete // 0' "$commit_dir/summary.json")
        killed=$(jq -r '.summary.total_killed // 0' "$commit_dir/summary.json")
        surviving=$(jq -r '.summary.total_surviving // 0' "$commit_dir/summary.json")
        timestamp=$(jq -r '.timestamp // ""' "$commit_dir/summary.json")
      else
        score=$(grep -o '"mutation_score":[0-9.]*' "$commit_dir/summary.json" | grep -o '[0-9.]*' | head -1 || echo "0")
        jobs=$(grep -o '"total_jobs":[0-9]*' "$commit_dir/summary.json" | grep -o '[0-9]*' | head -1 || echo "0")
        complete=$(grep -o '"total_complete":[0-9]*' "$commit_dir/summary.json" | grep -o '[0-9]*' | head -1 || echo "0")
        killed=$(grep -o '"total_killed":[0-9]*' "$commit_dir/summary.json" | grep -o '[0-9]*' | head -1 || echo "0")
        surviving=$(grep -o '"total_surviving":[0-9]*' "$commit_dir/summary.json" | grep -o '[0-9]*' | head -1 || echo "0")
        timestamp=$(grep -o '"timestamp":"[^"]*"' "$commit_dir/summary.json" | sed 's/"timestamp":"\([^"]*\)"/\1/' | head -1 || echo "")
      fi
      
      HISTORY_ITEMS="${HISTORY_ITEMS}              <div class=\"history-item\">
                <div class=\"history-info\">
                  <h3>Commit: $commit</h3>
                  <p style=\"color: #666; margin: 5px 0;\">$timestamp</p>
                  <div class=\"history-stats\">
                    <div class=\"history-stat\">
                      <div class=\"history-stat-value\">$score%</div>
                      <div class=\"history-stat-label\">Score</div>
                    </div>
                    <div class=\"history-stat\">
                      <div class=\"history-stat-value\">$jobs</div>
                      <div class=\"history-stat-label\">Jobs</div>
                    </div>
                    <div class=\"history-stat\">
                      <div class=\"history-stat-value\">$complete</div>
                      <div class=\"history-stat-label\">Complete</div>
                    </div>
                    <div class=\"history-stat\">
                      <div class=\"history-stat-value\" style=\"color: #4ade80;\">$killed</div>
                      <div class=\"history-stat-label\">Killed</div>
                    </div>
                    <div class=\"history-stat\">
                      <div class=\"history-stat-value\" style=\"color: #f87171;\">$surviving</div>
                      <div class=\"history-stat-label\">Surviving</div>
                    </div>
                  </div>
                </div>
                <a href=\"$commit/summary.json\" class=\"history-link\" download>Download JSON</a>
              </div>
"
    fi
  done
fi

# Generate history index page
replace_placeholders "$TEMPLATES_DIR/history-index.html" "$HISTORY_DIR/index.html"

# Copy module reports to pages directory and history
if [ -d "mutation-reports" ]; then
  echo ""
  echo "=== Copying reports to pages directory ==="
  find mutation-reports -name "report.html" -type f | while IFS= read -r report_file; do
    # Extract module name
    module=$(echo "$report_file" | sed -E 's|^mutation-reports/+||' | sed -E 's|/report\.html$||' | sed -E 's|^mutation-reports/+||')
    module=$(basename "$module")
    
    if [ -n "$module" ] && [ "$module" != "mutation-reports" ] && [ "$module" != "." ] && [ "$module" != "report.html" ]; then
      echo "Copying $report_file to $PAGES_DIR/$module/report.html"
      mkdir -p "$PAGES_DIR/$module"
      cp "$report_file" "$PAGES_DIR/$module/report.html" && echo "  ✓ Success: $module" || echo "  ✗ Failed: $module"
      
      # Also copy to history directory
      mkdir -p "$HISTORY_DIR/$COMMIT_SHORT/$module"
      cp "$report_file" "$HISTORY_DIR/$COMMIT_SHORT/$module/report.html" && echo "  ✓ History: $module" || echo "  ✗ History failed: $module"
    fi
  done
fi

echo ""
echo "✅ Pages generated successfully"
echo "  - Index: $PAGES_DIR/index.html"
echo "  - History: $HISTORY_DIR/index.html"
echo "  - Current run stored in: $HISTORY_DIR/$COMMIT_SHORT/"

