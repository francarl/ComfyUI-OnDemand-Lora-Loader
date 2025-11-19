import requests
import json
import json
import os
import requests
import sys
import logging
from tqdm import tqdm
import folder_paths
from pathlib import Path
from nodes import LoraLoader
import server
from aiohttp import web
import json

from .nodes import _get_api_key_for_url, _download_model, logger

API_URL = "https://civitai.com/api/v1/models?types=LORA&favorites=true&nsfw=true"
LORA_CONFIG = None
SELECTED_LORA = None


def _fetch_data_from_api(url):
    try:
        apikey = os.environ.get('CIVITAI_TOKEN');
        headers = {
            "Authorization": f"Bearer {apikey}"
        } if apikey else None

        response = requests.get(url, headers=headers)
        response.raise_for_status()  
        
        return response.json()
    
    except Exception as e:
        logger.error("Error in retreving data from Civitai API: {e}", e)
        return None

def _transform_data_to_loras_structure(data):
    loras_list = []
    
    for item in data.get("items", []):
        main_model_name = item.get("name", "")
        model_versions = item.get("modelVersions", [])

        for version in model_versions:
            version_name = version.get("name", "")
            version_files = version.get("files", [])
            
            download_url = None
            is_model_type = False
            
            if version_files:
                first_file = version_files[0]
                if first_file.get("type") == "Model":
                    is_model_type = True
                    download_url = version.get("downloadUrl")

            if is_model_type and download_url:
                new_name = f"{main_model_name} - {version_name}"
                
                loras_list.append({
                    "name": new_name,
                    "url": download_url
                })

    return {
        "loras": loras_list
    }

def _get_lora_config():
    global LORA_CONFIG
    if LORA_CONFIG is not None:
        return LORA_CONFIG

    raw_data = _fetch_data_from_api(API_URL)
    if raw_data:
        lora_config = _transform_data_to_loras_structure(raw_data)
        none_entry = {"name": "None", "url": None}
        lora_config['loras'].insert(0, none_entry)
        LORA_CONFIG = lora_config
        return LORA_CONFIG
    
    return None

class OnDemandCivitaiLikedLoraLoader:

    @classmethod
    def INPUT_TYPES(cls):
        loras = { "loras": [] }
        global LORA_CONFIG
        LORA_CONFIG = _get_lora_config()
        if LORA_CONFIG:
            loras = [lora["name"] for lora in LORA_CONFIG.get("loras", []) ]
       
        return {
            "required": {
                "model": ("MODEL",),
                "lora_name": (loras,),
                "strength_model": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "strength_clip": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
            },
            "optional": {
                "clip": ("CLIP", ),
                "download_chunks": ("INT", {"default": 4, "min": 1, "max": 12, "step": 1})
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP")
    RETURN_NAMES = ("model", "clip")
    FUNCTION = "download_lora"
    DESCRIPTION = "Load loras models from CivitAI Liked/Favorites collection, they will be downloaded automatically if not found.\nPut a valid CivitAI API key in CIVITAI_TOKEN environment variable to access private user list"

    CATEGORY = "loaders"

    def download_lora(self, model, lora_name, strength_model, strength_clip, clip=None, api_key=None, download_chunks=None):
        self.lora_loader = LoraLoader()

        global LORA_CONFIG
        LORA_CONFIG = _get_lora_config()
        if not LORA_CONFIG:
            return model, clip # Return original model/clip if civitai api call fails

        destination_dir = os.path.join(folder_paths.models_dir, "loras")

        lora_url = None
        for lora_model in LORA_CONFIG.get("loras", []):
            if lora_model["name"] == lora_name:
                lora_url = lora_model["url"]
                break

        if not lora_url:
            logger.error(f"Model URL not found for name: {lora_name} in 'loras'")
            return model, clip # Return original model/clip if URL not found

        api_key = os.environ.get('CIVITAI_TOKEN')

        lora_filepath = _download_model(lora_url, lora_name, destination_dir, api_key, download_chunks)
        if not lora_filepath:
            return model, clip # Return original model/clip if download fails

        lora_filename = os.path.basename(lora_filepath)

        # Load the LORA using the existing LoraLoader
        model_lora, clip_lora = self.lora_loader.load_lora(model, clip, lora_filename, strength_model, strength_clip)
        return model_lora, clip_lora


@server.PromptServer.instance.routes.post("/francarl/lora_changed")
async def lora_changed_handler(request):
    global SELECTED_LORA, LORA_CONFIG
    data = await request.json()
    lora_name = data.get("lora_name")
    if lora_name:
        print(f"[OnDemandLoader] The user selected '{lora_name}'")
        if LORA_CONFIG:
            found_lora = next((lora for lora in LORA_CONFIG.get("loras", []) if lora["name"] == lora_name), None)

            if found_lora:
                SELECTED_LORA = found_lora
                print(f"[OnDemandLoader] Found and stored: {SELECTED_LORA}")
            else:
                print(f"[OnDemandLoader] Lora '{lora_name}' not found in LORA_CONFIG.")
        else:
            print("[OnDemandLoader] LORA_CONFIG is not loaded.")
    else:
        return web.Response(status=400, text=json.dumps({"error": "lora_name not provided"}), content_type='application/json')
    return web.Response(status=200, text=json.dumps({"status": "ok"}), content_type='application/json')
