import itertools
import math
import os
import time
import random  # Importing random for randomness in animations
import argparse

from abc import abstractmethod
from pathlib import Path
from threading import Thread
from typing import List, Self, Type

from attr import Factory, define
from click import clear
from DepthFlow import DepthScene
from DepthFlow.Motion import Animation, Components, Preset, Presets, Target
from DepthFlow.State import DepthState
from dotmap import DotMap

from Broken.Externals.Depthmap import DepthAnythingV2, DepthEstimator
from Broken.Externals.Upscaler import BrokenUpscaler, NoUpscaler

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

parser = argparse.ArgumentParser(description="Create DepthFlow")
# Create an ArgumentParser to handle command-line arguments
parser.add_argument('--o', dest='path', required=True, help='Path to the directory containing files to be sorted.')
parser.add_argument('--d', dest='datetimeStr', required=True, help='Datetime folder name.')
parser.add_argument('--t', type=int, default=5, dest='slide_time', help='Frame duration.')
parser.add_argument('--tl', type=int, default=595, dest='time_limit', help='Duration of clip')

args = parser.parse_args()
output_folder = args.path
datetime_str = args.datetimeStr

datetime_folder = os.path.join(output_folder, datetime_str)
os.makedirs(datetime_folder, exist_ok=True)

image_paths = [f for f in os.listdir(datetime_folder) if f.endswith('.jpg') or f.endswith('.jpeg')]
video_paths = [f for f in os.listdir(datetime_folder) if f.endswith('.mp4')]
merged_paths = sorted(image_paths + video_paths, key=lambda x: x.lower())

# limit number of values in "merged_paths"
limit = int(args.time_limit/args.slide_time - 3)
merged_paths = merged_paths[:limit]

# delete images that are not in "merged_paths" from disk
for image_path in image_paths:
    if image_path not in merged_paths:
        os.remove(os.path.join(datetime_folder, image_path))
        print(f"Deleted image: {image_path}")

# delete videos that are not in "merged_paths" from disk
for video_path in video_paths:
    if video_path not in merged_paths:
        os.remove(os.path.join(datetime_folder, video_path))
        print(f"Deleted video: {video_path}")

def combinations(**options):
    """Returns a dictionary of key='this' of itertools.product"""
    for combination in itertools.product(*options.values()):
        yield DotMap(zip(options.keys(), combination))


# Note: You can also use your own subclassing like Custom.py!
class YourScene(DepthScene):
    def update(self):
        self.state.offset_x = 0.3 * math.sin(self.cycle)
        self.state.isometric = 1
        self.state.zoom = 0.7 + 0.2 * math.sin(self.cycle * 2)

# ------------------------------------------------------------------------------------------------ #

