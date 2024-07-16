import json

def format_workflow(workflow_string,data):
    try:
        formatted_json = workflow_string.format(**data)
        return json.loads(formatted_json), None
    except KeyError as e:
        return None, {{"error": f"Missing key in data: {{str(e)}}"}}
    
  
# URL for face pose image
face_pose_url = 'https://res.cloudinary.com/dtsxndikq/image/upload/v1719584574/face-pose.png'

# JSON template as a string with placeholders
generate = '''
{{
  "2": {{
    "inputs": {{
      "ckpt_name": "epicrealism_naturalSinRC1VAE.safetensors"
    }},
    "class_type": "CheckpointLoaderSimple",
    "_meta": {{
      "title": "Load Checkpoint"
    }}
  }},
  "4": {{
    "inputs": {{
      "text": " {positiveprompt} sunny, bright, professional photoshoot, ultra realistic, 4K, product picture, no human, beautiful landscape, clean",
      "clip": [
        "2",
        1
      ]
    }},
    "class_type": "CLIPTextEncode",
    "_meta": {{
      "title": "CLIP Text Encode (Prompt)"
    }}
  }},
  "5": {{
    "inputs": {{
      "text": "{negativeprompt} dark, poor textures, worst quality, multiple objects",
      "clip": [
        "2",
        1
      ]
    }},
    "class_type": "CLIPTextEncode",
    "_meta": {{
      "title": "CLIP Text Encode (Prompt)"
    }}
  }},
  "7": {{
    "inputs": {{
      "samples": [
        "19",
        0
      ],
      "vae": [
        "2",
        2
      ]
    }},
    "class_type": "VAEDecode",
    "_meta": {{
      "title": "VAE Decode"
    }}
  }},
  "19": {{
    "inputs": {{
      "seed": {seed},
      "steps": 25,
      "cfg": 2,
      "sampler_name": "dpmpp_2m_sde",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "209",
        0
      ],
      "positive": [
        "77",
        0
      ],
      "negative": [
        "77",
        1
      ],
      "latent_image": [
        "50",
        0
      ]
    }},
    "class_type": "KSampler",
    "_meta": {{
      "title": "KSampler"
    }}
  }},
  "35": {{
    "inputs": {{
      "mask": [
        "194",
        0
      ]
    }},
    "class_type": "MaskToImage",
    "_meta": {{
      "title": "Convert Mask to Image"
    }}
  }},
  "50": {{
    "inputs": {{
      "pixels": [
        "35",
        0
      ],
      "vae": [
        "2",
        2
      ]
    }},
    "class_type": "VAEEncode",
    "_meta": {{
      "title": "VAE Encode"
    }}
  }},
  "75": {{
    "inputs": {{
      "expand": 0,
      "incremental_expandrate": 0,
      "tapered_corners": true,
      "flip_input": false,
      "blur_radius": 10,
      "lerp_alpha": 1,
      "decay_factor": 1,
      "fill_holes": false,
      "mask": [
        "227",
        0
      ]
    }},
    "class_type": "GrowMaskWithBlur",
    "_meta": {{
      "title": "Grow Mask With Blur"
    }}
  }},
  "77": {{
    "inputs": {{
      "multiplier": 0.17,
      "positive": [
        "4",
        0
      ],
      "negative": [
        "5",
        0
      ],
      "vae": [
        "2",
        2
      ],
      "foreground": [
        "78",
        0
      ]
    }},
    "class_type": "ICLightConditioning",
    "_meta": {{
      "title": "IC-Light Conditioning"
    }}
  }},
  "78": {{
    "inputs": {{
      "pixels": [
        "252",
        0
      ],
      "vae": [
        "2",
        2
      ]
    }},
    "class_type": "VAEEncode",
    "_meta": {{
      "title": "VAE Encode"
    }}
  }},
  "194": {{
    "inputs": {{
      "min": 0,
      "max": 1,
      "mask": [
        "75",
        0
      ]
    }},
    "class_type": "RemapMaskRange",
    "_meta": {{
      "title": "Remap Mask Range"
    }}
  }},
  "209": {{
    "inputs": {{
      "model_path": "iclight_sd15_fc.safetensors",
      "model": [
        "2",
        0
      ]
    }},
    "class_type": "LoadAndApplyICLightUnet",
    "_meta": {{
      "title": "Load And Apply IC-Light"
    }}
  }},
  "214": {{
    "inputs": {{
      "model_name": "GroundingDINO_SwinT_OGC (694MB)"
    }},
    "class_type": "GroundingDinoModelLoader (segment anything)",
    "_meta": {{
      "title": "GroundingDinoModelLoader (segment anything)"
    }}
  }},
  "216": {{
    "inputs": {{
      "prompt": "subject",
      "threshold": 0.4,
      "sam_model": [
        "218",
        0
      ],
      "grounding_dino_model": [
        "214",
        0
      ],
      "image": [
        "252",
        0
      ]
    }},
    "class_type": "GroundingDinoSAMSegment (segment anything)",
    "_meta": {{
      "title": "GroundingDinoSAMSegment (segment anything)"
    }}
  }},
  "218": {{
    "inputs": {{
      "model_name": "sam_vit_b (375MB)"
    }},
    "class_type": "SAMModelLoader (segment anything)",
    "_meta": {{
      "title": "SAMModelLoader (segment anything)"
    }}
  }},
  "220": {{
    "inputs": {{
      "expand": 0,
      "incremental_expandrate": 0,
      "tapered_corners": true,
      "flip_input": false,
      "blur_radius": 0.5,
      "lerp_alpha": 1,
      "decay_factor": 1,
      "fill_holes": false,
      "mask": [
        "216",
        1
      ]
    }},
    "class_type": "GrowMaskWithBlur",
    "_meta": {{
      "title": "Grow Mask With Blur"
    }}
  }},
  "222": {{
    "inputs": {{
      "blend_percentage": 0.5,
      "image_a": [
        "7",
        0
      ],
      "image_b": [
        "252",
        0
      ],
      "mask": [
        "223",
        0
      ]
    }},
    "class_type": "Image Blend by Mask",
    "_meta": {{
      "title": "Image Blend by Mask"
    }}
  }},
  "223": {{
    "inputs": {{
      "mask": [
        "220",
        0
      ]
    }},
    "class_type": "MaskToImage",
    "_meta": {{
      "title": "Convert Mask to Image"
    }}
  }},
  "224": {{
    "inputs": {{
      "images": [
        "222",
        0
      ]
    }},
    "class_type": "PreviewImage",
    "_meta": {{
      "title": "Preview Image"
    }}
  }},
  "227": {{
    "inputs": {{
      "channel": "red",
      "image": [
        "249",
        0
      ]
    }},
    "class_type": "ImageToMask",
    "_meta": {{
      "title": "Convert Image to Mask"
    }}
  }},
  "249": {{
    "inputs": {{
      "width": 512,
      "height": 512,
      "upscale_method": "nearest-exact",
      "keep_proportion": false,
      "divisible_by": 2,
      "image": [
        "265",
        0
      ],
      "get_image_size": [
        "252",
        0
      ]
    }},
    "class_type": "ImageResizeKJ",
    "_meta": {{
      "title": "Resize Image"
    }}
  }},
  "252": {{
    "inputs": {{
      "size": 1024,
      "interpolation_mode": "bicubic",
      "image": [
        "264",
        0
      ]
    }},
    "class_type": "JWImageResizeByLongerSide",
    "_meta": {{
      "title": "Image Resize by Longer Side"
    }}
  }},
  "264": {{
    "inputs": {{
      "image": "{productimageurl}",
      "keep_alpha_channel": false,
      "output_mode": false
    }},
    "class_type": "LoadImageFromUrl",
    "_meta": {{
      "title": "Load Image From URL"
    }}
  }},
  "265": {{
    "inputs": {{
      "image": "https://res.cloudinary.com/dtsxndikq/image/upload/v1721166828/light.png",
      "keep_alpha_channel": false,
      "output_mode": false
    }},
    "class_type": "LoadImageFromUrl",
    "_meta": {{
      "title": "Load Image From URL"
    }}
  }},
  "269": {{
    "inputs": {{
      "output_path": "temporal",
      "filename_prefix": "product-{gen_id}",
      "filename_delimiter": "_",
      "filename_number_padding": 1,
      "filename_number_start": "false",
      "extension": "png",
      "dpi": 300,
      "quality": 100,
      "optimize_image": "true",
      "lossless_webp": "false",
      "overwrite_mode": "false",
      "show_history": "false",
      "show_history_by_prefix": "true",
      "embed_workflow": "true",
      "show_previews": "true",
      "images": [
        "222",
        0
      ]
    }},
    "class_type": "Image Save",
    "_meta": {{
      "title": "Image Save"
    }}
  }}
}}'''


example_pp='blue bike standing on rocks,beach, sand, rocks, summer, \nsunny, bright, forestation, professional photoshoot, ultra realistic, 4K, product picture, no human, beautiful landscape, clean'
example_np='dark, poor textures, worst quality, multiple objects, human, girl, human face'