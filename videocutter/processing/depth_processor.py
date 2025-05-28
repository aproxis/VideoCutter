# videocutter/processing/depth_processor.py
# Handles applying DepthFlow effects to images.

import itertools
import math
import os
import time
import random
from abc import abstractmethod # abstractmethod was used in DepthManager
from pathlib import Path
from threading import Thread
from typing import List, Type # Self was used but requires Python 3.11, using Type for broader compatibility for now

from attr import Factory, define # Using define from attr, not attrs
from DepthFlow import DepthScene
from DepthFlow.Motion import Animation, Components, Preset, Presets, Target
from DepthFlow.State import DepthState
from dotmap import DotMap

# Assuming these custom externals are available in the Python path
# If they are part of this project, their new location needs to be referenced.
# For now, keeping original import paths.
from Broken.Externals.Depthmap import DepthAnythingV2, DepthEstimator
from Broken.Externals.Upscaler import BrokenUpscaler, NoUpscaler

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1" # Should be set once at app start if possible

def _combinations(**options):
    """Helper for generating combinations for DotMap."""
    for combination in itertools.product(*options.values()):
        yield DotMap(zip(options.keys(), combination))

# YourScene is simple, can be defined here or passed as a type if more complex scenes are needed.
class DefaultDepthScene(DepthScene): # Renamed from YourScene for clarity
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Randomize parameters for continuous base motion
        self._offset_x_amplitude = random.uniform(0.1, 0.2) # Amplitude for horizontal motion (reduced)
        self._offset_x_frequency = random.uniform(0.8, 1.2) # Frequency for horizontal motion
        self._zoom_amplitude = random.uniform(0.01, 0.05) # Amplitude for zoom motion (significantly reduced)
        self._zoom_frequency = random.uniform(1.5, 2.5) # Frequency for zoom motion
        self._initial_phase_x = random.uniform(0, 2 * math.pi) # Random initial phase for x
        self._initial_phase_zoom = random.uniform(0, 2 * math.pi) # Random initial phase for zoom

    def update(self):
        # Reintroduce continuous motion with randomized parameters
        self.state.offset_x = self._offset_x_amplitude * math.sin(self.cycle * self._offset_x_frequency + self._initial_phase_x)
        self.state.zoom = 0.7 + self._zoom_amplitude * math.sin(self.cycle * self._zoom_frequency + self._initial_phase_zoom)
        self.state.isometric = 1 # Example, can be driven by config
        # Removed hardcoded zoom animation. Zoom is now controlled by ConfigurableDepthManager.animate

