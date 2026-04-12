# URL Shortener (CI/CD Focus)

A simple URL shortener API built with Node.js, Express, and a focus on **DevSecOps** and **CI/CD best practices**.

## Features

- **Simple API**: Only 2 endpoints for shortening and retrieving URLs
- **In-Memory Storage**: Fast and simple (data resets on restart)
- **Production-Grade CI/CD**:
    - **SAST**: CodeQL for security analysis
    - **SCA**: npm audit for dependency scanning
    - **Container Security**: Trivy vulnerability scanning
    - **Automated Testing**: Jest integration tests
    - **Code Quality**: ESLint and Prettier
    - **Docker**: Production-ready containerization
    - **GitHub Actions**: Fully automated pipeline

## CI/CD Pipeline Stages

### 1. Code Quality Check (Linting)
- **Tool**: ESLint
- **Purpose**: Enforce coding standards and prevent technical debt

### 2. SAST - Static Application Security Testing
- **Tool**: GitHub CodeQL
- **Purpose**: Detect code-level vulnerabilities (OWASP Top 10, CWE patterns)
- **Results**: Available in GitHub Security tab

### 3. SCA - Software Composition Analysis
- **Tool**: npm audit
- **Purpose**: Identify vulnerable dependencies and supply-chain risks
- **Threshold**: Moderate severity and above

### 4. Unit Tests
- **Tool**: Jest
- **Purpose**: Validate business logic and prevent regressions
- **Coverage**: 4 test cases covering all endpoints

### 5. Build Verification
- **Purpose**: Ensure application compiles and runs correctly

### 6. Docker Build & Container Scan
- **Build**: Multi-stage Docker build with Node.js Alpine
- **Scan**: Trivy vulnerability scanner
- **Severity**: Reports CRITICAL and HIGH vulnerabilities

### 7. Container Runtime Test
- **Purpose**: Validate container behavior and API functionality
- **Tests**: Health check and endpoint validation

### 8. DockerHub Push
- **Trigger**: Only on push to main branch
- **Tags**: `latest` and commit SHA
- **Authentication**: GitHub Secrets

## Prerequisites

- Node.js (v18+)
- npm
- Docker (optional, for containerization)

## Installation

1.  Clone the repository
2.  Install dependencies:

    ```bash
    npm install
    ```

## Running the Server

Start the server locally:

```bash
npm start
```

The server runs at `http://localhost:3000`.

## API Documentation

### 1. Shorten a URL

**Endpoint:** `POST /shorten`

**Body:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "slug": "AbCdEf",
  "url": "https://example.com"
}
```

### 2. Retrieve Original URL

**Endpoint:** `GET /url/:slug`

**Response:**
```json
{
  "slug": "AbCdEf",
  "url": "https://example.com"
}
```

## Development & CI/CD

### Run Tests
```bash
npm test
```

### Linting & Formatting
```bash
npm run lint
npm run format
```

### Docker Build
```bash
docker build -t url-shortener .
```

### Run Container
```bash
docker run -p 3000:3000 url-shortener
```

## GitHub Secrets Configuration

To enable DockerHub push, configure these secrets in your repository:

| Secret Name | Description |
|-------------|-------------|
| `DOCKERHUB_USERNAME` | Your DockerHub username |
| `DOCKERHUB_TOKEN` | DockerHub access token (not password) |

**How to set up:**
1. Go to Repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add both secrets

## Security

See [SECURITY.md](SECURITY.md) for details on our security scanning and vulnerability reporting process.

## CI/CD Architecture

```
Push to main
    ↓
┌─────────────────────────────────────┐
│  Stage 1: Code Quality (ESLint)    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Stage 2: SAST (CodeQL)            │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Stage 3: SCA (npm audit)          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Stage 4: Unit Tests (Jest)        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Stage 5: Build Verification       │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Stage 6: Docker Build + Trivy     │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Stage 7: Container Runtime Test   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Stage 8: Push to DockerHub        │
└─────────────────────────────────────┘
```

## Why Each Stage Matters

| Stage | Why It Matters |
|-------|----------------|
| Linting | Prevents technical debt and maintains code quality |
| SAST (CodeQL) | Detects OWASP Top 10 vulnerabilities early |
| SCA (npm audit) | Identifies supply-chain risks in dependencies |
| Unit Tests | Prevents regressions and validates logic |
| Build | Ensures application compiles correctly |
| Trivy Scan | Prevents vulnerable container images from shipping |
| Runtime Test | Validates container actually works |
| DockerHub Push | Enables downstream deployment |

## License

MIT
