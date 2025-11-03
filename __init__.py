import json
import os
import requests
import sys
import logging
from tqdm import tqdm
import re
import folder_paths
from nodes import LoraLoader
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Logger initialization 
MSG_PREFIX = "[CivitAI LORA Loader]"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(MSG_PREFIX + ' %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Function to load configuration 
def load_config(config_filename="config.json"):
    
    current_dir = os.path.dirname(__file__)
    config_path = os.path.join(current_dir, config_filename)
    
    default_config = { 
        "loras": [
            {
                "name": "Lora n1",
                "url": "not_valid_url",
            },
            {
                "name": "Lora n2",
                "url": "not_valid_url"
            }
        ]
    }

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Successfully loaded configuration from {config_filename}")
        return config
    except FileNotFoundError:
        logger.warning(f"Configuration file '{config_path}' not found. Using default fallback configuration.")
        return default_config
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from '{config_path}'. Using default fallback configuration.")
        return default_config
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading '{config_path}': {e}. Using default fallback.")
        return default_config

NODE_CONFIG = load_config()

class CivitAILoraLoader:

    @classmethod
    def INPUT_TYPES(cls):

        loras = [lora["name"] for lora in NODE_CONFIG.get("loras", []) ]
       
        return {
            "required": {
                "model": ("MODEL",),
                "lora_name": (loras,),
                "strength_model": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "strength_clip": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
            },
            "optional": {
                "clip": ("CLIP", ),
                "api_key": ("STRING", {"default": None, "multiline": False}),
                "download_chunks": ("INT", {"default": 4, "min": 1, "max": 12, "step": 1})
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP")
    RETURN_NAMES = ("model", "clip")
    FUNCTION = "download_lora"
    DESCRIPTION = "Load loras models from CivitAI, they will be downloaded automatically if not found.\nPut a valid CivitAI API key in form field 'api_key' or in CIVITAI_TOKEN environment variable to access private models"

    CATEGORY = "loaders"

    def add_query_param(self, url, param_key, param_value):
        parsed_url = urlparse(url)
        query_dict = parse_qs(parsed_url.query)
        query_dict[param_key] = [param_value]
        encoded_query = urlencode(query_dict, doseq=True)
        new_url = urlunparse(parsed_url._replace(query=encoded_query))
        return new_url

    def download_lora(self, model, lora_name, strength_model, strength_clip, clip=None, api_key=None, download_chunks=None):
        self.lora_loader = LoraLoader()

        loras_models_dir = os.path.join(folder_paths.models_dir, "loras")
        os.makedirs(loras_models_dir, exist_ok=True)

        api_key = api_key or os.environ.get('CIVITAI_TOKEN')

        # get model info from url
        lora_url = None
        for lora in NODE_CONFIG["loras"]:
            if lora["name"] == lora_name:
                lora_url = lora["url"]
                break
        if not lora_url:
            logger.error(f"Lora URL not found for name: {lora_name}")
            return model, clip

        if api_key:
            logger.info("Using provided API key for CivitAI.")
            lora_url = self.add_query_param(lora_url, 'token', api_key) if api_key else lora_url

        response = requests.get(lora_url, stream=True, allow_redirects=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        lora_filename = None

        content_disposition = response.headers.get('Content-Disposition')
        if content_disposition:
            filename_match = re.search(r'filename="?([^"]+)"?', content_disposition)
            if filename_match:
                lora_filename = filename_match.group(1).strip()

        lora_filepath = os.path.join(loras_models_dir, lora_filename)

        # Check if the file already exists
        if os.path.exists(lora_filepath):
            logger.info(f"LORA file '{lora_filename}' already exists at '{lora_filepath}'. Skipping download.")
        else:
            logger.info(f"Downloading LORA '{lora_filename}' from '{lora_url}' to '{lora_filepath}'")
            try:
                total_size = int(response.headers.get('content-length', 0))
                block_size = download_chunks * 1024  # x Kilobytes
                progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)

                with open(lora_filepath, 'wb') as f:
                    for data in response.iter_content(block_size):
                        progress_bar.update(len(data))
                        f.write(data)
                progress_bar.close()
                logger.info(f"Successfully downloaded '{lora_name}'.")
            except requests.exceptions.RequestException as e:
                logger.error(f"Error downloading LORA '{lora_name}': {e}")
                return model, clip
            except Exception as e:
                logger.error(f"An unexpected error occurred during download of '{lora_name}': {e}")
                return model, clip

        # Load the LORA using the existing LoraLoader
        model_lora, clip_lora = self.lora_loader.load_lora(model, clip, lora_filename, strength_model, strength_clip)
        return model_lora, clip_lora




NODE_CLASS_MAPPINGS = {
    "CivitAILoraLoader": CivitAILoraLoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CivitAILoraLoader": "CivitAI Lora Loader"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']