@define
class ConfigurableDepthManager: # No longer inherits from a local DepthManager
    # Fields from original DepthManager
    estimator: DepthEstimator = Factory(DepthAnythingV2)
    upscaler: BrokenUpscaler = Factory(NoUpscaler)
    threads: List[Thread] = Factory(list)
    outputs: List[Path] = Factory(list)
    
    # New config attribute
    config: DotMap = Factory(DotMap) 
    
    # Concurrency can be part of config or initialized
    concurrency: int = 1 # Default, will be set from config in __attrs_post_init__

    def __attrs_post_init__(self):
        self.estimator.load_torch()
        self.estimator.load_model()
        self.upscaler.load_model()
        # Set concurrency from config, falling back to env var then 1
        self.concurrency = self.config.get('workers', int(os.getenv("WORKERS", 1)))

    def __enter__(self): # Python 3.11+ can use -> Self:
        self.outputs = list()
        return self

    def __exit__(self, *ignore) -> None:
        self.join()

    def parallax(self, scene_class: Type[DepthScene], image_path: Path) -> None:
        while len(self.threads) >= self.concurrency:
            self.threads = [t for t in self.threads if t.is_alive()]
            time.sleep(0.05)

        thread = Thread(target=self._worker, args=(scene_class, image_path), daemon=True)
        self.threads.append(thread)
        thread.start()

    def _worker(self, scene_class: Type[DepthScene], image_path: Path):
        scene_instance = scene_class(backend="headless")
        scene_instance.estimator = self.estimator
        scene_instance.set_upscaler(self.upscaler)
        scene_instance.input(image=image_path)

        for data_combination in _combinations(**self.variants(image_path)):
            data_combination.update(scene=scene_instance, image=image_path)
            
            output_file = self.filename(data_combination)
            scene_instance.clear_animations()
            self.animate(data_combination) # Pass the combined data

            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            video_result = scene_instance.main(output=output_file, **data_combination.render)
            if video_result and video_result[0]:
                self.outputs.append(video_result[0])
        
        scene_instance.window.destroy()

    def join(self):
        for thread in self.threads:
            thread.join()
            
    # filename, animate, variants methods remain largely the same,
    # but ensure they use self.config where appropriate.
    # Original filename to use config for output path construction if needed,
    # or ensure data.image.parent is correctly set to the working datetime_folder.
    # The original filename method seems to save in the same parent as the image.
    def filename(self, data: DotMap) -> Path:
        """Output path for rendered depth video."""
        # data.image is a Path object to the input image
        return data.image.parent / (data.image.stem + "_df.mp4")

    def animate(self, data: DotMap) -> None:
        """Add preset system's animations to each export."""
        data.scene.add_animation(DepthState(
            vignette_enable=self.config.get('depthflow.vignette_enable', True),
            dof_enable=self.config.get('depthflow.dof_enable', True),
        ))

        # Configure available animations with their parameters
        animations_config = self.config.get('depthflow.animations', [
            ("Circle", {"intensity_min": 0.3, "intensity_max": 0.5}),
            ("Orbital", {"intensity_min": 0.3, "intensity_max": 0.5}),
            ("Dolly", {"intensity_min": 0.2, "intensity_max": 0.4}),
            ("Horizontal", {"intensity_min": 0.2, "intensity_max": 0.4}),
            ("Vertical", {"intensity_min": 0.2, "intensity_max": 0.4}),
            ("Zoom", {"intensity_min": 0.15, "intensity_max": 0.25}),  # Much lower zoom intensity
        ])
        
        # Build available animations list
        possible_animations = []
        for name, params in animations_config:
            intensity = round(random.uniform(params["intensity_min"], params["intensity_max"]), 2)
            reverse = random.choice([True, False])
            
            if name == "Circle": 
                possible_animations.append(("Circle", Presets.Circle(intensity=intensity, loop=True, reverse=reverse)))
            elif name == "Orbital": 
                possible_animations.append(("Orbital", Presets.Orbital(intensity=intensity, loop=True, reverse=reverse)))
            elif name == "Dolly": 
                possible_animations.append(("Dolly", Presets.Dolly(intensity=intensity, loop=True, reverse=reverse)))
            elif name == "Horizontal": 
                possible_animations.append(("Horizontal", Presets.Horizontal(intensity=intensity, loop=True, reverse=reverse)))
            elif name == "Vertical":
                possible_animations.append(("Vertical", Presets.Vertical(intensity=intensity, loop=True, reverse=reverse)))
            elif name == "Zoom":
                possible_animations.append(("Zoom", Presets.Zoom(intensity=intensity, loop=True, reverse=reverse)))

        # Set base 3D properties (these don't create motion, just set the 3D appearance)
        isometric_value = round(random.uniform(
            self.config.get('depthflow.isometric_min', 0.4), 
            self.config.get('depthflow.isometric_max', 0.5)
        ), 2)
        height_value = round(random.uniform(
            self.config.get('depthflow.height_min', 0.1), 
            self.config.get('depthflow.height_max', 0.15)
        ), 2)

        data.scene.add_animation(Components.Set(target=Target.Isometric, value=isometric_value))
        data.scene.add_animation(Components.Set(target=Target.Height, value=height_value))
        
        # REMOVED: The always-applied base zoom that was causing excessive zoom
        # Old code: data.scene.add_animation(Presets.Zoom(intensity=zoom_value, loop=zoom_loops))

        # Apply multiple random animations
        applied_animations_log = []
        applied_names = set()
        
        # Allow more effects per image for variety
        num_animations_to_apply = random.randint(
            self.config.get('depthflow.min_effects_per_image', 2), 
            self.config.get('depthflow.max_effects_per_image', 4)
        )

        # Control zoom probability - make zoom less likely to be selected
        zoom_probability = self.config.get('depthflow.zoom_probability', 0.3)  # 30% chance
        
        if possible_animations:
            for _ in range(num_animations_to_apply):
                available_choices = [anim for anim in possible_animations if anim[0] not in applied_names]
                if not available_choices: 
                    break
                    
                # Filter out zoom if we want to reduce its probability
                if random.random() > zoom_probability:
                    available_choices = [anim for anim in available_choices if anim[0] != "Zoom"]
                
                if not available_choices:  # If no non-zoom choices, allow zoom
                    available_choices = [anim for anim in possible_animations if anim[0] not in applied_names]
                
                if available_choices:
                    name, animation_preset = random.choice(available_choices)
                    applied_names.add(name)
                    data.scene.add_animation(animation_preset)
                    applied_animations_log.append(f"Animation: {name}, Preset: {animation_preset}")
        
        # Enhanced logging
        log_file_path = Path(self.config.get('output_datetime_folder', '.')) / "_depth_log.txt"
        with open(log_file_path, "a") as f:
            log_entry = (
                f"Image: {data.image.stem}\n"
                f"Isometric: {isometric_value}\n"
                f"Height: {height_value}\n"
                f"Applied {len(applied_animations_log)} animations:\n"
            )
            for anim_log in applied_animations_log:
                log_entry += f"  {anim_log}\n"
            f.write(log_entry + "\n")

    def variants(self, image: Path) -> DotMap:
        # segment_duration should come from the main config
        # segment_duration and fps should come from the main config (top level)
        # If DepthFlow produces videos 1s shorter, let's try adding 1 to the time passed to it.
        segment_duration_for_df = self.config.get('segment_duration', 5)
        render_height = self.config.get('depthflow.render_height', 1920) # This is correct, render_height is a depthflow specific setting
        render_fps = self.config.get('fps', 25) # Use top-level fps
        
        print(f"DepthFlow variants: Requesting time={segment_duration_for_df}s for output (target segment duration {self.config.get('segment_duration', 5)}s)")

        return DotMap(
            variation=[0], # From original YourManager
            render=_combinations(
                height=[render_height],
                time=[segment_duration_for_df], # Use adjusted time
                loop=[1], # From original YourManager
                fps=[render_fps],
            )
        )

