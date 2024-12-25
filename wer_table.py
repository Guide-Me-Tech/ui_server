import os
import logging
import wave
import contextlib
from dataclasses import dataclass
import pandas as pd
import numpy as np

# Janis Rubins step 1: Configure logger for deep logging
# The logger will track all steps, errors, warnings, and info messages for future analysis.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(asctime)s][%(levelname)s][%(name)s]: %(message)s"))
logger.addHandler(handler)

@dataclass
class AudioFile:
    id: str
    audio_path: str
    txt_path: str
    text: str
    duration: float

# Janis Rubins step 2: Define paths
# These paths can be easily changed or parameterized to adapt to different environments or data sources.
path_test = "/Users/aslonkhamidov/Downloads/ISSAI_USC/test/"
path_train = "/Users/aslonkhamidov/Downloads/ISSAI_USC/train/"
path_val = "/Users/aslonkhamidov/Downloads/ISSAI_USC/dev/"

# Janis Rubins step 3: List files
# We read directory listings. If directories are huge, consider filtering or caching.
files_test = os.listdir(path_test)
files_train = os.listdir(path_train)
files_val = os.listdir(path_val)

# Janis Rubins step 4: Extract IDs
# Splitting filenames to get unique IDs. This logic remains unchanged to avoid breaking old code.
ids_test = set(f.split(".")[0] for f in files_test)
ids_train = set(f.split(".")[0] for f in files_train)
ids_val = set(f.split(".")[0] for f in files_val)

logger.info("Test IDs: %d", len(ids_test))
logger.info("Train IDs: %d", len(ids_train))
logger.info("Val IDs: %d", len(ids_val))

# Janis Rubins step 5: Prepare a stats dictionary for performance and resource usage tracking
stats = {
    "test_missing": 0,
    "train_missing": 0,
    "val_missing": 0,
    "total_objects": 0,
    "total_duration": 0.0
}

