# Quick Start Guide

Get Clean Architecture enforcement running in your project in 5 minutes.

## 🚀 Installation

### 1. Copy Files to Your Project

```bash
cd your-project-root

# Copy configuration files
curl -O https://raw.githubusercontent.com/rajeevdiligent/cursor-ai-rules/main/.cursorrules
curl -O https://raw.githubusercontent.com/rajeevdiligent/cursor-ai-rules/main/cursor.json
curl -O https://raw.githubusercontent.com/rajeevdiligent/cursor-ai-rules/main/review_parser.py

# Copy GitHub workflows
mkdir -p .github/workflows
curl -o .github/workflows/ai_review.yml https://raw.githubusercontent.com/rajeevdiligent/cursor-ai-rules/main/.github/workflows/ai_review.yml
curl -o .github/workflows/ai_merge_guard.yml https://raw.githubusercontent.com/rajeevdiligent/cursor-ai-rules/main/.github/workflows/ai_merge_guard.yml

# Make script executable
chmod +x review_parser.py
```

### 2. Configure AI API Key

Get an API key from [Anthropic](https://console.anthropic.com/) or [OpenAI](https://platform.openai.com/), then add it to your GitHub repository:

```bash
# Using GitHub CLI
gh secret set ANTHROPIC_API_KEY

# Or go to: Repository → Settings → Secrets → Actions → New secret
```

### 3. Update Project Paths (Optional)

Edit `cursor.json` if your project structure differs:

```json
{
  "architecture": {
    "layers": {
      "domain": {
        "paths": ["src/domain/**"]
      },
      "application": {
        "paths": ["src/application/**"]
      },
      "infrastructure": {
        "paths": ["src/infrastructure/**"]
      },
      "presentation": {
        "paths": ["src/api/**"]
      }
    }
  }
}
```

## 🤖 How It Works

When you create a pull request, the workflow:

1. **Sends your code changes** to Claude AI (or GPT-4 if using OpenAI)
2. **AI analyzes** the code against Clean Architecture rules in `.cursorrules`
3. **Generates review feedback** with:
   - Architecture violations
   - SOLID principle issues
   - Security vulnerabilities
   - Code quality problems
   - Suggestions for fixes
4. **Posts comments** directly on your PR

The review happens automatically within minutes of creating or updating a PR.

## 📝 Project Structure

Organize your code with cursor-ai-rules files at the root:

```
your-project/
├── .cursorrules                    # Clean Architecture rules (copied)
├── cursor.json                     # AI review configuration (copied)
├── review_parser.py                # Review analyzer script (copied)
├── .github/
│   └── workflows/
│       ├── ai_review.yml          # AI code review workflow (copied)
│       └── ai_merge_guard.yml     # Architecture guard workflow (copied)
├── src/
│   ├── domain/                    # Business logic (no external dependencies)
│   ├── application/               # Use cases, orchestration
│   ├── infrastructure/            # Database, APIs, external services
│   └── presentation/              # Controllers, API routes
└── tests/
```

## ✅ Test It

Create a PR and the AI will automatically review it:

```bash
git checkout -b feature/test-review
echo "# Test" > src/domain/test.ts
git add .
git commit -m "Test AI review"
git push origin feature/test-review
```

Create a pull request on GitHub and check for AI review comments.

## 📚 Clean Architecture Rules

### ✅ DO
- Keep domain layer pure (no framework dependencies)
- Use interfaces in domain, implement in infrastructure
- Handle errors with Result/Option types
- Write tests for domain logic

### ❌ DON'T
- Import infrastructure in domain layer
- Put business logic in controllers
- Use direct database access in use cases
- Create circular dependencies

## 🔍 Example: Repository Pattern

**❌ Wrong:**
```typescript
// domain/user.ts
import { db } from '../infrastructure/database';  // VIOLATION!

export class User {
  async save() {
    await db.query('INSERT...');  // Domain knows about DB
  }
}
```

**✅ Correct:**
```typescript
// domain/user.ts
export class User {
  constructor(public id: string, public email: string) {}
  
  validate() {
    if (!this.email.includes('@')) throw new Error('Invalid email');
  }
}

// domain/repositories/user-repository.ts
export interface UserRepository {
  save(user: User): Promise<void>;
}

// infrastructure/user-repository-impl.ts
export class UserRepositoryImpl implements UserRepository {
  constructor(private db: Database) {}
  
  async save(user: User): Promise<void> {
    await this.db.query('INSERT...', user);
  }
}

// application/create-user-use-case.ts
export class CreateUserUseCase {
  constructor(private userRepo: UserRepository) {}
  
  async execute(email: string): Promise<void> {
    const user = new User(uuid(), email);
    user.validate();
    await this.userRepo.save(user);
  }
}
```

## 🛠️ Troubleshooting

**Workflow not running?**
- Enable GitHub Actions: Settings → Actions → General → Allow all actions

**No AI comments?**
- Verify API key: `gh secret list`
- Check workflow logs: Actions tab → Latest run

**False positives?**
- Add project-specific rules to `.cursorrules`
- Adjust thresholds in `cursor.json`

## 📖 Learn More

- **Full Documentation:** [README.md](./README.md)
- **Clean Architecture:** [The Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- **Language Support:** Python, TypeScript/JavaScript, Rust

---

**Ready!** Your project now has AI-powered Clean Architecture enforcement. Create a PR to see it in action! 🎉
