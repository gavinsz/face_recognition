#coding=utf8
import face_recognition
import os
import shutil
import argparse
import logging
import multiprocessing as mp
import math

logging.basicConfig(filename='logger.log', 
                    format='%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s', 
                    level = logging.DEBUG,
                    filemode='a',
                    datefmt='%Y-%m-%d %I:%M:%S %p')
STEP = int(7)

def get_star_name(path):
    #path='E:/workspace/ai/google-images-download-master/downloads/stars-top1000-part3/周震南'
    #star name=周震南
    return path.split('/')[-1]

def get_all_dirs(path):
    files = os.listdir(path)
    s = []
    for file in files:
        #print(file)
        s.append(os.path.join(path, file))

    return s

def get_signal_dir_files(path):
    files = os.listdir(path)
    s = []

    for file in files:
        #判断是否是文件夹，不是文件夹才打开
        if not os.path.isdir(file):
            s.append(os.path.join(path, file))

    return s

def get_image_encodings(star_name, files):
    unknown_face_encodings = []
    front_face_list =[]
    have_check_img = False

    for file in files:
        #print('encoding file=', file)
        name = os.path.basename(file)
        if name == '1.jpg' or name == '1.jpeg':
            have_check_img = True
            try:
                image = face_recognition.load_image_file(file)
                encodings = face_recognition.face_encodings(image)
            except Exception as err:
                logging.error('load image failed|file=%s'%(file))
                return None, None, None
                    
            if len(encodings) == 1:
                image_to_check_encoding = encodings[0]
                unknown_face_encodings.append(image_to_check_encoding)
                front_face_list.append(file)
            else:
                logging.error('image encoding failed|file=%s'%(file))
                #print('image encoding failed|file=%s'%(file))
                return None, None, None
        else:
            try:
                image = face_recognition.load_image_file(file)
                encodings = face_recognition.face_encodings(image)
                #print(name, 'encodings len=', len(encodings))
                if len(encodings) == 1:
                    unknow_face_to_encoding = face_recognition.face_encodings(image)[0]
                    unknown_face_encodings.append(unknow_face_to_encoding)
                    front_face_list.append(file)
            except Exception as err:
                #print('open image failed|err=%s|file=%s'%(err, file))
                logging.error('load image failed|file=%s'%(file))
                pass

    if have_check_img is False:
        #print(star_name, 'donot have 1.jpg or 1.jpeg')
        logging.error('%s donot have 1.jpg or 1.jpeg'%(star_name))
        return None, None, None

    return unknown_face_encodings, image_to_check_encoding, front_face_list

def get_similar_images(files, result):
    similars = dict()
    #print('len(files)=', len(files), 'len(result)=', len(result))
    for i, file_name in enumerate(files):
        #name = os.path.basename(file)
        similars[file_name] = result[i]
    
    return similars

def copy_choosed_image(similars, star_name, dst_path):
    out_dir = os.path.join(dst_path, star_name)
    #print('dst_path=', dst_path, 'out_dir=', out_dir)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    similars = sorted(similars.items(), key=lambda d: d[1])
    #print('copy_choosed_image similars=', similars)

    for  i, item in enumerate(similars):
        if i < 10 and item[1] < 0.6:
            key = item[0]
            name = os.path.basename(key)
            shutil.copy(key, os.path.join(out_dir, name))
            #print(item[0], item[1])

def star_image_is_choosed(star_name, dst_path):
    out_dir = os.path.join(dst_path, star_name)
    if not os.path.exists(out_dir):
        return False
    else:
        return True

def chunks(arr, m):
    n = int(math.ceil(len(arr) / float(m)))
    return [arr[i:i + n] for i in range(0, len(arr), n)]

def process_choose_image(dirs, out_path):
    
    for i, star_dir in enumerate(dirs):
        star_name = get_star_name(star_dir)
        if not star_image_is_choosed(star_name, out_path):
            #print('star_dir=', star_dir)
            files = get_signal_dir_files(star_dir) 
            unknown_face_encodings, image_to_check_encoding, face_img_list = get_image_encodings(star_name, files)
            if image_to_check_encoding is None:
                #print('continue')
                continue
            compare_result = face_recognition.face_distance(unknown_face_encodings, image_to_check_encoding)
            #print('compare_result=', compare_result)
            similars = get_similar_images(face_img_list, compare_result)
            #print('similars=', similars)
            copy_choosed_image(similars, star_name, out_path)

        print('choosing... %d/%d' %(i, len(dirs)), end='\r')

if __name__ == "__main__":
    src_path = 'E:/workspace/ai/google-images-download-master/cpc_images'
    out_path = 'F:\\cpc_images'

    '''
    #单进程挑选图片
    dirs = get_all_dirs(src_path)
    process_choose_image(dirs, out_path)
    '''

    #多进程挑选图片
    #max process number
    process_num = 7
    pool = mp.Pool(process_num)
    dirs = get_all_dirs(src_path)
    dirs_chunks = chunks(dirs, process_num)
    for chunk in dirs_chunks:
        #print('len(chunk)=', len(chunk))
        pool.apply_async(process_choose_image, (chunk, out_path,))
    
    pool.close()
    pool.join()

    print('choose images completed')