@define
class DepthManager:
    estimator: DepthEstimator = Factory(DepthAnythingV2)
    """A **shared** estimator for all threads"""

    upscaler: BrokenUpscaler = Factory(NoUpscaler)
    """The upscaler to use for all threads"""

    threads: List[Thread] = Factory(list)
    """List of running threads"""

    concurrency: int = int(os.getenv("WORKERS", 1))
    """Maximum concurrent render workers (high memory usage)"""

    outputs: List[Path] = Factory(list)
    """List of all rendered videos on this session"""

    def __attrs_post_init__(self):
        self.estimator.load_torch()
        self.estimator.load_model()
        self.upscaler.load_model()

    # # Allow for using with statements

    def __enter__(self) -> Self:
        self.outputs = list()
        return self

    def __exit__(self, *ignore) -> None:
        self.join()

    # # User methods

    def parallax(self, scene: Type[DepthScene], image: Path) -> None:

        # Limit the maximum concurrent threads, nice pattern 😉
        while len(self.threads) >= self.concurrency:
            self.threads = list(filter(lambda x: x.is_alive(), self.threads))
            time.sleep(0.05)

        # Create and add a new running worker, daemon so it dies with the main thread
        thread = Thread(target=self._worker, args=(scene, image), daemon=True)
        self.threads.append(thread)
        thread.start()

    # @abstractmethod
    # def filename(self, data: DotMap) -> Path:
    #     """Find the output path (Default: same path as image, 'Render' folder)"""
    #     return (data.image.parent / "Render") / ("_".join((
    #         data.image.stem,
    #         f"v{data.variation or 0}",
    #         f"{data.render.time}s",
    #         f"{data.render.height}p{data.render.fps or ''}",
    #     )) + ".mp4")
    @abstractmethod
    def filename(self, data: DotMap) -> Path:
        """Find the output path (Default: same path as image, 'Render' folder)"""
        return (data.image.parent ) / (data.image.stem + "_df.mp4")

    @abstractmethod
    def animate(self, data: DotMap) -> None:
        """Add preset system's animations to each export"""
        data.scene.add_animation(DepthState(
            vignette_enable=True,
            dof_enable=True,
        ))

        # List of possible animations
        animations = [
            ("Circle", Presets.Circle(intensity=round(random.uniform(0.6, 0.8), 2), loop=True, reverse=random.choice([True, False]))),
            ("Orbital", Presets.Orbital(intensity=round(random.uniform(0.6, 0.8), 2) , loop=True, reverse=random.choice([True, False]))),
            ("Dolly", Presets.Dolly(intensity=round(random.uniform(0.5, 0.7), 2), loop=True, reverse=random.choice([True, False]))),
            ("Horizontal", Presets.Horizontal(intensity=round(random.uniform(0.5, 0.7), 2), loop=True, reverse=random.choice([True, False]))),
        ]

        isometric_value = round(random.uniform(0.4, 0.5), 2)
        height_value = round(random.uniform(0.1, 0.15), 2)
        zoom_value = round(random.uniform(0.65, 0.75), 2)

        data.scene.add_animation(Components.Set(target=Target.Isometric, value=isometric_value))
        print(f"Isometric: {isometric_value}")

        data.scene.add_animation(Components.Set(target=Target.Height, value=height_value))
        print(f"Height: {height_value}")

        data.scene.add_animation(Presets.Zoom(intensity=zoom_value, loop=True))
        print(f"Zoom: {zoom_value}")

        applied = set()
        for _ in range(random.randint(2, 3)):  # Randomly choose 2 to 3 animations
            name, animation = random.choice([x for x in animations if x[0] not in applied])
            applied.add(name)
            data.scene.add_animation(animation)
            print(f"Applied Animation: {name}: {animation}")
            # log text file with filenames and applied animation parameters in datetime_folder  
            with open(f"{datetime_folder}/_depth_log.txt", "a") as f:
                f.write(f"{data.image.stem}\n{name}\n{animation}\n Isometric: {isometric_value}\n Height: {height_value}\n Zoom: {zoom_value}\n\n")


    @abstractmethod
    def variants(self, image: Path) -> DotMap:
        return DotMap(
            render=combinations(
                height=(1920),
                time=(6),
                fps=(25),
            )
        )

    # # Internal methods

    def _worker(self, scene: Type[DepthScene], image: Path):
        # Note: Share an estimator between threads to avoid memory leaks
        scene = scene(backend="headless")
        scene.estimator = self.estimator
        scene.set_upscaler(self.upscaler)
        scene.input(image=image)

        # Note: We reutilize the Scene to avoid re-creation!
        # Render multiple lengths, or framerates, anything
        for data in combinations(**self.variants(image)):
            data.update(scene=scene, image=image)

            # Find or set common parameters
            output = self.filename(data)
            scene.clear_animations()
            self.animate(data)

            # Make sure the output folder exists
            output.parent.mkdir(parents=True, exist_ok=True)

            video = scene.main(output=output, **data.render)
            if video:  # Check if video was created successfully
                self.outputs.append(video[0])

        # Imporant: Free up OpenGL resources
        scene.window.destroy()

    def join(self):
        for thread in self.threads:
            thread.join()

class YourManager(DepthManager):
    def variants(self, image: Path) -> DotMap:
        return DotMap(
            variation=[0],
            render=combinations(
                height=[1920],
                time=[6],
                loop=[1],
                fps=[25],
            )
        )

if (__name__ == "__main__"):
    # images = Path(os.getenv("IMAGES", "/Users/a/Desktop/Share/YT/Scripts/VideoCutter/INPUT/DEPTH"))
    images = Path(os.getenv("IMAGES", datetime_folder))

    # Multiple unique videos per file
    # Note: Use Upscayl() for some upscaler!
    # with DepthManager(upscaler=NoUpscaler()) as manager:
    # with YourManager(upscaler=Upscayl()) as manager:


    with YourManager(upscaler=NoUpscaler()) as manager:
        for image in images.glob("*"):
            if image.suffix in ['.jpg', '.jpeg', '.png']:  # Only process image files
                manager.parallax(DepthScene, image)

        for output in manager.outputs:
            print(f"• {output}")

