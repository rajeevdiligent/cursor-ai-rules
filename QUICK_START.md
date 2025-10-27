# Quick Start Guide

Get up and running with Cursor AI Clean Architecture Pack in 5 minutes!

## ⚡ Quick Install

### Option 1: Automated Installation (Recommended)

```bash
# Clone or download this pack
cd your-project-root

# Run the installer
./path/to/cursor-ai-clean-architecture-pack/install.sh
```

The installer will:
- ✅ Copy all necessary files
- ✅ Detect your project structure
- ✅ Create required directories
- ✅ Make scripts executable
- ✅ Provide customization guidance

### Option 2: Manual Installation

```bash
cd your-project-root

# Copy core files
cp path/to/pack/.cursorrules .
cp path/to/pack/cursor.json .
cp path/to/pack/review_parser.py .

# Copy workflows
mkdir -p .github/workflows
cp path/to/pack/.github/workflows/*.yml .github/workflows/

# Make scripts executable
chmod +x review_parser.py
```

## 🔑 Configure API Keys

Choose one AI provider:

### Option A: Anthropic Claude (Recommended)

1. Get API key from https://console.anthropic.com/
2. Add to GitHub:
   ```bash
   # Using GitHub CLI
   gh secret set ANTHROPIC_API_KEY
   
   # Or manually:
   # Go to: Your Repo → Settings → Secrets → New repository secret
   # Name: ANTHROPIC_API_KEY
   # Value: your-api-key
   ```

### Option B: OpenAI GPT-4

1. Get API key from https://platform.openai.com/
2. Add to GitHub:
   ```bash
   gh secret set OPENAI_API_KEY
   ```

## 📁 Update Project Paths

Edit `cursor.json` to match your structure:

```json
{
  "architecture": {
    "layers": {
      "domain": {
        "paths": ["src/domain/**", "your-path/**"]
      },
      "application": {
        "paths": ["src/application/**", "your-path/**"]
      }
    }
  }
}
```

## 🧪 Test It Out

1. **Create a test branch:**
   ```bash
   git checkout -b test-ai-review
   ```

2. **Make a small change:**
   ```bash
   echo "// Test change" >> src/domain/test.ts
   git add .
   git commit -m "Test AI review"
   git push origin test-ai-review
   ```

3. **Create a PR:**
   - Go to GitHub and create a PR
   - Wait for the AI review workflow to run
   - Check the PR comments for the review results

## 📊 Example: Good vs Bad Code

### ❌ Bad: Violation Example

```typescript
// src/domain/user.ts
import { database } from '../infrastructure/database';  // VIOLATION!

export class User {
  async save() {
    await database.execute('INSERT INTO users...');  // Domain shouldn't know about DB
  }
}
```

The AI will flag this as:
- **Violation**: Domain layer importing from Infrastructure
- **Severity**: Error
- **Suggestion**: Use repository pattern with dependency injection

### ✅ Good: Correct Implementation

```typescript
// src/domain/user.ts - Pure domain logic
export class User {
  constructor(
    private id: string,
    private name: string,
    private email: string
  ) {}
  
  validate(): void {
    if (!this.email.includes('@')) {
      throw new InvalidEmailError();
    }
  }
}

// src/domain/repositories/user-repository.ts - Interface in domain
export interface UserRepository {
  save(user: User): Promise<void>;
  findById(id: string): Promise<User | null>;
}

// src/infrastructure/user-repository-impl.ts - Implementation in infrastructure
export class UserRepositoryImpl implements UserRepository {
  constructor(private database: Database) {}
  
  async save(user: User): Promise<void> {
    await this.database.execute('INSERT INTO users...', user);
  }
}

// src/application/create-user-use-case.ts - Use case orchestrates
export class CreateUserUseCase {
  constructor(private userRepo: UserRepository) {}
  
  async execute(dto: CreateUserDTO): Promise<void> {
    const user = new User(dto.id, dto.name, dto.email);
    user.validate();
    await this.userRepo.save(user);
  }
}
```