# Janis Rubins step 6: Function to safely calculate duration and log errors
def calculate_duration(audio_path):
    # Attempt to open the WAV file and compute duration.
    # If any error occurs, log it and return 0.0 to avoid code break.
    try:
        with contextlib.closing(wave.open(audio_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            return duration
    except Exception as e:
        logger.error("Error calculating duration for %s: %s", audio_path, e)
        return 0.0

# Janis Rubins step 7: Function to process a set of IDs from a given path
# This function reads text files, maps audio files, and creates AudioFile objects.
# It logs every step, allowing ML engineers to understand exactly what happened.
def process_ids(ids_set, txt_base_path, audio_base_path, missing_key):
    result = []
    missing = 0
    for idx in ids_set:
        txt_path = os.path.join(txt_base_path, idx + ".txt")
        audio_path = os.path.join(audio_base_path, idx + ".wav")

        # Janis Rubins step 8: Check file existence to save CPU and avoid useless operations
        if not os.path.exists(txt_path):
            missing += 1
            logger.warning("Missing text file for ID: %s", idx)
            continue
        if not os.path.exists(audio_path):
            missing += 1
            logger.warning("Missing audio file for ID: %s", idx)
            continue

        # Janis Rubins step 9: Read text file
        # Any error here is logged, ensuring we can identify problematic files quickly.
        try:
            with open(txt_path, "r") as f:
                text = f.read()
        except Exception as e:
            missing += 1
            logger.error("Error reading text file for %s: %s", idx, e)
            continue

        # Janis Rubins step 10: Create AudioFile object
        # duration=0.0 initially; we'll calculate it later.
        result.append(AudioFile(
            id=idx,
            audio_path=audio_path,
            txt_path=txt_path,
            text=text,
            duration=0.0
        ))

    # Janis Rubins step 11: Update stats and log results
    stats[missing_key] += missing
    logger.info("Processed %d items, %d missing for current set", len(result), missing)
    return result

# Janis Rubins step 12: Process all sets
# We call process_ids three times. This is kept unchanged to avoid impacting external code that may rely on these steps.
objects = []
objects.extend(process_ids(ids_test, path_test, path_test, "test_missing"))
objects.extend(process_ids(ids_train, path_train, path_train, "train_missing"))
objects.extend(process_ids(ids_val, path_val, path_val, "val_missing"))

stats["total_objects"] = len(objects)
logger.info("Total objects collected: %d", stats["total_objects"])

# Janis Rubins step 13: Calculate durations
# We iterate over each AudioFile, calculate duration, and accumulate total duration in stats for analysis.
for o in objects:
    d = calculate_duration(o.audio_path)
    o.duration = d
    stats["total_duration"] += d

logger.info("Durations calculated. Total duration sum: %.2f seconds", stats["total_duration"])

# Janis Rubins step 14: Convert to DataFrame
df = pd.DataFrame(objects)

# Janis Rubins step 15: Save to CSV/JSON
# Saving results for future analytics. The file formats remain unchanged.
df.to_csv("data.csv")
df.to_json("data.json", indent=4)
logger.info("Data saved to data.csv and data.json")

# Janis Rubins step 16: Post-process paths to make them relative, reducing absolute path overhead
# This keeps the code flexible if we move data directories. Just changing base paths will suffice.
def change_path(row):
    # Replace the base prefix with nothing to get relative paths.
    # This helps if we share this dataset with other systems or run on different machines.
    row.audio_path = row.audio_path.replace("/Users/aslonkhamidov/Downloads/ISSAI_USC/", "")
    row.txt_path = row.txt_path.replace("/Users/aslonkhamidov/Downloads/ISSAI_USC/", "")
    return row

df = df.apply(change_path, axis=1)
df.to_csv("data_relative_paths.csv")
df.to_json("data_relative_paths.json", indent=4)
logger.info("Paths updated and saved to data_relative_paths.csv and data_relative_paths.json")

# Janis Rubins step 17: Reload and verify final JSON for consistency
df_check = pd.read_json("data_relative_paths.json")
logger.info("Reloaded data_relative_paths.json for verification, shape: %s", df_check.shape)

# Janis Rubins step 18: Log final stats for ML engineers and Data Scientists
# This allows them to quickly understand how many files were processed, how many missing, total duration, etc.
logger.info("Final stats: %s", stats)

# Janis Rubins step 19: Conclude
# The script ended successfully. Resources were used efficiently, logs provide full trace,
# and resulting data is ready for ML pipelines, analytics, or external integrations.
logger.info("Script completed successfully, ready for further analysis and integration.")

# Janis Rubins step 20: Extract ML/DS Insights
# This section helps ML engineers and Data Scientists understand the data better
# for model retraining and improvements without changing the core functionality.
logger.info("Starting ML/DS analysis for potential improvements...")

def extract_ml_insights(df):
    """
    Analyze dataset characteristics for ML/DS optimization opportunities.
    Key metrics help in:
    - Identifying data imbalances
    - Spotting potential preprocessing needs
    - Finding optimization opportunities
    - Understanding resource requirements
    """
    insights = {
        "distribution_stats": {},
        "resource_metrics": {},
        "quality_indicators": {},
        "performance_hints": {}
    }
    
    # Janis Rubins step 20.1: Analyze text characteristics
    # Understanding text properties helps in tokenizer selection and preprocessing
    insights["distribution_stats"]["text_length"] = {
        "mean": df["text"].str.len().mean(),
        "std": df["text"].str.len().std(),
        "min": df["text"].str.len().min(),
        "max": df["text"].str.len().max(),
        "percentile_95": np.percentile(df["text"].str.len(), 95)
    }
    
    # Janis Rubins step 20.2: Audio duration analysis
    # Critical for batch size selection and memory management
    insights["resource_metrics"]["duration"] = {
        "total_hours": df["duration"].sum() / 3600,
        "mean_duration": df["duration"].mean(),
        "std_duration": df["duration"].std(),
        "min_duration": df["duration"].min(),
        "max_duration": df["duration"].max()
    }
    
    # Janis Rubins step 20.3: Dataset balance analysis
    # Helps identify potential biases and training challenges
    insights["distribution_stats"]["samples_per_split"] = df["audio_path"].apply(
        lambda x: x.split("/")[0]
    ).value_counts().to_dict()
    
    # Janis Rubins step 20.4: Quality indicators
    # Flags potential issues for preprocessing or model architecture decisions
    insights["quality_indicators"] = {
        "very_short_samples": len(df[df["duration"] < 1]),
        "very_long_samples": len(df[df["duration"] > 30]),
        "empty_text": len(df[df["text"].str.strip() == ""]),
        "unique_texts": len(df["text"].unique())
    }
    
    # Janis Rubins step 20.5: Performance optimization hints
    # Suggestions for model architecture and training strategy
    insights["performance_hints"] = {
        "recommended_batch_size": min(32, len(df) // 100),
        "suggested_max_length": int(insights["distribution_stats"]["text_length"]["percentile_95"]),
        "memory_estimate_gb": (df["duration"].sum() * 16000 * 2) / (1024**3),  # Assuming 16kHz, 16-bit
        "suggested_train_steps": len(df) // 32 * 10  # 10 epochs with batch size 32
    }
    
    return insights

# Janis Rubins step 20.6: Generate and log insights
# Provide actionable information for ML engineers and Data Scientists
insights = extract_ml_insights(df)

logger.info("ML/DS Insights Summary:")
logger.info("Dataset Characteristics:")
logger.info(f"- Total duration: {insights['resource_metrics']['duration']['total_hours']:.2f} hours")
logger.info(f"- Average sample duration: {insights['resource_metrics']['duration']['mean_duration']:.2f} seconds")
logger.info(f"- Text length (mean/max): {insights['distribution_stats']['text_length']['mean']:.1f}/{insights['distribution_stats']['text_length']['max']}")

logger.info("\nQuality Flags:")
logger.info(f"- Very short samples: {insights['quality_indicators']['very_short_samples']}")
logger.info(f"- Very long samples: {insights['quality_indicators']['very_long_samples']}")
logger.info(f"- Empty text samples: {insights['quality_indicators']['empty_text']}")

logger.info("\nOptimization Suggestions:")
logger.info(f"- Recommended batch size: {insights['performance_hints']['recommended_batch_size']}")
logger.info(f"- Estimated memory requirement: {insights['performance_hints']['memory_estimate_gb']:.2f}GB")
logger.info(f"- Suggested training steps: {insights['performance_hints']['suggested_train_steps']}")

# Save insights for future reference
import json
with open("ml_insights.json", "w") as f:
    json.dump(insights, f, indent=4)
logger.info("ML insights saved to ml_insights.json")

# Janis Rubins step 20.7: Conclude ML analysis
# All insights are logged and saved, ready for ML engineers to use
# in improving model architecture and training strategy
logger.info("ML/DS analysis completed. Use insights in ml_insights.json for model improvements.")