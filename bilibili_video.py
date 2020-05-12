"""
该脚本用于批处理Windows商店B站客户端下载文件。
说明：
1.批量下载的文件MP4格式为音频视频分割；
2.flv格式长视频进行了分切多个短视频；
3.视频文件名为数字串码
环境准备：
1. 下载ffmpeg软件并加载环境变量，下载地址：https://ffmpeg.zeranoe.com/builds/
2. pip安装ffmpy3模块
功能：
1. 对于下载的MP4格式文件语音、视频合成，重命名。处理耗时较长，不建议下载此格式
2. 对于下载的flv格式文件进行拼接，重命名
"""
import json, os, datetime
from ffmpy3 import FFmpeg

#源视频下载路径
source_dir = r"G:\b_cache\795290408"
#处理后视频的输出路径，并新建视频标题文件夹
target_dir = r"D:\bli"


def file_handler(root, files):
    output_dir = ""
    audio_path = ""
    video_path = ""
    flv_list = []

    for file in files:

        if file.endswith(".info"):
            file_name, dir_name = get_video_info(root, file)
            save_dir = os.path.join(target_dir, dir_name)
            if not os.path.exists(save_dir):
                os.mkdir(save_dir)
            output_dir = os.path.join(save_dir, file_name)

        if file.startswith("audio"):
            audio_path = os.path.join(root, file)
        if file.startswith("video"):
            video_path = os.path.join(root, file)
        if file.endswith(".flv"):
            flv_list.append(os.path.join(root, file))
    return output_dir, audio_path, video_path, flv_list


def get_video_info(root, file):
    json_dir = os.path.join(root, file)
    with open(json_dir, "r", encoding="utf-8")as f:
        info_dic = json.load(f)
        file_name = info_dic['PartName']
        file_name = file_name.replace(" ", "")
        dir_name = info_dic['Title']
        return file_name, dir_name


def mp4_handler(video_path, audio_path, output_dir):
    ff = FFmpeg(inputs={str(video_path): None, str(audio_path): None},
                outputs={str(output_dir + '.mp4'): '-c:v h264 -c:a ac3 -v quiet -y'})
    # print(ff.cmd)
    ff.run()


def creat_flv_list_file(root, flv_list):
    flv_list_dir = os.path.join(root, "flv_list.txt")
    with open(flv_list_dir, 'a', encoding='utf-8')as f:
        for i in flv_list:
            f.write("file '{}'\n".format(i))
    return flv_list_dir


def flv_concat(flv_list_dir, output_dir):
    # 不加safe参数报错，-v quiet不显示处理过程，-y覆盖已存在
    ff = FFmpeg(global_options="-f concat -safe 0 ", inputs={str(flv_list_dir): None},
                outputs={output_dir + '.flv': "-c copy -v quiet -y"})
    # print(ff.cmd)
    ff.run()


def flv_handler(root, flv_list, output_dir):

    flv_list_dir = creat_flv_list_file(root, flv_list)
    flv_concat(flv_list_dir, output_dir)
    if os.path.exists(flv_list_dir):
        os.remove(flv_list_dir)


if __name__ == '__main__':
    start = datetime.datetime.now()
    total = 0
    count = 0

    for root, dirs, files in os.walk(source_dir):
        runtime = datetime.datetime.now() - start
        if not total:
            total = len(dirs)
        print("\r\033[1;92m正在处理：第{}个  "
              "共：{}个 "
              "已用时：{}\033[0m".format(count, total, runtime), end='')
        count += 1

        is_video = file_handler(root, files)
        if is_video:
            output_dir, audio_path, video_path, flv_list = is_video
            if video_path and audio_path and output_dir:
                mp4_handler(video_path, audio_path, output_dir)
            if output_dir and flv_list:
                # print(flv_list)
                flv_handler(root, flv_list, output_dir)
    print("\n已全部处理完成！")
