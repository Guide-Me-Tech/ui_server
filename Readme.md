## Before to Run the Code

This section helps ensure that you have a complete grasp of the system before starting the application. Review this checklist and accompanying references carefully:

### Understand the Project Structure and Purpose

Examine the project's directory tree and understand each file and directory. The code is designed as a pipeline that transforms raw data from various sources into a final UI, applying configurations, security measures, platform-specific profiles, and flexible widget mappings along the way. Each directory focuses on a particular area of responsibility:

```
.
├── adapters
│   ├── base_adapter.py          # Abstract base for all adapters, defines the interface
│   ├── default_adapter.py       # Fallback adapter if no other adapter matches the input data
│   ├── known_adapters           # Concrete adapters for known data formats (JSON, XML, CSV-like, etc.)
│   │   ├── known_adapter_five.py
│   │   ├── known_adapter_four.py
│   │   ├── known_adapter_one.py
│   │   ├── known_adapter_six.py
│   │   ├── known_adapter_three.py
│   │   └── known_adapter_two.py
│   └── registry.py              # Dynamically loads and selects the correct adapter at runtime
│
├── configuration_manager
│   ├── configuration_manager.py # Manages environment-based configurations and persistent storage if needed
│   └── __init__.py
│
├── docker
│   └── Dockerfile               # Docker build instructions for containerizing the application
│
├── .dockerignore                # Specifies files to ignore in Docker builds
├── dynamic_requirements_updater.py # Automates updating requirements.txt when dependencies change
├── functions_to_format
│   ├── components.py            # Defines UI widgets used in building the final interface
│   ├── dynamic_ui_builder.py    # Constructs the final UI structure from adapted data and widgets
│   ├── functions.py             # Utility functions for formatting and processing
│   ├── __init__.py
│   ├── mapper.py                # Maps data fields to specific widgets or logic paths
│   └── platform_profiles.py     # Adjusts the UI based on platform-specific requirements (e.g., mobile, desktop)
│
├── .git (internal Git data)
├── .gitignore
├── Readme.md                    # This document (instructions and overview)
├── requirements.txt             # All Python dependencies listed here
├── src
│   ├── __init__.py
│   └── server.py                # Main FastAPI application entry point, orchestrates everything
│
├── t.json                       # Example data file for testing
├── utils
│   ├── cache.py                 # Provides caching mechanisms to optimize performance
│   ├── deploy_docker.sh         # Script to build and run the Docker container with resource limits
│   ├── logger.py                # Central logging configuration for consistent output
│   ├── performance_metrics.py   # Collects and reports performance/resource metrics
│   ├── security.py              # Security checks, rate limiting, input validation against suspicious patterns
│   └── users.py                 # Loads user/API keys and related information for authentication/authorization
│
├── .vscode
│   └── settings.json
├── wer_table.ipynb
└── wer_table.py
```

**Key Takeaways from the Structure:**

- **`src/server.py`** is the main entry point. It handles incoming requests and orchestrates the entire pipeline.
- **`adapters/`** handles raw data formats, converting them into a standard internal structure. Adapters are chosen dynamically.
- **`functions_to_format/`** deals with turning adapted data into a final UI, using widgets, mapping rules, and platform profiles.
- **`configuration_manager/`** loads and manages environment-based configurations.
- **`utils/`** contains logging, caching, security checks, performance metrics, and user management utilities, providing essential infrastructure.

Understanding where each piece fits will help you troubleshoot issues and decide where to make changes if needed.

### Check Your System Requirements

Before running the application:

- Ensure you have **Python 3.7+** installed.
- Verify that `pip` is available and that you can install packages from `requirements.txt`.
- If you plan to use Docker:
  - Ensure Docker is installed and running.
  - Review the `docker/Dockerfile` and `utils/deploy_docker.sh` script if you want a containerized setup.

### Verify Dependencies

Install all required dependencies:

```bash
pip install -r requirements.txt
```

Consider using a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

This keeps your project dependencies isolated from other projects on your system.

