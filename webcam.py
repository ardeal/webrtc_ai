import argparse
import asyncio
import json
import logging
import os
import platform
import ssl

import numpy

from aiohttp import web

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay

ROOT = os.path.dirname(__file__)
from aiortc import (
    RTCIceCandidate,
    RTCPeerConnection,
    RTCSessionDescription,
    VideoStreamTrack,
    MediaStreamTrack
)

import av._core
from av import VideoFrame
from av.video import VideoFrame
import av

import cv2
PHOTO_PATH = os.path.join(ROOT, "photo.jpg")

import time

class VideoImageTrack(VideoStreamTrack):
    """
    A video stream track that returns a rotating image.
    """
    kind = "video"
    def __init__(self):
        super().__init__()  # don't forget this!

        self.kind = 'video'
        # self._player = player
        self._queue = asyncio.Queue()
        self._start = None

        self.img = cv2.imread(PHOTO_PATH, cv2.IMREAD_COLOR)

        self.frame = VideoFrame.from_ndarray(self.img, format="bgr24")
        self.image_rootdir = r'D:\datasets\coco\images\train2014'
        self.image_list = os.listdir(self.image_rootdir)
        self.counter = 0

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        # time.sleep(0.01)
        image = cv2.imread(os.path.join(self.image_rootdir, self.image_list[self.counter]))
        self.counter +=1
        if self.counter >= len(self.image_list): self.counter = 0
        # self.img = image
        self.img = cv2.resize(image, (960, 540))

        img = self.img
        # rotate image
        rows, cols, _ = self.img.shape
        # M = cv2.getRotationMatrix2D((cols / 2, rows / 2), int(pts * time_base * 45), 1)
        # img = cv2.warpAffine(self.img, M, (cols, rows))

        # create video frame
        frame = VideoFrame.from_ndarray(img, format="bgr24")
        frame.pts = pts
        frame.time_base = time_base

        return frame

def create_local_tracks(play_from):
    global relay, webcam

    if play_from:
        player = MediaPlayer(play_from)
        return player.audio, player.video
    else:
        options = {"framerate": "30", "video_size": "640x480"}
        if relay is None:
            if platform.system() == "Darwin":
                webcam = MediaPlayer(
                    "default:none", format="avfoundation", options=options
                )
            elif platform.system() == "Windows":
                webcam = MediaPlayer(
                    "video=Integrated Camera", format="dshow", options=options
                )
            else:
                webcam = MediaPlayer("/dev/video0", format="v4l2", options=options)
            relay = MediaRelay()
        return None, relay.subscribe(webcam.video)

import numpy as np

def generate_video():
    duration = 10
    fps = 24
    total_frames = duration * fps

    # container = av.open('test.mp4', mode='w')
    container = av.open(r'd:/test.mp4', mode='w')

    stream = container.add_stream('mpeg4', rate=fps)
    stream.width = 480
    stream.height = 320
    stream.pix_fmt = 'yuv420p'

    for frame_i in range(total_frames):

        img = np.empty((480, 320, 3))
        img[:, :, 0] = 0.5 + 0.5 * np.sin(2 * np.pi * (0 / 3 + frame_i / total_frames))
        img[:, :, 1] = 0.5 + 0.5 * np.sin(2 * np.pi * (1 / 3 + frame_i / total_frames))
        img[:, :, 2] = 0.5 + 0.5 * np.sin(2 * np.pi * (2 / 3 + frame_i / total_frames))

        img = np.round(255 * img).astype(np.uint8)
        img = np.clip(img, 0, 255)

        frame = av.VideoFrame.from_ndarray(img, format='rgb24')
        for packet in stream.encode(frame):
            container.mux(packet)

    # Flush stream
    for packet in stream.encode():
        container.mux(packet)
    return container

async def index(request):
    content = open(os.path.join(ROOT, "index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)


async def javascript(request):
    content = open(os.path.join(ROOT, "client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)


async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    # open media source
    audio, video = create_local_tracks(args.play_from)

    # videoc = generate_video()

    await pc.setRemoteDescription(offer)
    for t in pc.getTransceivers():
        # if t.kind == "audio" and audio:
        #     pc.addTrack(audio)
        # elif t.kind == "video" and video:
        #     pc.addTrack(video)

        if t.kind == 'video':
            pc.addTrack(VideoImageTrack())

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


pcs = set()


async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebRTC webcam demo")
    parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument("--play-from", default=r'D:\video_20210121_161410.mp4',help="Read the media from a file and sent it."),
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host for HTTP server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for HTTP server (default: 8080)"
    )
    parser.add_argument("--verbose", "-v", action="count")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.cert_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(args.cert_file, args.key_file)
    else:
        ssl_context = None

    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    app.router.add_post("/offer", offer)
    web.run_app(app, host=args.host, port=args.port, ssl_context=ssl_context)
