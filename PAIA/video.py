import datetime
import glob
import json
import math
import os
import sys
import subprocess

import cv2
import ffmpeg
from PIL import Image, ImageDraw, ImageFont
import ffmpeg_streaming
from ffmpeg_streaming import Formats

from config import ENV, bool_ENV, int_ENV

def insert_player_id(id: str, input_path, output_path, info_time: int=None):
    if info_time is None:
        info_time = int_ENV('RECORDING_INFO_SECONDS', 3)
    
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))
    
    in1 = ffmpeg.input(input_path)
    v1 = in1.video.drawtext(
        text='Player',
        fontsize='round(sqrt(w*h/50))',
        x='(w-tw)/2',
        y='((h-text_h)/2)-(text_h-(th/4))',
        fontfile='assets/fonts/NotoSansTC-Bold.otf',
        fontcolor='white',
        borderw=4,
        enable=f'between(t,0,{info_time})'
    ).drawtext(
        text=id,
        fontsize='round(sqrt(w*h/50))',
        x='(w-tw)/2',
        y='((h-text_h)/2)+(text_h-(th/4))',
        fontfile='assets/fonts/NotoSansTC-Bold.otf',
        fontcolor='white',
        borderw=4,
        enable=f'between(t,0,{info_time})'
    )
    a1 = in1.audio
    out = ffmpeg.output(v1, a1, output_path)
    out.run(overwrite_output=True)

def background_image(width=1920, height=1080):
    image = Image.new('RGB', (width, height)) # Create the image

    innerColor = [64, 64, 64] # Color at the center
    outerColor = [32, 32, 32] # Color at the corners


    for y in range(height):
        for x in range(width):
            # Find the distance to the center
            distanceToCenter = math.sqrt((x - width / 2) ** 2 + (y - height / 2) ** 2)
            # Make it on a scale from 0 to 1
            distanceToCenter = float(distanceToCenter) / (math.sqrt(2) * width / 2)
            # Calculate r, g, and b values
            r = outerColor[0] * distanceToCenter + innerColor[0] * (1 - distanceToCenter)
            g = outerColor[1] * distanceToCenter + innerColor[1] * (1 - distanceToCenter)
            b = outerColor[2] * distanceToCenter + innerColor[2] * (1 - distanceToCenter)
            # Place the pixel        
            image.putpixel((x, y), (int(r), int(g), int(b)))
    
    return image

def result_image(width, height, id, usedtime, progress, video_dir, duration=10):
    if width < 0:
        width = 1920
    if height < 0:
        height = 1080
    
    image = background_image(width, height)

    fontsize = int(math.sqrt(width * height / 100))
    font = ImageFont.truetype('assets/fonts/NotoSansTC-Bold.otf', fontsize)
    draw = ImageDraw.Draw(image)

    usedtime = '' if usedtime == -1  else round(usedtime, 2)
    progress = '' if progress == -1  else int(round(progress * 100, 0))

    id_w, th = draw.textsize(id, font)
    time_w, _ = draw.textsize(f'Used Time: {usedtime} (s)', font)
    pg_w, _ = draw.textsize(f'Progress: {progress} %', font)

    draw.text(((width - id_w) / 2, (height - 1.5 * th) / 2 - 1.5 * th + th / 4), id, '#FFFFFF', font)
    draw.text(((width - time_w) / 2, (height - 1.5 * th) / 2), f'Used Time: {usedtime} (s)', '#FFFFFF', font)
    draw.text(((width - pg_w) / 2, (height - 1.5 * th) / 2 + 1.5 * th - th / 4), f'Progress: {progress} %', '#FFFFFF', font)

    image.save(os.path.join(video_dir, 'result.jpg'))

    with open(os.path.join(video_dir, 'img.txt'), 'r', encoding="utf-8") as fin:
        lines = fin.read().splitlines()
        last_index = 0
        while -last_index < len(lines):
            last_index -= 1
            last_line = lines[last_index]
            if last_line.startswith("file 'img_"):
                break
        with open(os.path.join(video_dir, 'img.txt'), 'w') as fout:
            for i in range(len(lines) + last_index + 1):
                fout.write(lines[i] + '\n')
            fout.write(f"duration 0\nfile 'result.jpg'\nduration {duration}\n")
            fout.write(f"file 'result.jpg'\nduration 0\n")

    return image

