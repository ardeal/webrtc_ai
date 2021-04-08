# WebRTC for AI

This example illustrates how to enconde images processed by GPU and send video steam to browser. This solution is to take place of traditional C/S mode.


# Motivation

see the following picture.
* solution 1: is the traditonal solution which is used when AI algorithms could be run on GPU. in this case, both client GUi and algorithms are both run on CPU.
* solution 2: is the latest requirement. the latest algorithms based on deep learning could only be run one GPU. however, not all computer has GPU. so solution 1 is not appropriate for the latest requirement.
* solution 3: C++ client GUI is running on CPU computer, but the algorithms is running on remote GPU computer. This sotion is good, but less better than solution 4.
* solution 4: B/S mode. algorithm is running on remote GPU server. there is no client GUI at all. it is convenient and generic. This solution fits the latest usecase. 


# How to run
1) install packages:
<pre>
pip install aiortc
pip install pyav
pip install opencv-python
pip install aiohttp 
pip install websockets
</pre>

2) run the file: webcam.py
3) on browser: http://127.0.0.1:8080， click on start button


# Explanation of the code
Pay attion on the code in webcamp.py file.
1) Code from line 35 to 73 in webcam.py file defines the stream class which prepare video stream that will be send to browser.
2) If you would like to send your own images to browser, comment out code between line 48 to 49 and 65 to 67, and uncomment the code between line 51 to 53 and 58 to 61. in addition, you should replace line 51 with your own image folder.
3) understand the code between line 161 to 168.

# Enjoy the best solution for AI GUI.

