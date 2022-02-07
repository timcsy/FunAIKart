from datetime import datetime
import logging
import sys
from mlagents_envs import env_utils

from config import ENV, bool_ENV, int_ENV
import demo
import unity
import video

def manual():
    MAX_EPISODES = int_ENV('MAX_EPISODES', -1)
    unity_app = unity.get_unity_app()
    logging.info("Check this file if the game doesn't open:")
    logging.info(unity_app)

    episode = 0
    tmp_dir = None
    recording_dir = None
    output_video_path = None
    id = ''
    usedtime = 0
    progress = 0
    has_demo = False
    demo_purename = datetime.now().strftime("%Y%m%d%H%M%S")

    while MAX_EPISODES < 0 or episode < MAX_EPISODES:
        # Preparation
        if recording_dir is None:
            tmp_dir, recording_dir, output_video_path = unity.prepare_recording(episode=episode)
        else:
            tmp_dir, _, output_video_path = unity.prepare_recording(episode=episode, recording_dir=recording_dir)
        
        demo_name = unity.prepare_demo(episode=episode, purename=demo_purename)
        if not demo_name is None:
            has_demo = True
        pickups = int_ENV('PLAY_PICKUPS', 0)
        if pickups is None:
            pickups = bool_ENV('PLAY_PICKUPS', True)
        unity.set_config('PickUps', pickups)

        # Main part: Excecute the App
        if not unity_app is None:
            env_utils.launch_executable(unity_app, args=[]).wait()
        else:
            input('Press any key to continue after stop the Unity game ...')
        episode += 1
        print(f'Episode {episode} finished')

        # Post-processing
        id = ENV.get('PLAYER_ID', '')
        usedtime, progress = demo.get_info(demo_name)
        if not tmp_dir is None and not output_video_path is None:
            video.generate_video(
                video_dir=tmp_dir,
                output_path=output_video_path,
                id=id,
                usedtime=usedtime,
                progress=progress
            )

        # If MAX_EPISODES is unlimited, ask if want to stop
        if MAX_EPISODES < 0:
            is_continue = input('Continue? (y/n): ')
            if is_continue.lower() != 'y':
                break
    
    # Finish all
    if has_demo:
        demo.demo_to_paia(purename=demo_purename)
    unity.set_config('Records', False)
    unity.set_config('Screen', False)
    unity.set_config('Demo', False)
    unity.set_config('PickUps', False)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1].isnumeric():
            ENV['MAX_EPISODES'] = sys.argv[1]
            if len(sys.argv) > 2 and sys.argv[2] == '--pickups' or sys.argv[2] == '-P':
                ENV['PLAY_PICKUPS'] = sys.argv[3] if len(sys.argv) > 3 else 'true'
        elif sys.argv[1] == '--pickups' or sys.argv[1] == '-P':
            ENV['PLAY_PICKUPS'] = sys.argv[2] if len(sys.argv) > 2 else 'true'
    manual()