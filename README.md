# OpenAI Metrics Retrieval Script

A minimal Python script to retrieve and display OpenAI API usage metrics, costs, and project information.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Valid OpenAI API key

1. **Install uv** (if not already installed):
   ```bash
   # macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone or download this repository**:
   ```bash
   git clone <repository-url>
   cd openai-metrics
   ```

3. **Dependencies are managed automatically by uv** - no manual installation needed!

## Configuration

### Basic Setup

1. **Copy the template configuration**:
   ```bash
   cp config.yaml my-config.yaml
   ```

2. **Edit your configuration file**:
   ```yaml
   # OpenAI API base URL (default: https://api.openai.com/v1)
   base_url: "https://api.openai.com/v1"
   
   # Your OpenAI API key (required)
   api_key: "your-openai-api-key-here"
   
   # Number of days to look back (default: 7)
   days_back: 7
   ```
## Usage

### Retrieve Metrics
Run the main script to retrieve usage metrics:

```bash
uv run main.py my-config.yaml
```

### Generate Usage Data
To create test usage data for metrics analysis:

```bash
uv run generate_usage.py my-config.yaml
```

**Note**: `main.py` only reads data from OpenAI APIs. `generate_usage.py` will make API calls that consume tokens and may incur costs.

## License

MIT