### Set Environment Variables Appropriately

Many features and behaviors are controlled via environment variables. For example:

- **LOG_LEVEL:** Controls logging verbosity (`DEBUG`, `INFO`, `ERROR`).
- **ADAPTERS_LIST:** Specifies which adapters to load (e.g., `"adapters.known_adapters.known_adapter_one"`).
- **UI_BUILDER_WIDGET_MAPPING:** Defines how data fields map to certain widgets.
- **PLATFORM_PROFILES_LIST:** E.g., `"mobile,desktop"` to enable platform-specific UI adjustments.
- **CACHE_ENABLED, RATE_LIMIT_ENABLED, METRICS_ENABLED:** Enable or disable caching, rate limiting, and performance metrics.

Even if you rely on defaults at first, being aware of these variables helps you tailor the system’s behavior later without changing code.

### Review the Dynamic Requirements Updater

If you add new Python code that imports new libraries, consider the `dynamic_requirements_updater.py` script:

1. After adding new libraries (e.g., `pip install newlibrary`), run:
   ```bash
   python3 dynamic_requirements_updater.py
   ```
2. This script updates `requirements.txt` automatically, ensuring it remains synchronized with the actual libraries you are using.
3. Re-run `pip install -r requirements.txt` if needed, especially before deploying or committing changes.

This step ensures a consistent and stable environment.

### Plan Any Modifications Before Running

If you anticipate modifying the code, for example, to support a new data format, you should follow a structured approach. Try to achieve your goals through environment variables first. If you must modify code, follow the sequence below, from the simplest changes to the more complex:

```
                      (Goal: Add/Change Feature)
                      |
             ┌─────────────────┐
             │ Try ENV changes  │
             │ (no code changes)│
             └───────▲─────────┘
                     │ If not enough:
                     │
      ┌─────────────────────────────┐
      │Add/Modify Adapters if new    │
      │data format needed (adapters/)│
      └─▲──────────────────────────┘
        │If UI layout changes:
        │
  ┌──────────────┐
  │Modify Widgets │
  │(components.py)│
  │or Mapper(mapper.py)
  └─▲─────────────┘
    │If platform changes:
    │
  ┌─────────────────────────┐
  │ Add Platform Profile     │
  │(platform_profiles.py)    │
  └─▲───────────────────────┘
    │If new config keys:
    │
  ┌─────────────────────────┐
  │ configuration_manager    │
  │ (configuration_manager.py)
  └─▲───────────────────────┘
    │If caching/security/metrics:
    │
  ┌───────────────────────┐
  │ utils/(cache.py,       │
  │ security.py, metrics)  │
  └─▲─────────────────────┘
    │Finally if needed:
    │
  ┌─────────────────┐
  │   server.py      │
  └─────────────────┘
```

**Interpretation of this Diagram:**

1. Start by changing environment variables if you want to tweak behavior without code edits.
2. If you need a new data format, create or modify an adapter in `adapters/`.
3. If the UI layout needs to change, adjust `components.py` or `mapper.py` to control widget usage.
4. If the look-and-feel must differ for a new platform (e.g., a voice assistant), add a profile in `platform_profiles.py`.
5. If new config parameters are needed, update `configuration_manager.py`.
6. For optimization or new security rules, modify `utils/` files as needed.
7. Only alter `server.py` if absolutely no other option works.

By following this order, you reduce complexity, avoid breaking other parts, and maintain a smooth development workflow.


**1) `src/server.py` (Main Entry Point)**

This file orchestrates the entire pipeline: it receives incoming HTTP requests, invokes configuration and security checks, selects the appropriate adapter, and delegates to the UI builder and platform profiles before returning the final UI.

