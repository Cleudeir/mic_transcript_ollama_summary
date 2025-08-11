---
applyTo: '**'
---
## Test Policy
- NEVER create test files or testing code
- Do not generate files in `/tests/` directory
- Do not create files with `test_` prefix
- Focus on implementation and documentation

## Documentation Requirements
- Always create documentation in `/docs/` folder for new features
- Use descriptive markdown filenames
- Follow the project's documentation template
- Exception: README.md stays in root directory

## File Organization
- Source code: `/src/` folder
- Documentation: `/docs/` folder (except README.md)
- Configuration: Root or `/src/`
- Generated files: `/src/output/`

## Priority
1. Working functionality
2. Comprehensive documentation
3. Clean, maintainable code
4. User experience


## Code Organization and DRY Principle
- Always separate code into distinct files and folders based on functionality
- Group related code in dedicated modules within `/src/`
- Avoid code duplication by reusing functions, classes, or modules
- Refactor repeated logic into shared utilities or helper files
- Name folders and files descriptively to reflect their purpose