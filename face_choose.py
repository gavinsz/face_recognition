#coding=utf8
import face_recognition
import os
import shutil
import argparse

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

def get_image_encodings(files):
    unknown_face_encodings = []
    front_face_list =[]
    for file in files:
        #print('encoding file=', file)
        name = os.path.basename(file)
        if name == '1.jpg' or name == '1.jpeg':
            image = face_recognition.load_image_file(file)
            encodings = face_recognition.face_encodings(image)
            if len(encodings) == 1:
                image_to_check_encoding = encodings[0]
                unknown_face_encodings.append(image_to_check_encoding)
                front_face_list.append(file)
            else:
                print('image encoding failed|file=%s'%(file))
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
                pass

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
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    similars = sorted(similars.items(), key=lambda d: d[1])
    #print('similars=', similars)

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

def process_choose_image(src_path, out_path, step_start=0):
    dirs = get_all_dirs(src_path)
    count = 0;
    #for i, star_dir in enumerate(dirs, step_start):
    for i in range(step_start, len(dirs), STEP):
        star_dir = dirs[i]
        star_name = get_star_name(star_dir)
        if not star_image_is_choosed(star_name, out_path):
            #print('star_dir=', star_dir)
            files = get_signal_dir_files(star_dir) 
            unknown_face_encodings, image_to_check_encoding, face_img_list = get_image_encodings(files)
            compare_result = face_recognition.face_distance(unknown_face_encodings, image_to_check_encoding)
            similars = get_similar_images(face_img_list, compare_result)
            copy_choosed_image(similars, star_name, out_path)

        print('choosing... %d/%d' %(i, len(dirs)), end='\r')

if __name__ == "__main__":
    src_path = 'E:/workspace/ai/google-images-download-master/downloads/stars-top1000-part1'
    out_path = 'F:\\star-top1000-imgs'

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--progress_id', action="store", help="1....n", default=1, type=int)
    args = parser.parse_args()
    
    process_choose_image(src_path, out_path, args.progress_id)
    print('choose images completed')
    exit(0)

    files = get_signal_dir_files(path)
    unknown_face_encodings, image_to_check_encoding, face_img_list = get_image_encodings(files)
    
    '''
    compare_result = face_recognition.compare_faces(unknown_face_encodings, 
                                            image_to_check_encoding, 
                                            tolerance=0.4)
    '''

    compare_result = face_recognition.face_distance(unknown_face_encodings, image_to_check_encoding)
    similars = get_similar_images(face_img_list, compare_result)

    copy_choosed_image(similars, )

    out_dir = 'output/'
    similars = sorted(similars.items(), key=lambda d: d[1])
    #print('similars=', similars)

    for  i, item in enumerate(similars):
        if i < 10:
            key = item[0]
            name = os.path.basename(key)
            shutil.copy(key, out_dir + name)
            print(item[0], item[1])
    
    '''
    for k, v in  similars.items():
        name = os.path.basename(k)
        shutil.copy(k, out_dir + name)
        print(name, 'similar rate=', v)
    '''
