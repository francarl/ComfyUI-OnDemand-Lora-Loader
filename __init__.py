from .nodes import OnDemandLoraLoader, OnDemandUNETLoader, OnDemandCheckpointLoader, OnDemandVAELoader, OnDemandCLIPLoader, OnDemandGGUFLoader, OnDemandControlNetLoader
from .lora_node import OnDemandCivitaiLikedLoraLoader


NODE_CLASS_MAPPINGS = {
    "OnDemandLoraLoader": OnDemandLoraLoader,
    "OnDemandUNETLoader": OnDemandUNETLoader,
    "OnDemandCheckpointLoader": OnDemandCheckpointLoader,
    "OnDemandVAELoader": OnDemandVAELoader,
    "OnDemandCLIPLoader": OnDemandCLIPLoader,
    "OnDemandGGUFLoader": OnDemandGGUFLoader,
    "OnDemandControlNetLoader": OnDemandControlNetLoader,
    "OnDemandCivitaiLikedLoraLoader": OnDemandCivitaiLikedLoraLoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OnDemandLoraLoader": "OnDemand Lora Loader",
    "OnDemandUNETLoader": "OnDemand UNET Loader",
    "OnDemandCheckpointLoader": "OnDemand Checkpoint Loader",
    "OnDemandVAELoader": "OnDemand VAE Loader",
    "OnDemandCLIPLoader": "OnDemand CLIP Loader",
    "OnDemandGGUFLoader": "OnDemand GGUF Loader",
    "OnDemandControlNetLoader": "OnDemand ControlNet Loader",
    "OnDemandCivitaiLikedLoraLoader": "OnDemand Civitai Liked Lora Loader"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

# Module metadata
__version__ = "1.0.4"
__author__ = "francarl"
__description__ = "A suite of nodes for on-demand loading of Diffusion Models, VAE, Clip and Loras in ComfyUI."
