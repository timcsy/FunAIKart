# Configuration settings for the SSH Server
PAIA_ID=
PAIA_HOST=
PAIA_PORT=
PAIA_USERNAME=
PAIA_PASSWORD=


# About Game playing
# PLAY_PICKUPS: false for no pickups, true or int for using pickups, int for same pickups set
PLAY_PICKUPS=true
# PLAYER_ID: The ID to show in the game result
PLAYER_ID="kart"
PLAY_BASE_DIR="ml"
PLAY_SCRIPT="${PLAY_BASE_DIR}/ml_play.py"
PLAY_AUTOSAVE=true
# Play the game for MAX_EPISODES rounds, use negative value for unlimit rounds
MAX_EPISODES=1



# Recording: Record the video of the game
RECORDING_ENABLE=false
RECORDING_BASE_DIR="records"
# Set false if you want to store in the base directory
RECORDING_USE_DIR=true
RECORDING_DIR_PREFIX=${PLAYER_ID}
# Set false to disable, or using Python-style strftime format
RECORDING_DIR_TIMESTAMP=%Y%m%d_%H%M%S
RECORDING_FILE_PREFIX=${PLAYER_ID}
RECORDING_FILE_TIMESTAMP=false
RECORDING_SAVE_REC=false
RECORDING_RESULT_SECONDS=75
RECORDING_PERIOD=1


# Video: Video of the game competition
VIDEO_WIDTH=1920
VIDEO_HEIGHT=1080
VIDEO_RANK_SECONDS=5
VIDEO_PRESERVE_SECONDS=75