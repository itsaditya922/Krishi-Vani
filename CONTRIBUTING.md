# Contributing to KrishiVani

Thank you for your interest in contributing to KrishiVani! This guide will help you get started.

## Code of Conduct

- Be respectful and inclusive
- Focus on technical excellence
- Help others learn and grow
- Report issues constructively

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature
4. Make your changes
5. Test thoroughly
6. Submit a pull request

## Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/KrishiVani.git
cd KrishiVani
python -m venv .venv
.venv\Scripts\Activate  # On Windows
source .venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

## Making Changes

### Branch Naming
- Feature: `feature/description` (e.g., `feature/add-weather-endpoint`)
- Bug fix: `bugfix/issue-name` (e.g., `bugfix/fix-audio-transcription`)
- Documentation: `docs/description` (e.g., `docs/setup-guide`)

### Commit Messages
- Use clear, descriptive messages
- Use imperative mood ("Add feature" not "Added feature")
- Keep commits focused on one change
- Example: `"Add Hindi voice support for disease advice"`

### Code Style
- Follow PEP 8 conventions
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic
- Maintain readability

Example:
```python
def predict_disease(image_path: str, top_k: int = 3) -> list:
    """
    Predict crop disease from image.
    
    Args:
        image_path: Path to the crop image file
        top_k: Number of top predictions to return
    
    Returns:
        List of predictions with disease label and confidence
    """
    image = Image.open(image_path).convert("RGB")
    inputs = extractor(images=image, return_tensors='pt')
    
    with torch.no_grad():
        logits = model(**inputs).logits
    
    # Get top predictions
    probs = torch.softmax(logits, dim=-1)[0]
    top_indices = probs.topk(top_k).indices.tolist()
    
    results = []
    for idx in top_indices:
        label = model.config.id2label[idx]
        confidence = probs[idx].item() * 100
        results.append({
            "disease": label,
            "confidence": round(confidence, 4)
        })
    
    return results
```

## Testing

Before submitting, test your changes:

```bash
# Test syntax
python -m py_compile your_file.py

# Run test pipeline
python tests/test_pipeline.py

# Manual testing
python telegram_app.py  # or twilio_app.py
```

## Pull Request Process

1. Update `readme.md` if you've changed functionality
2. Add comments for complex changes
3. Ensure code follows project style
4. Reference any related issues: "Fixes #123"
5. Write clear PR description
6. Wait for review and address feedback

## PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Related Issues
Fixes #(issue number)

## Testing
How to test the changes

## Screenshots (if applicable)
Add screenshots for UI changes
```

## Areas to Contribute

### High Priority
- [ ] Improve crop disease prediction accuracy
- [ ] Add more crop types and diseases
- [ ] Support more languages
- [ ] Performance optimization

### Medium Priority
- [ ] Documentation improvements
- [ ] UI/UX enhancements
- [ ] Error handling
- [ ] Logging improvements

### Great for Beginners
- [ ] Documentation fixes
- [ ] Comments and docstrings
- [ ] Code examples
- [ ] Test cases

## Adding New Features

### Example: Adding a New Crop Disease

1. **Update the model** (`core/model.py`):
   - Use a trained model with the new disease class
   - Ensure `id2label` mapping includes it

2. **Update advice** (`core/agent.py`):
   - Add disease-specific advice to LLM prompts
   - Add treatment tips

3. **Test thoroughly**:
   - Test with sample images
   - Test language detection
   - Test voice response

4. **Update documentation**:
   - Add to supported crops list
   - Add examples

## Reporting Issues

Use GitHub Issues to report bugs:

**Title**: Brief description
**Description**: 
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages/logs
- Environment (OS, Python version, etc.)

Example:
```
Title: Audio transcription fails for Punjabi
Description:
Steps:
1. Send Punjabi audio note via Telegram
2. Bot receives the note
3. Transcription fails

Error: langdetect error on empty text
Python: 3.10
OS: Windows 11
```

## Questions?

- Check existing documentation
- Review past issues and discussions
- Start a new discussion if needed

## Recognition

Contributors will be:
- Added to `CONTRIBUTORS.md`
- Credited in release notes
- Mentioned in project updates

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

Thank you for helping make KrishiVani better! 🌱