def generate_video(video_dir, output_path, id: str, usedtime: float, progress: float, username: str=None, result_duration: int=None, width: int=None, height: int=None, save_rec=None, remove_original: bool=True):
    if username is None:
        username = ENV.get('PAIA_USERNAME', '')
    if result_duration is None:
        result_duration = int_ENV('RECORDING_RESULT_SECONDS', 10)
    if save_rec is None:
        save_rec = bool_ENV('RECORDING_SAVE_REC', False)
    
    try:
        with open(os.path.join(video_dir, 'size.txt'), 'r', encoding="utf-8") as fin:
            sizes = fin.read().split('x')
            width = width or int(sizes[0])
            height = height or int(sizes[1])
    except:
        width = width or -1
        height = height or -1

    result_image(width, height, id, usedtime, progress, video_dir, result_duration)

    try:
        result = subprocess.run([
            'ffmpeg',
            '-y',
            '-f', 'concat',
            '-i', 'img.txt',
            '-i', 'audio.wav',
            '-pix_fmt', 'yuv420p',
            '-vf', f'scale={width}:{height},setsar=1:1',
            'tmp.mp4'
        ], check=True, cwd=video_dir)
    except:
        result = -1
    
    insert_player_id(id, os.path.join(video_dir, 'tmp.mp4'), output_path)
    os.remove(os.path.join(video_dir, 'tmp.mp4'))

    if remove_original:
        if os.path.abspath(os.path.dirname(output_path)) == os.path.abspath(video_dir):
            path_all = glob.glob(f'{os.path.abspath(video_dir)}/**/*', recursive=True)
            path_remove=[filename for filename in path_all if not filename == output_path]
            [os.remove(filePath) for filePath in path_remove]
        else:
            for root, dirs, files in os.walk(os.path.abspath(video_dir), topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(os.path.abspath(video_dir))
    
    if save_rec:
        rec_path = os.path.join(os.path.dirname(output_path), os.path.splitext(os.path.basename(output_path))[0] + '.json')
        with open(rec_path, 'w') as fout:
            obj = {
                'id': id,
                'usedtime': usedtime,
                'progress': progress,
                'username': username
            }
            fout.write(json.dumps(obj, indent=4))

    return result

def rank_image(ids, width=1920, height=1080):
    if width < 0:
        width = 1920
    if height < 0:
        height = 1080
    
    image = background_image(width, height)

    fontsize = int(math.sqrt(width * height / 100))
    font = ImageFont.truetype('assets/fonts/NotoSansTC-Bold.otf', fontsize)
    draw = ImageDraw.Draw(image)

    ranks = ['1st', '2nd', '3rd', '4th']

    th = draw.textsize('Test', font)[1] if len(ids) > 0 else 0
    tw = [draw.textsize(f'{ranks[i]}: {ids[i]}', font)[0] for i in range(len(ids))]
    pos = [((width - tw[i]) / 2, (height / (len(ids) + 1) / 2) * (2 * i + 2) - th / 1.5) for i in range(len(ids))]

    for i in range(len(ids)):
        draw.text(pos[i], f'{ranks[i]}: {ids[i]}', '#FFFFFF', font)

    return image

def video_duration(filepath):
    result = subprocess.run(
        f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{filepath}"',
        capture_output=True, shell=True
    ).stdout.decode()

    fields = json.loads(result)['streams'][0]

    return float(fields['duration'])

def rank_video(players, output_path, preserve_time: int=None, result_time: int=None, rank_time: int=None, width: int=None, height: int=None):
    # players: [{'rank', 'video_path'}]

    if preserve_time is None:
        preserve_time = int_ENV('VIDEO_PRESERVE_SECONDS', 75)
    if result_time is None:
        result_time = int_ENV('RECORDING_RESULT_SECONDS', 10)
    if rank_time is None:
        rank_time = int_ENV('VIDEO_RANK_SECONDS', 5)
    if width is None:
        width = int_ENV('VIDEO_WIDTH', 1920)
    if height is None:
        height = int_ENV('VIDEO_HEIGHT', 1080)

    durations = [video_duration(player['video_path']) for player in players]
    duration = max(durations)
    trim_time = duration - (preserve_time - result_time)
    total_time = trim_time + rank_time

    w = []
    h = []
    pos = []
    if len(players) == 1:
        # Player 0
        w.append(width)
        h.append(height)
        pos.append((0, 0))
    if len(players) == 2:
        # Player 0
        w.append(width / 2)
        h.append(height / 2)
        pos.append((0, height / 4))
        # Player 1
        w.append(width / 2)
        h.append(height / 2)
        pos.append((width / 2, height / 4))
    if len(players) == 3:
        # Player 0
        w.append(width / 2)
        h.append(height / 2)
        pos.append((width / 4, 0))
        # Player 1
        w.append(width / 2)
        h.append(height / 2)
        pos.append((0, height / 2))
        # Player 2
        w.append(width / 2)
        h.append(height / 2)
        pos.append((width / 2, height / 2))
    if len(players) == 4:
        # Player 0
        w.append(width / 2)
        h.append(height / 2)
        pos.append((0, 0))
        # Player 1
        w.append(width / 2)
        h.append(height / 2)
        pos.append((width / 2, 0))
        # Player 2
        w.append(width / 2)
        h.append(height / 2)
        pos.append((0, height / 2))
        # Player 3
        w.append(width / 2)
        h.append(height / 2)
        pos.append((width / 2, height / 2))

    image = Image.new('RGB', (width, height)) # Create the image (with background black)
    image.save('tmp_bg.jpg')
    ranked_player = [p['id'] for p in sorted(players, key=lambda p:p['rank'])]
    rank_img = rank_image(ranked_player, width, height)
    rank_img.save('tmp_rank.jpg')

    bg = ffmpeg.input('tmp_bg.jpg')
    bgm = ffmpeg.input('assets/audio/BGM.mp3').filter('atrim', end=total_time).filter('volume', 0.5)
    v = bg
    a = []
    for i in range(len(players)):
        input = ffmpeg.input(players[i]['video_path'])
        video = input.video.trim(end=total_time).filter('scale', size=f'{int(w[i])}x{int(h[i])}', force_original_aspect_ratio='increase')
        v = v.overlay(video, x=pos[i][0], y=pos[i][1])
        a.append(input.audio)
    vr = ffmpeg.input('tmp_rank.jpg')
    v = v.overlay(vr, enable=f'between(t,{trim_time},{total_time})')
    a = ffmpeg.filter(a, 'amix', inputs=len(a)).filter('atrim', end=total_time).filter('volume', 2)
    a = ffmpeg.filter((bgm, a), 'amix', inputs=2)
    out = ffmpeg.output(v, a, output_path, pix_fmt='yuv420p')
    out.run(overwrite_output=True)

    os.remove('tmp_bg.jpg')
    os.remove('tmp_rank.jpg')
    
    return rank_img

def poster(video_basepath):
    # Show the thumbnail of the video
    vc = cv2.VideoCapture(video_basepath + '.mp4')

    if vc.isOpened():
        _, frame = vc.read()
        cv2.imwrite(video_basepath + '.jpg', frame)
    vc.release()

def monitor(ffmpeg, duration, time_, time_left, process):
    per = round(time_ / duration * 100)
    sys.stdout.write(
        "\rTranscoding...(%s%%) %s left [%s%s]" %
        (per, datetime.timedelta(seconds=int(time_left)), '#' * per, '-' * (100 - per))
    )
    sys.stdout.flush()

def live(video_basepath):
    video = ffmpeg_streaming.input(video_basepath + '.mp4')
    hls = video.hls(Formats.h264())
    hls.auto_generate_representations()
    output_path = video_basepath + '.m3u8'
    hls.output(output_path, monitor=monitor, async_run=False)


if __name__ == '__main__':
    # Example input
    video_dir = 'Records'
    output_path = os.path.abspath('records/kart.mp4')
    # generate_video(video_dir, output_path, 'Alice', 31.28, 0.999, 75, remove_original=True)
    # generate_video(video_dir, output_path, 'Alice', 31.28, 0.999)

    # rank_video([
    #     {'rank': 4, 'id': 'Debby', 'video_path': 'video/result_4.mp4'},
    #     {'rank': 2, 'id': 'Alice', 'video_path': 'video/result_1.mp4'},
    #     {'rank': 3, 'id': 'Bob', 'video_path': 'video/result_2.mp4'},
    #     {'rank': 1, 'id': 'Chris', 'video_path': 'video/result_3.mp4'}
    # ], 'output.mp4', 75, 10, 5, 1920, 1080)

    rank_video([
        {'rank': 4, 'id': 'Debby', 'video_path': 'video/result_4.mp4'},
        {'rank': 2, 'id': 'Alice', 'video_path': 'video/result_1.mp4'},
        {'rank': 3, 'id': 'Bob', 'video_path': 'video/result_2.mp4'},
        {'rank': 1, 'id': 'Chris', 'video_path': 'video/result_3.mp4'}
    ], 'output.mp4')