```
             ┌─────────────────────────────┐
             │         server.py            │
             │   (main FastAPI app)         │
             └───────────▲─────────────────┘
                         │ HTTP request arrives
                         │
              (1) Load configs from configuration_manager
              (2) Validate request & user from utils/security & utils/users
                         │
                         ▼
            ┌───────────────────────────┐
            │    adapters/registry.py    │
            │(selects correct adapter)   │
            └───────────▲──────────────┘
                        │ get raw data, adapt it
                        │
                 (3) Receive adapted data
                        │
                        ▼
          ┌─────────────────────────────────┐
          │ functions_to_format/dynamic_ui_builder.py │
          │ builds final UI with widgets & mapper     │
          └───────────▲─────────────────────────────┘
                      │
              (4) If needed, apply platform profiles
                      │
             (5) Construct final UI
                      │
                      ▼
            Return HTTP response with final UI to client
```

**Key Points:**  
- `server.py` is the starting point.  
- Loads configs, applies security checks.  
- Invokes adapter selection, then passes adapted data to the UI builder.  
- Final output returned to client.

---

**2) `functions_to_format/dynamic_ui_builder.py` (UI Construction)**

This file takes adapted data and uses widgets (from `components.py`) along with mapping rules (from `mapper.py`) to produce a structured UI. It may also integrate caching or consider resource-saving modes.

```
            ┌───────────────────────────────┐
            │ dynamic_ui_builder.py          │
            │ builds final UI structure       │
            └──────────▲────────────────────┘
                       │ receives adapted data from server.py
                       │ and possibly a set of environment-driven configs
                       │
           (1) Check if caching is enabled (if UI already cached, return from cache)
                       │
           (2) Use UI_BUILDER_WIDGET_MAPPING & mapper.py to select widgets
                       │
                       ▼
          ┌─────────────────────────┐
          │ functions_to_format/    │
          │ components.py (widgets) │
          └───────────▲────────────┘
                      │ fetch widget definitions
                      │
            (3) For each data field, assign a widget and populate it
                      │
                      ▼
             Build a UI dictionary structure: {"ui": [ ... ]}
                      │
            (4) Format output according to UI_BUILDER_OUTPUT_FORMAT
                      │  (e.g., "json" or "dict")
                      │
            (5) If caching is enabled, store final UI in cache
                      │
                      ▼
                  Return final UI structure to server.py
```

**Key Points:**  
- Transforms adapted data into a final UI.  
- Chooses widgets per field using mappings and environment variables.  
- Supports caching and configurable output formats.

---

**3) `functions_to_format/platform_profiles.py` (Platform-Specific Adjustments)**

This file applies additional transformations to the UI based on the target platform profile(s). For example, mobile might simplify UI elements, desktop might add sidebars, voice assistant might remove images and shorten text.

```
             ┌──────────────────────────────┐
             │ platform_profiles.py          │
             │ applies platform adjustments  │
             └───────────▲──────────────────┘
                         │ receives a UI structure from dynamic_ui_builder
                         │
                (1) Read PLATFORM_PROFILES_LIST (e.g., "mobile,desktop")
                         │
                (2) For each profile in the list:
                    - mobile: reduce image sizes, simplify layout
                    - desktop: add navigation menus, advanced options
                    - voice_assistant: remove visuals, shorten text
                    - ar_vr: add depth fields, remove backgrounds
                         │
                         ▼
              Apply modifications to the UI dictionary
                         │
                (3) After all profiles processed, final UI is updated
                         │
                         ▼
                 Return updated UI back to dynamic_ui_builder or server.py
```

**Key Points:**  
- Modifies UI after it’s constructed, before returning to the client.  
- Each profile is environment-driven, so no code changes needed for switching platforms.  
- Profiles can be chained (e.g., mobile + voice_assistant) by applying them in order.

---

**4) `adapters/registry.py` (Adapter Selection)**

`registry.py` is crucial for choosing the correct adapter based on the incoming data format. It dynamically loads adapters, tries each until one matches, and returns an adapter instance capable of transforming raw input into the standard internal structure.

