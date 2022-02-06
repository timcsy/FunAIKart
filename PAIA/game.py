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
PLAY_CONTINUE=false
PLAY_AUTOSAVE_DIR="autosave"
PLAY_AUTOSAVE_PREFIX="ml_play"
PLAY_AUTOSAVE_USE_NEWEST=true
PLAY_AUTOSAVE_PATH=""
# Play the game for MAX_EPISODES rounds, use negative value for unlimit rounds
MAX_EPISODES=-1


# LOG_LEVEL: The depth you want to log information using logging module
# Uncomment the following for your case (Recommand using INFO or DEBUG):
#LOG_LEVEL=CRITICAL
#LOG_LEVEL=ERROR
#LOG_LEVEL=WARNING
LOG_LEVEL=INFO
#LOG_LEVEL=DEBUG
#LOG_LEVEL=NOTSET


# Demo: Record demonstration files (.paia), which can use by imitation learning
DEMO_ENABLE=false
DEMO_BASE_DIR="demo"
# Set false if you want to store in the base directory
DEMO_USE_DIR=false
DEMO_DIR_PREFIX=${PLAYER_ID}
# Set false to disable, or using Python-style strftime format
DEMO_DIR_TIMESTAMP=%Y%m%d_%H%M%S
DEMO_FILE_PREFIX=${PLAYER_ID}
# Set false to disable, or using Python-style strftime format
DEMO_FILE_TIMESTAMP=false
DEMO_PERIOD=1
# DEMO_EXPRESSION is available when the DEMO_PERIOD is 0, using lambda expression
# Returns boolean value
DEMO_EXPRESSION="lambda n: n % 10 == 0"
DEMO_ALL_IN_ONE=true


# Image: The directory to store the images when using PAIA.state_info() function
IMAGE_ENABLE=false
IMAGE_BASE_DIR="cameras"
# Set false if you want to store in the base directory
IMAGE_USE_DIR=true
IMAGE_DIR_PREFIX=${PLAYER_ID}
# Set false to disable, or using Python-style strftime format
IMAGE_DIR_TIMESTAMP=%Y%m%d_%H%M%S
IMAGE_FILE_PREFIX="img"
# Set false to disable, or using Python-style strftime format
IMAGE_FILE_TIMESTAMP=false


# Unity Application
UNITY_USE_EDITOR=false
# UNITY_APP_AUTO: Choose the OS automatically, if is false, then use UNITY_APP_OTHER (with UNITY_APP_BASE_DIR)
UNITY_APP_AUTO=true
UNITY_APP_BASE_DIR="kart"
UNITY_APP_WINDOWS="Windows/kart.exe"
UNITY_APP_LINUX="Linux/kart.x86_64"
UNITY_APP_MACOS="macOS/kart.app"
UNITY_APP_OTHER=""
UNITY_CONFIG_BASE_DIR="kart"
UNITY_CONFIG_COMPANY="PAIA"
UNITY_CONFIG_PRODUCT="kart"


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
RECORDING_WIDTH=960
RECORDING_HEIGHT=540
RECORDING_INFO_SECONDS=3
RECORDING_RESULT_SECONDS=10
RECORDING_PERIOD=1
# RECORDING_EXPRESSION is available when the RECORDING_PERIOD is 0, using lambda expression
# Returns boolean value
RECORDING_EXPRESSION="lambda n: n % 10 == 0"


# Video: Video of the game competition
VIDEO_WIDTH=1920
VIDEO_HEIGHT=1080
VIDEO_RANK_SECONDS=5
VIDEO_PRESERVE_SECONDS=75