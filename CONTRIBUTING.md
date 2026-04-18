# Contributing

We'd love your help improving the Claude Token Efficiency analyzer!

## What We Need

- **Bug reports**: Found an issue? Open an issue with reproduction steps
- **Feature ideas**: New metrics? Better visualizations? Tell us!
- **Pricing updates**: When Anthropic changes rates, submit a PR with updated `PRICING` dict
- **Documentation**: Clearer explanations, examples, edge cases
- **Translations**: Help make this available in other languages

## How to Contribute

### Reporting Bugs

1. Check [existing issues](https://github.com/yourusername/claude-token-efficiency/issues) first
2. Open a new issue with:
   - **Title**: Clear, short description
   - **Steps to reproduce**: What did you do?
   - **Expected vs actual**: What should happen vs. what happened?
   - **Environment**: Python version, OS, Claude Code version
   - **Screenshots**: If relevant (e.g., malformed output)

### Submitting Code

1. Fork the repo
2. Create a branch: `git checkout -b fix/your-fix-name`
3. Make your changes
4. Test: `python3 analyzer.py` and verify output looks good
5. Commit: `git commit -m "Fix: brief description of your change"`
6. Push: `git push origin fix/your-fix-name`
7. Open a PR with a clear description

**Code style**: 
- Follow PEP 8 (Python)
- Comment only non-obvious logic
- Keep functions focused

### Updating Pricing

When Anthropic announces new rates:

1. Edit `analyzer.py`, find the `PRICING` dict
2. Update the rates for each model
3. Open a PR titled "Update: Anthropic rates [YYYY-MM-DD]"

Example:
```python
PRICING = {
    "claude-sonnet-4-6": {
        "input": 3.0,      # was 3.0
        "output": 15.0,    # was 15.0
        "cache_read": 0.30,
        "cache_write": 3.75,
    },
    ...
}
```

### New Features

Want to add a new metric or visualization? 

1. **Open an issue first** to discuss the idea
2. Describe what insight it provides
3. Show a mockup or example
4. Discuss implementation approach

Examples of good feature ideas:
- Session-over-session trend analysis
- Export to CSV/JSON for external analysis
- Per-project token breakdown
- Projected costs for future usage
- Interactive HTML report (instead of terminal)

## Testing Your Changes

```bash
# Run the analyzer with your changes
python3 analyzer.py

# Verify:
# - No Python errors
# - All sections print correctly
# - Heatmap colors show (if your terminal supports them)
# - Numbers make sense (no negative tokens, etc.)
```

## PR Checklist

Before submitting:
- [ ] Code follows PEP 8
- [ ] No unnecessary imports or dead code
- [ ] Script runs without errors
- [ ] Output is readable and correctly formatted
- [ ] Commit message is clear and descriptive
- [ ] Related issue is referenced (if applicable)

## Questions?

- Open an issue labeled `question` or `discussion`
- We're here to help!

## License

By contributing, you agree your code will be released under the MIT License.

---

**Thank you for helping make Claude Token Efficiency better!**