```
               ┌───────────────────────┐
               │ registry.py (adapters) │
               │ selects correct adapter│
               └──────────▲────────────┘
                          │ server.py calls registry to find an adapter
                          │
                (1) Load adapters from ADAPTERS_LIST or ADAPTERS_DIR env settings
                          │ 
                (2) For each adapter:
                    - known_adapter_one: checks if data format matches expected keys
                    - known_adapter_two: checks if input_type="xml"
                    - known_adapter_three: checks if source="csv"
                    etc.
                          │
                (3) The first adapter that match(data) returns True is chosen
                          │
                (4) registry returns the chosen adapter instance to server.py
                          │
                          ▼
                   server.py uses adapter.adapt(raw_data) to get adapted data
```

**Key Points:**  
- Dynamically determines which adapter handles the raw input.  
- Allows adding new adapters without changing `server.py`.  
- If none match, fallback adapter (default_adapter.py) is used.

---

**5) `utils/security.py` (Security, Validation, Rate Limiting)**

This file ensures that input data is safe (no malicious patterns), applies rate limits to prevent abuse, and validates identifiers and request sizes. It’s often called by `server.py` at the start of a request.

```
           ┌─────────────────────────┐
           │ security.py             │
           │ input validation & rate │
           │ limiting                │
           └─────────▲──────────────┘
                     │ server.py invokes security checks
                     │
           (1) Validate input size vs MAX_INPUT_SIZE env variable
                     │
           (2) Check suspicious patterns using regex and SUSPICIOUS_PATTERNS
                     │
           (3) Check if RATE_LIMIT_ENABLED:
                 - If enabled, record request timestamp
                 - If too many requests from same key/IP, block request
                     │
           (4) Validate identifiers against IDENTIFIER_PATTERN
                     │
                     ▼
              If all checks pass, allow request to proceed
              Otherwise, return error or block request
```

**Key Points:**  
- Protects from malicious inputs and DoS attacks.  
- Fully configurable via environment variables.  
- Returns control to server.py only if everything is safe.

---

**Additional Guidance**

### Running the Code

**Step-by-Step Instructions:**

1. **Set Up Environment**  
   Ensure Python 3.7+ is available. Consider using a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Environment Variables (Optional)**  
   If you want to customize logging, adapters, caching, etc., export environment variables:
   ```bash
   export LOG_LEVEL=DEBUG
   export ADAPTERS_LIST="adapters.known_adapters.known_adapter_one"
   export PLATFORM_PROFILES_LIST="mobile"
   # ...and so forth
   ```

   If you do not set them, the code uses defaults.

4. **Run the Application**  
   Start the FastAPI server:
   ```bash
   uvicorn src.server:app --host 0.0.0.0 --port 8000
   ```
   
   Open your browser to http://localhost:8000 to interact with the API.

5. **Check Logs & Adjust Variables**  
   If something doesn’t appear as expected, increase logging verbosity (LOG_LEVEL=DEBUG) or enable metrics. No code changes needed for these adjustments, just change environment variables and restart the server.

6. **Test with Example Data**  
   Send requests to endpoints defined in `server.py`. If you have sample data (like `t.json`), you can send it as JSON input to the API to see how it’s adapted and transformed into a UI.

### Modifying the Code

As explained in the earlier diagram, if you need to add or change functionality:

- **No code changes:**  
  Try adjusting environment variables first. Many aspects of adapter selection, UI widget mapping, platform profiles, caching, security, and metrics can be controlled this way.

- **New Data Format (Adapter):**  
  If ENV changes are insufficient, add a new adapter in `adapters/known_adapters/`. Implement `match()` and `adapt()` methods. Update ADAPTERS_LIST to include your new adapter.

- **Change UI Layout (Widgets/Mapper):**  
  If you need a new widget type or different data-to-widget mapping, modify `components.py` or `mapper.py`. This allows changes to how UI elements are constructed without touching `server.py`.

- **Platform-Specific Adjustments:**  
  For new platforms or unique adjustments, add or modify a platform profile in `platform_profiles.py`. This ensures that when PLATFORM_PROFILES_LIST is updated, the new platform’s changes are applied.

- **New Configuration Keys:**  
  For adding new configuration parameters (like a new environment variable or a new file-based config), adjust `configuration_manager.py`.

