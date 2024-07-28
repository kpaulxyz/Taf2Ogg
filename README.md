# Toniebox Chapter Extractor

This script extracts chapter information from a Toniebox file, converts it to audio chapters, and splits the audio into separate files.

## Prerequisites

Ensure you have Python 3 installed on your system.
FFmpeg must be installed and accessible via the $PATH environment variable.

## Installation

1. Clone this repository or download the script files.

2. Navigate to the project directory.

3. Install the required dependencies using `pip`:
    ```bash
    pip install -r requirements.txt
    ```
## Usage

To run the script, use the following command:

```bash
python Taf2Ogg.py <tonie_file> <output_directory>
    <tonie_file>: The path to the Toniebox file you want to process.
    <output_directory>: The directory where the extracted chapters will be saved.

python Taf2Ogg.py CONTENT/8D77321C/500304E0 ./output_chapters
```

## Notes

    The script assumes the sample rate for the Toniebox Opus audio is 48000 Hz.
    If the Toniebox has not cached the entire file, extraction of all chapters may not be possible.
