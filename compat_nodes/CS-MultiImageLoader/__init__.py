"""Compatibility node for the supplied H3 low-VRAM workflow.

The source workflow references CS-MultiImageLoader but no public Manager
catalogue entry or upstream source could be identified.  This preserves the
workflow's node name, input names and five IMAGE outputs without changing its
graph.  It is intentionally limited to local ComfyUI input files.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageOps
import torch

import folder_paths


_RESAMPLING = {
    "nearest": Image.Resampling.NEAREST,
    "bilinear": Image.Resampling.BILINEAR,
    "bicubic": Image.Resampling.BICUBIC,
    "lanczos": Image.Resampling.LANCZOS,
}


class CSMultiImageLoader:
    """Load up to four newline-separated ComfyUI input images."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_paths": ("STRING", {"multiline": True, "default": ""}),
                "width": ("INT", {"default": 0, "min": 0, "max": 16384}),
                "height": ("INT", {"default": 0, "min": 0, "max": 16384}),
                "interpolation": (["nearest", "bilinear", "bicubic", "lanczos"], {"default": "lanczos"}),
                "resize_method": (["crop", "stretch"], {"default": "crop"}),
                "multiple_of": ("INT", {"default": 32, "min": 1, "max": 1024}),
                "img_compression": ("INT", {"default": 18, "min": 0, "max": 100}),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "IMAGE", "IMAGE")
    RETURN_NAMES = ("multi_output", "image_1", "image_2", "image_3", "image_4")
    FUNCTION = "load_images"
    CATEGORY = "H3 compatibility"

    @staticmethod
    def _target_size(width: int, height: int, multiple_of: int) -> tuple[int, int] | None:
        if width <= 0 or height <= 0:
            return None
        return (
            max(multiple_of, width - (width % multiple_of)),
            max(multiple_of, height - (height % multiple_of)),
        )

    @staticmethod
    def _to_image_tensor(image: Image.Image) -> torch.Tensor:
        array = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
        return torch.from_numpy(array)[None,]

    def load_images(self, image_paths, width, height, interpolation, resize_method, multiple_of, img_compression):
        del img_compression  # retained for workflow compatibility
        names = [line.strip() for line in image_paths.splitlines() if line.strip()][:4]
        if not names:
            raise ValueError("CS-MultiImageLoader needs at least one input image path")

        target = self._target_size(width, height, multiple_of)
        tensors = []
        for name in names:
            path = Path(folder_paths.get_annotated_filepath(name))
            if not path.is_file():
                raise FileNotFoundError(f"ComfyUI input image was not found: {name}")
            with Image.open(path) as opened:
                image = ImageOps.exif_transpose(opened).convert("RGB")
            if target:
                if resize_method == "crop":
                    image = ImageOps.fit(image, target, method=_RESAMPLING[interpolation])
                else:
                    image = image.resize(target, resample=_RESAMPLING[interpolation])
            tensors.append(self._to_image_tensor(image))

        while len(tensors) < 4:
            tensors.append(tensors[-1])

        # multi_output is only a batch when image sizes match; the workflow's
        # individual image outputs stay valid even when its input sizes differ.
        try:
            multi_output = torch.cat(tensors, dim=0)
        except RuntimeError:
            multi_output = tensors[0]
        return (multi_output, tensors[0], tensors[1], tensors[2], tensors[3])


NODE_CLASS_MAPPINGS = {"CS-MultiImageLoader": CSMultiImageLoader}
NODE_DISPLAY_NAME_MAPPINGS = {"CS-MultiImageLoader": "CS Multi Image Loader (H3 compatibility)"}