def apply_depth_effects(image_file_paths: List[str], config_params: DotMap) -> List[str]:
    """
    Applies DepthFlow effects to a list of images.

    Args:
        image_file_paths (List[str]): List of absolute paths to image files.
        config_params (dict): Configuration dictionary. Expected keys include:
            'depthflow': {
                'segment_duration': int,
                'render_height': int,
                'render_fps': int,
                'vignette_enable': bool, (optional)
                'dof_enable': bool, (optional)
                'animations': list of tuples (name, params), (optional)
                'isometric_min': float, (optional)
                # ... other depthflow specific params
            },
            'output_datetime_folder': str (for logging)
            'workers': int (concurrency for DepthManager, optional, defaults to env WORKERS or 1)


    Returns:
        List[str]: List of paths to the generated depth video files.
    """
    print("Applying DepthFlow effects...")
    
    # Convert config_params dict to DotMap for easier access if DepthManager expects it
    # Or adapt DepthManager to use dicts. For now, assuming DotMap is fine.
    cfg = DotMap(config_params)

    # Ensure PYTORCH_ENABLE_MPS_FALLBACK is set (ideally once at app startup)
    os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
    
    # Upscaler can be made configurable too
    upscaler_choice = cfg.get('depthflow.upscaler', 'NoUpscaler')
    upscaler_instance = NoUpscaler() # Default
    # if upscaler_choice == 'Upscayl': from Broken.Externals.Upscaler import Upscayl; upscaler_instance = Upscayl()
    
    # Estimator can also be made configurable
    estimator_instance = DepthAnythingV2() # Default

    concurrency = cfg.get('workers', int(os.getenv("WORKERS", 1)))

    processed_video_paths = []

    # The DepthManager uses pathlib.Path, so convert strings to Path objects
    image_paths_as_path_obj = [Path(p) for p in image_file_paths]

    try:
        with ConfigurableDepthManager(
            estimator=estimator_instance, 
            upscaler=upscaler_instance, 
            concurrency=concurrency,
            config=cfg # Pass the config
            ) as manager:
            for image_path_obj in image_paths_as_path_obj:
                if image_path_obj.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    print(f"Processing image with DepthFlow: {image_path_obj}")
                    # Scene type can also be made configurable if needed
                    manager.parallax(DefaultDepthScene, image_path_obj) 
                else:
                    print(f"Skipping non-image file for DepthFlow: {image_path_obj}")
            
            manager.join() # Wait for all threads to complete
            processed_video_paths = [str(p) for p in manager.outputs]

    except Exception as e:
        print(f"An error occurred during DepthFlow processing: {e}")
        # Potentially re-raise or handle more gracefully

    print(f"DepthFlow effects application complete. Generated {len(processed_video_paths)} videos.")
    return processed_video_paths

if __name__ == "__main__":
    print("depth_processor.py executed directly (for testing).")
    # This requires setting up a dummy config and image files.
    # Example (conceptual):
    # test_image_dir = "temp_depth_test_images"
    # os.makedirs(test_image_dir, exist_ok=True)
    # # Create a dummy image e.g., test_image_dir/test01.jpg
    # with open(os.path.join(test_image_dir, "test01.jpg"), "w") as f: f.write("dummy") # Needs real image
    
    # mock_config = {
    #     'depthflow': {
    #         'segment_duration': 5,
    #         'render_height': 1080, # Smaller for faster test
    #         'render_fps': 25,
    #         'vignette_enable': True,
    #         'dof_enable': True,
    #         'isometric_min': 0.4,
    #         'isometric_max': 0.5,
    #         'height_min': 0.1,
    #         'height_max': 0.15,
    #         'zoom_min': 0.65,
    #         'zoom_max': 0.75,
    #         'min_effects_per_image': 1,
    #         'max_effects_per_image': 1,
    #         'animations': [("Circle", {"intensity_min": 0.6, "intensity_max": 0.7})]
    #     },
    #     'output_datetime_folder': test_image_dir, # For _depth_log.txt
    #     'workers': 1 
    # }
    # test_images = [os.path.abspath(os.path.join(test_image_dir, "test01.jpg"))]
    # if os.path.exists(test_images[0]): # Check if dummy image was created
    #    generated_videos = apply_depth_effects(test_images, mock_config)
    #    print(f"Generated videos: {generated_videos}")
    # else:
    #    print(f"Test image {test_images[0]} not found. Skipping apply_depth_effects test.")
    # shutil.rmtree(test_image_dir, ignore_errors=True)
    print("Depth processor test placeholder finished.")
