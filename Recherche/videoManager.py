import scenedetect
from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.stats_manager import StatsManager
from scenedetect.detectors import ContentDetector


def get_scenes(video_path):
    global scene_list
    video_manager = VideoManager([video_path])
    stats_manager = StatsManager()
    scene_manager = SceneManager(stats_manager)

    # Add ContentDetector algorithm (constructor takes detector options like threshold).
    scene_manager.add_detector(ContentDetector(threshold=40.0, min_scene_len=30))
    base_timecode = video_manager.get_base_timecode()

    try:
        # If stats file exists, load it.
        # if os.path.exists(STATS_FILE_PATH):
        # Read stats from CSV file opened in read mode:
        # with open(STATS_FILE_PATH, 'r') as stats_file:
        # stats_manager.load_from_csv(stats_file, base_timecode)

        start_time = base_timecode + 0  # 00:00:00.667
        video_manager.set_duration(start_time=start_time)

        # Set downscale factor to improve processing speed.
        video_manager.set_downscale_factor()

        # Start video_manager.
        video_manager.start()

        # Perform scene detection on video_manager.
        scene_manager.detect_scenes(frame_source=video_manager)

        # Obtain list of detected scenes.
        scene_list = scene_manager.get_scene_list(base_timecode)

    finally:
        video_manager.release()
        return scene_list