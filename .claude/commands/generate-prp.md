# Create Product Requirements Prompt (PRP)

Generate a complete PRP (Product Requirements Prompt) for general feature implementation with thorough research. Ensure context is passed to the AI agent to enable self-validation and iterative refinement. Read the feature file first to understand what needs to be created, how the examples provided help, and any other considerations.

The AI agent only gets the context you are appending to the PRP and training data. Assume the AI agent has access to the codebase and the same knowledge cutoff as you, so its important that your research findings are included or referenced in the PRP. The Agent has Websearch capabilities, so pass urls to documentation and examples.

- Extract only the filename and extension from `$ARGUMENTS` into `$FILE_NAME`. Append extension `.md` if necessary.
- Use the paths defined in `context/config/paths.md`
- Important ! Write your outputs from CLI in real-time to the log file `Claude_GenPRP_${FILE_NAME}` in `$LOGS_CONTEXT_PATH`. Also include your itnernalt thinking steps. Use the configured time stamp formatting.
- `FEATURE_FILE = ${FEATURES_PATH}/${FILE_NAME}`
- `PRP_FILE = ${PRP_PATH}/${FILE_NAME}`
- `PRP_TEMPLATE = ${TEMPLATES_PATH}/${prp_base.md}`
- Input file: `$FEATURE_FILE`
- Output file: `$PRP_FILE`

## Research Process

1. **Codebase Analysis**
   - Search for similar features/patterns in the codebase
   - Identify files to reference in `$PRP_FILE`
   - Note existing conventions to follow
   - Check test patterns for validation approach

2. **External Research**
   - Search for similar features/patterns online
   - Library documentation (include specific URLs)
   - Implementation examples (GitHub/StackOverflow/blogs)
   - Best practices and common pitfalls

3. **User Clarification** (if needed)
   - Specific patterns to mirror and where to find them?
   - Integration requirements and where to find them?

## PRP Generation

- Use `$PRP_TEMPLATE` as template

### Critical Context to Include and pass to the AI agent as part of the PRP

- **Documentation**: URLs with specific sections
- **Code Examples**: Real snippets from codebase
- **Gotchas**: Library quirks, version issues
- **Patterns**: Existing approaches to follow

### Implementation Blueprint

- Start with pseudocode showing approach
- Reference real files for patterns
- Include error handling strategy
- list tasks to be completed to fullfill the PRP in the order they should be completed

### Validation Gates (Must be Executable) e.g. for python

```bash
# Syntax/Style
make ruff
make type_check

# Unit Tests
# make coverage_all
```

***CRITICAL AFTER YOU ARE DONE RESEARCHING AND EXPLORING THE CODEBASE BEFORE YOU START WRITING THE PRP***

***ULTRATHINK ABOUT THE PRP AND PLAN YOUR APPROACH THEN START WRITING THE PRP***

## Quality Checklist

- [ ] All necessary context included
- [ ] References existing patterns
- [ ] Clear implementation path
- [ ] Error handling documented
- [ ] Validation gates are executable by AI

Score the PRP on a scale of 1-10 (confidence level to succeed in one-pass implementation using claude codes)

Remember: The goal is one-pass implementation success through comprehensive context.