- **Caching/Security/Metrics Changes:**  
  If you want to alter caching policies, security checks, or metric collection logic, head to `utils/` directory and modify `cache.py`, `security.py`, or `performance_metrics.py` respectively.

- **Finally, `server.py`:**  
  Only modify `server.py` if no other approach works. This file should remain stable and mostly rely on adapters, UI builder, and profiles.

Following this order prevents confusion and keeps the architecture clean.





### Familiarize Yourself with the Logging and Metrics Systems

The code includes robust logging and metrics:

- **Logging (utils/logger.py):** Adjust `LOG_LEVEL` for more verbose or quieter output. Logging provides insight into each step, from adapter selection to final UI building.
- **Performance Metrics (utils/performance_metrics.py):** If needed, enable metrics to monitor CPU usage, memory consumption, and request processing times. This information is crucial if you need to optimize performance.

If you encounter issues, these tools help you understand what is happening internally, letting you adjust environment variables or code accordingly.

### How to Run the Code (Step-by-Step)

Before running the code, ensure you have Python 3.7 or higher installed and that you’ve installed all dependencies from `requirements.txt`. You may also want to consider setting environment variables to customize the behavior of the system. Follow these steps:

**Step 1: Setup Your Environment**

- **Check Python:**  
  Verify Python version:  
  ```bash
  python3 --version
  ```
  Ensure it returns something like `Python 3.7.0` or higher.

- **(Optional) Create a Virtual Environment:**  
  It's recommended but not mandatory:  
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
  
- **Install Dependencies:**  
  Inside your project directory:  
  ```bash
  pip install --no-cache-dir -r requirements.txt
  ```
  
  This installs all required packages (FastAPI, uvicorn, etc.).

**Step 2: (Optional) Set Environment Variables**

You can adjust system behavior without editing code by setting environment variables. For example:

- To increase logging verbosity:
  ```bash
  export LOG_LEVEL=DEBUG
  ```
- To specify which adapters to load:
  ```bash
  export ADAPTERS_LIST="adapters.known_adapters.known_adapter_one,adapters.known_adapters.known_adapter_two"
  ```
- To apply platform profiles (e.g., "mobile"):
  ```bash
  export PLATFORM_PROFILES_LIST="mobile"
  ```
  
If you do not set any environment variables, default values are used. You can always come back and adjust them later if needed.

**Step 3: Start the Server**

Run the FastAPI server using `uvicorn`:

```bash
uvicorn src.server:app --host 0.0.0.0 --port 8000
```

- `src/server.py` is the main application file.
- `--host` and `--port` specify where the server listens.

Open your browser at `http://localhost:8000` to see if the server is running. You can also check `http://localhost:8000/docs` for interactive documentation.

---

### High-Level Execution Flow

When you make a request to the server, here’s what happens internally. The following diagram and explanation illustrate the `adapters/registry.py` part of the process.

```
               ┌───────────────────────┐
               │ registry.py (adapters) │
               │ selects correct adapter│
               └──────────▲────────────┘
                          │ server.py calls registry to find an adapter
                          │
                (1) Read environment vars: ADAPTERS_LIST or ADAPTERS_DIR
                    - If ADAPTERS_LIST is set, registry loads adapters listed there.
                    - If ADAPTERS_DIR is set, registry scans that directory for adapter files.
                    If none provided, it uses default fallback adapter.
                          │
                (2) registry.py now has a list of adapter classes (like known_adapter_one, known_adapter_two, etc.)
                    For each adapter:
                      - known_adapter_one checks if data matches its expected format key/value.
                      - known_adapter_two checks if input_type="xml".
                      - known_adapter_three checks if source="csv".
                      - known_adapter_four, five, six similarly check their own conditions.
                          │
                (3) registry tries adapters in order:
                    - Calls adapter.match(data)
                    - If match() returns True, that adapter is chosen immediately.
                    - If match() returns False, it tries the next adapter.
                    If none match, it uses default_adapter.py (fallback).
                          │
                (4) Once an adapter is chosen, registry returns that adapter instance to server.py
                          │
                          ▼
                   server.py calls adapter.adapt(raw_data) to transform raw input
                   into a standardized internal format suitable for UI building.
```

