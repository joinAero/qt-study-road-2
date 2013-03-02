# -*- coding:utf-8 -*-

import os
import re
import urllib
import urllib2
from os import path

def fetch_html(url):
	"""抓取网页"""
	return urllib2.urlopen(url).read()

def get_catalogs():
	"""获取目录地址"""
	html = fetch_html('http://www.devbean.net/2012/08/qt-study-road-2-catelog/')
	patt = r'<li><a href="(http://www.devbean.net/\d{4}/\d{2}/qt-study-road-2-(.*?)/)".*?>(.+?)</a></li>'
	return re.findall(patt, html)

def get_infos(article_url):
	"""获取文章的内想要的信息"""
	html = fetch_html(article_url)
	patt = r'日期:\s+?(\d{4} 年 \d{2} 月 \d{2} 日)'
	res = re.search(patt, html)
	if res:
		date = res.group(1).replace(' ', '')
		return date
	return 'None'

def temp(d):
	"""替换字典表内容"""
	with open('template', 'r') as f:
		temp = ''.join(f.readlines())
	def inner_temp(d):
		new_temp = temp
		for k, v in d.items():
			new_temp = new_temp.replace(k, v)
		return new_temp
	return inner_temp(d)

def temp_rst(ref, title, url, date):
	# uft8，中文字符长度为3，所以会长点
	n = len(title) + len(url) + 6
	dashes = '=' * n
	d = {
		'{ref}': ref,
		'{title}': title,
		'{dashes}': dashes,
		'{url}': url,
		'{date}': date
	}
	return temp(d)

def write_file(filename, content):
	"""将content写入指定文件"""
	with open(filename, 'w') as f:
		f.write(content)

def main():
	# print temp_rst('qt_intro', '2. Qt 简介', 'http://www.devbean.net/2012/08/qt-study-road-2-qt-intro/', '2012年08月21日')
	# print get_infos('http://www.devbean.net/2012/08/qt-study-road-2-catelog/')

	x, y = 0, 0
	fname_list = []
	catalog_list = get_catalogs()
	for n, catalog in enumerate(catalog_list):
		url, name, title = catalog

		num = str(n + 1) # 2
		ref = name.replace('-', '_') # qt_intro
		filename = ''.join([num, '_', ref, '.rst']) # 2_qt_intro.rst
		fname_list.append(filename)

		if path.exists(filename):
			print(filename + ' 已存在')
			x += 1
		else:
			title = ''.join([num, '. ', title]) # 2. Qt 简介
			date = get_infos(url) # 2012年08月21日 or None
			content = temp_rst(ref, title, url, date)
			write_file(filename, content)
			print(filename + ' 已新建')
			# print(content)
			y += 1

	print('已有%d个文件，新增了%d个文件' % (x, y))

	# print('**' * 10)
	# for fname in fname_list:
	# 	print(fname[:-4])

if __name__ == '__main__':
	main()
