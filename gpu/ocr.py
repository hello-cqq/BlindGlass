# -*- coding: UTF-8 -*-
from aip import AipOcr
#here are baidu api personal information
APP_ID = '15914447'
API_KEY = '8GBoUkQqclUYcaQvfQSQ2QoY'

SECRET_KEY = 'PEz4P5qRGGVUSRApUZ4p3sqw3vfIjmUB'

aipOcr  = AipOcr(APP_ID, API_KEY, SECRET_KEY)


def get_file_content(filePath):
	with open(filePath,'rb') as fp:
		return fp.read()

def get_result(img_name, img_path, location):
	options = {"language_type": 'CHN_ENG',
				"detect_direction":'true',	
				"detect_language":'true',
				"probability":'true'}
	results = aipOcr.basicAccurate(get_file_content(img_path), options)

	finnal_result = ''
	for item in results['words_result']:
		finnal_result += item['words']
	print(finnal_result)
	result = {}
	result['name'] = img_name
	result['res_path'] = './photo/original/'+img_name+'.jpg'
	result['text'] = ''
	result['target'] = '书'
	result['msg'] = finnal_result
	return result

if __name__ == '__main__':
	get_result('./QQ.png', './QQ.png','')