**What This Means in Practice:**

- Suppose your request’s data format is JSON with a certain key `format="json"`.  
- If `known_adapter_one` is designed to handle `format="json"`, its `match()` will return True.  
- The registry stops searching and returns `known_adapter_one` to `server.py`.  
- `server.py` then calls `known_adapter_one.adapt(raw_data)`, and you get adapted data ready for UI building.

---

### Detailed Steps After Running the Code

Once the server is running, here’s a more comprehensive view of the entire pipeline (combining the previous instructions with the code logic):

1. **User Sends HTTP Request to the API**:  
   You use `curl` or your browser to hit `http://localhost:8000/` or another endpoint.  
   The request arrives in `server.py`.

2. **server.py Loads Configs & Security Checks**:  
   - Reads environment variables (via configuration_manager/).  
   - Applies security checks from utils/security.py (checks input size, suspicious patterns, rate limit if enabled).
   If checks fail, request is rejected. If all good, continues.

3. **Adapter Selection via registry.py**:  
   server.py asks `registry.py` for the correct adapter.  
   `registry.py` loads adapters, tries each adapter’s `match()` method until one returns True.
   If no adapter matches, fallback_adapter is used.

4. **Data Adaptation**:  
   Once an adapter is chosen, server.py calls `adapter.adapt(raw_data)`.
   The adapter returns a standardized internal representation of your data.

5. **UI Construction with dynamic_ui_builder.py**:  
   server.py passes adapted data to `dynamic_ui_builder`.  
   `dynamic_ui_builder`:
   - Checks if a cached UI version exists if caching is enabled.
   - Reads UI_BUILDER_WIDGET_MAPPING (if any) to know which widgets to use for each data field.
   - Fetches widget definitions from `functions_to_format/components.py`.
   - Constructs a UI dictionary like `{"ui": [ ... ]}`.
   - If platform profiles are set, `platform_profiles.py` is invoked to modify the UI for mobile/desktop/voice, etc.

6. **Finalize and Return UI**:  
   After all transformations, server.py receives the fully constructed UI.  
   It returns the UI as the HTTP response to the client.

The user sees a final, platform-tailored UI, all done without changing code, just by setting environment variables and letting the pipeline run.

---

### If You Need to Modify the Code

The recommendation is to first try environment variables to achieve your goals. If environment tweaks aren’t enough:

- **Change Adapters**:  
  If you must support a new data format:
  1. Create a new file in `adapters/known_adapters/` implementing `BaseAdapter`.
  2. Add `match()` and `adapt()` logic.
  3. Update `ADAPTERS_LIST` to include this adapter.
  
- **Change UI Layout (Widgets/Mapper)**:  
  If the UI needs new widget types or a different field-to-widget logic:
  1. Check `functions_to_format/components.py` and add new widgets.
  2. Update `UI_BUILDER_WIDGET_MAPPING` env variable or `mapper.py` to map fields to these new widgets.
  3. Run the code again; no need to edit `server.py`.

- **New Platform Profiles**:  
  If you want new platform-specific UI changes:
  1. Add a new profile class in `functions_to_format/platform_profiles.py`.
  2. Set `PLATFORM_PROFILES_LIST` to include this new profile.
  
- **New Config Keys**:  
  If your feature needs new environment variables or config files:
  1. Add logic in `configuration_manager.py` or handle new ENV variables in your code.
  2. Document the new variables in README or similar place.

- **Caching/Security/Metrics**:  
  If you need changes in caching behavior, security checks, or metrics:
  1. Edit `utils/cache.py`, `utils/security.py`, or `utils/performance_metrics.py` accordingly.
  
- **Finally server.py**:  
  Only modify `src/server.py` if absolutely necessary. Usually, `server.py` should remain stable, orchestrating the pipeline without knowing implementation details.

