# -*- coding: UTF-8 -*-
import webrtcvad
import collections
import sys
import signal
import pyaudio
from array import array
from struct import pack
import wave
import time
# import os
 
 
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK_DURATION_MS = 30       # supports 10, 20 and 30 (ms)
PADDING_DURATION_MS = 1500   # 1 sec jugement
CHUNK_SIZE = int(RATE * CHUNK_DURATION_MS / 1000)  # chunk to read
CHUNK_BYTES = CHUNK_SIZE * 2  # 16bit = 2 bytes, PCM
NUM_PADDING_CHUNKS = int(PADDING_DURATION_MS / CHUNK_DURATION_MS)
NUM_WINDOW_CHUNKS = int(240 / CHUNK_DURATION_MS)
# NUM_WINDOW_CHUNKS = int(400 / CHUNK_DURATION_MS)  # 400 ms/ 30ms  ge
NUM_WINDOW_CHUNKS_END = NUM_WINDOW_CHUNKS * 2
 
def handle_int(sig, chunk):
    global leave, got_a_sentence
    leave = True
    got_a_sentence = True
 
 
def record_to_file(path, data, sample_width):
    '''
        录音并写入文件
        Args:
            path(str):音频最终保存路径
            data:表示音频的二进制字符串
            sample_width:指定样例宽度
    '''
    # sample_width, data = record()
    data = pack('<' + ('h' * len(data)), *data)
    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()
 
 
def normalize(snd_data):
    "Average the volume out"
    MAXIMUM = 32767  # 16384
    times = float(MAXIMUM) / max(abs(i) for i in snd_data)
    r = array('h')
    for i in snd_data:
        r.append(int(i * times))
    return r
 
signal.signal(signal.SIGINT, handle_int)
 
 
def record_sound(file_path='oppo.pcm'):
    '''
        录音函数,调用record_to_file
        Args:
            file_path(str):音频最终保存路径
    '''
    # 录音，有声音自动写入文件，默认为'test.wav'，声音结束后录音也停止，调用一次，录制一个片段
    vad = webrtcvad.Vad(3) # 这个参数可为1，2，3，可改变灵敏度，越大越粗犷
    pa = pyaudio.PyAudio()
    stream = pa.open(format=FORMAT,
                     channels=CHANNELS,
                     rate=RATE,
                     input=True,
                     start=False,
                     # input_device_index=2,
                     frames_per_buffer=CHUNK_SIZE)
 
    got_a_sentence = False
    leave = False
#     no_time = 0
 
    while not leave:
        ring_buffer = collections.deque(maxlen=NUM_PADDING_CHUNKS)
        triggered = False
#         voiced_frames = []
        ring_buffer_flags = [0] * NUM_WINDOW_CHUNKS
        ring_buffer_index = 0
 
        ring_buffer_flags_end = [0] * NUM_WINDOW_CHUNKS_END
        ring_buffer_index_end = 0
#         buffer_in = ''
        raw_data = array('h')
        index = 0
        start_point = 0
        StartTime = time.time()
        print("* recording: ")
        stream.start_stream()
 
        while not got_a_sentence and not leave:
            chunk = stream.read(CHUNK_SIZE)
            # add WangS
            raw_data.extend(array('h', chunk))
            index += CHUNK_SIZE
            TimeUse = time.time() - StartTime
 
            active = vad.is_speech(chunk, RATE)
 
            sys.stdout.write('1' if active else '_')
            ring_buffer_flags[ring_buffer_index] = 1 if active else 0
            ring_buffer_index += 1
            ring_buffer_index %= NUM_WINDOW_CHUNKS
 
            ring_buffer_flags_end[ring_buffer_index_end] = 1 if active else 0
            ring_buffer_index_end += 1
            ring_buffer_index_end %= NUM_WINDOW_CHUNKS_END
 
            # start point detection
            if not triggered:
                ring_buffer.append(chunk)
                num_voiced = sum(ring_buffer_flags)
                if num_voiced > 0.8 * NUM_WINDOW_CHUNKS:
                    sys.stdout.write(' Open ')
                    triggered = True
                    start_point = index - CHUNK_SIZE * 20  # start point
                    # voiced_frames.extend(ring_buffer)
                    ring_buffer.clear()
            # end point detection
            else:
                # voiced_frames.append(chunk)
                ring_buffer.append(chunk)
                num_unvoiced = NUM_WINDOW_CHUNKS_END - sum(ring_buffer_flags_end)
                if num_unvoiced > 0.90 * NUM_WINDOW_CHUNKS_END or TimeUse > 10:
                    sys.stdout.write(' Close ')
                    triggered = False
                    got_a_sentence = True
 
            sys.stdout.flush()
 
        sys.stdout.write('\n')
        # data = b''.join(voiced_frames)
 
        stream.stop_stream()
        print("* done recording")
        got_a_sentence = False
 
        # write to file
        raw_data.reverse()
        for index in range(start_point):
            raw_data.pop()
        raw_data.reverse()
        raw_data = normalize(raw_data)
        record_to_file(file_path, raw_data, 2)
        leave = True
 
    stream.close()
 
    return True
 
CHUNK = 512  # 512是树莓派能使用的最大的CHUNK

def play_sound(file_path='oppo.pcm'):
    '''
        播放声音文件，默认为'oppo.pcm'
    '''
    wf = wave.open(file_path, 'rb')
    p = pyaudio.PyAudio()
 
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
 
    data = wf.readframes(CHUNK)
 
    while data != b'':
        stream.write(data)
        data = wf.readframes(CHUNK)
    stream.stop_stream()
    stream.close()
    p.terminate()
    return
 
# 测试
if __name__ == '__main__':
    record_sound('oppo.pcm')
    play_sound('oppo.pcm')
