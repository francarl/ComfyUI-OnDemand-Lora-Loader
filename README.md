# ComfyUI-CivitAI-Loader

This is a custom node for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that allows you to download and apply LoRA models directly from Civitai. It simplifies your workflow by managing LoRA downloads automatically, so you don't have to manually download files and place them in the correct folder.

## Features

*   **Automatic Downloading**: Downloads LoRA models from Civitai URLs specified in a configuration file.
*   **No Re-downloads**: Checks if a LoRA file already exists before attempting to download it.
*   **Progress Bar**: Displays a progress bar in the console during download.
*   **Private Model Support**: Access private or early-access models using your Civitai API key.
*   **Centralized Configuration**: Manage your list of LoRAs from a simple `config.json` file.
*   **Seamless Integration**: Functions as a standard LoRA loader node within the ComfyUI interface.

## Installation

1.  Navigate to your ComfyUI `custom_nodes` directory:
    ```bash
    cd ComfyUI/custom_nodes/
    ```
2.  Clone this repository:
    ```bash
    git clone https://github.com/francarl/ComfyUI-CivitAI-Loader.git
    ```
3.  Install the required dependencies:
    ```bash
    cd ComfyUI-CivitAI-Loader
    pip install -r requirements.txt
    ```
4.  Restart ComfyUI.

## Usage

### 1. Configure Your LoRAs

After installation, you need to configure the LoRAs you want to use.

1.  Navigate to the `ComfyUI/custom_nodes/ComfyUI-CivitAI-Loader/` directory.
2.  Create a file named `config.json`. If the file does not exist, the node will fall back to a default example configuration.
3.  Add your LoRAs to the `config.json` file. Each entry requires a `name` (which will appear in the node's dropdown menu) and a `url` (the Civitai **download** link).

You can get the download link from a model's page on Civitai by right-clicking the download button and copying the link address. It should look like `https://civitai.com/api/download/models/MODEL_ID`.

**Example `config.json`:**

```json
{
    "loras": [
        {
            "name": "Epi Noise Offset",
            "url": "https://civitai.com/api/download/models/16576"
        },
        {
            "name": "LowRA",
            "url": "https://civitai.com/api/download/models/63006"
        },
        {
            "name": "My Private Lora",
            "url": "https://civitai.com/api/download/models/123456?type=Model&format=SafeTensor"
        }
    ]
}
```

### 2. Add the Node in ComfyUI

1.  In ComfyUI, double-click on the canvas to open the search menu.
2.  Search for and add the **`CivitAI Lora Loader`** node.
3.  Connect it in your workflow just as you would with a standard `LoraLoader` node.

### 3. Node Inputs

*   `model`: The input model from a checkpoint loader.
*   `clip` (optional): The input CLIP from a checkpoint loader.
*   `lora_name`: A dropdown menu to select the LoRA you configured in `config.json`.
*   `strength_model`: The strength of the LoRA applied to the model.
*   `strength_clip`: The strength of the LoRA applied to the CLIP model.
*   `api_key` (optional): Your Civitai API key. Use this to download private or early-access models. Alternatively, you can set the `CIVITAI_TOKEN` environment variable.
*   `download_chunks` (optional): The chunk size (in KB) for downloading files. Adjust if you experience slow downloads.

The first time you select a LoRA, it will be downloaded to your `ComfyUI/models/loras/` directory. Subsequent uses will load the existing file.

## License

This project is licensed under the MIT License. See the [LICENSE.txt](LICENSE.txt) file for details.