## 🎯 Common Tasks

### View Review Results

```bash
# Download artifact from GitHub Actions
gh run download [run-id]

# Or view in PR comments
# The AI posts results directly on your PR
```

### Run Manual Review

```bash
# Generate review data (you'll need to create this JSON)
python review_parser.py \
  --input review_data.json \
  --output CODE_REVIEW_SUMMARY.md
```

### Customize Rules

Edit `.cursorrules` to add project-specific rules:

```markdown
## Project-Specific Rules

### API Endpoints
- All endpoints must use versioning: /api/v1/...
- Use DTOs for all request/response bodies
- Implement rate limiting on public endpoints

### Testing
- Integration tests required for all repositories
- E2E tests required for critical user flows
```

### Adjust Quality Thresholds

Edit `cursor.json`:

```json
{
  "quality": {
    "maxFunctionLength": 30,        // Increase if needed
    "maxParameterCount": 5,         // Adjust based on team preference
    "minTestCoverage": 70           // Lower for legacy projects
  }
}
```

## 🔧 Troubleshooting

### Workflow Not Running?

1. Check GitHub Actions are enabled:
   - Go to: Settings → Actions → General
   - Allow all actions

2. Check branch protection:
   - Workflows must run on protected branches
   - Add status checks if needed

### No Review Comments?

1. Verify API key is set:
   ```bash
   gh secret list
   # Should show ANTHROPIC_API_KEY or OPENAI_API_KEY
   ```

2. Check workflow logs:
   - Go to Actions tab
   - Click on the failed run
   - Review error messages

### False Positives?

1. Update `.cursorrules` to clarify expectations
2. Adjust `cursor.json` settings
3. Add comments in code explaining exceptions
4. Consider lowering severity thresholds

### Rate Limits?

If you hit API rate limits:
1. Reduce `maxTokens` in `cursor.json`
2. Limit files reviewed (check workflow file)
3. Add cooldown between reviews

## 📚 Next Steps

1. **Read the full README.md** for comprehensive documentation
2. **Customize rules** for your team's needs
3. **Enable branch protection** to enforce reviews
4. **Share with your team** and gather feedback
5. **Iterate on rules** based on actual violations

## 🎓 Learn More

### Understanding Clean Architecture

**The Dependency Rule:**
```
Outer layers depend on inner layers, never the reverse.

Presentation → Application → Domain ← Infrastructure
                              ↑
                            Core
                     (No dependencies)
```

### Layer Responsibilities

1. **Domain (Core)**
   - Business entities
   - Business rules
   - Domain events
   - No framework dependencies

2. **Application**
   - Use cases
   - Business workflows
   - DTOs and mappers
   - Orchestration logic

3. **Infrastructure**
   - Database implementations
   - External APIs
   - File systems
   - Framework specifics

4. **Presentation**
   - Controllers
   - API routes
   - Request/response handling
   - UI components

## 💡 Tips for Success

1. **Start Small**: Enable for one service/module first
2. **Educate Team**: Share clean architecture resources
3. **Iterate Rules**: Adjust based on real violations
4. **Use Examples**: Reference good patterns in code reviews
5. **Be Consistent**: Apply rules uniformly across codebase

## 🆘 Getting Help

- **Check documentation**: README.md has detailed examples
- **Review workflows**: Look at workflow logs for errors
- **Open an issue**: Report bugs or request features
- **Ask the team**: Share knowledge and solutions

## ✅ Success Checklist

- [ ] Files copied to project root
- [ ] API key configured in GitHub Secrets
- [ ] `cursor.json` paths updated for your project
- [ ] Test PR created and reviewed
- [ ] Review comments appear on PR
- [ ] Team members understand the rules
- [ ] Branch protection configured (optional)
- [ ] Customized rules for your project

---

**You're all set! 🎉**

Create a PR and watch the AI review your code for Clean Architecture compliance!

