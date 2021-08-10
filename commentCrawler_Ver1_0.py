import os
import random
import re
import requests
import time
import codecs
from bs4 import BeautifulSoup

def bv2av(bvid):
   site = "https://api.bilibili.com/x/web-interface/view?bvid=" + bvid
   lst = codecs.decode(requests.get(site).content, "utf-8").split("\"")
   if int(lst[2][1:-1]) != 0: return "视频不存在！"
   return lst[16][1:-1]

def getTitle(webNumber):
   headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}  # 代理用户进行浏览器伪装
   if webNumber.startswith('BV'):
      url='https://www.bilibili.com/video/'+webNumber
      try:  # 尝试
         html = requests.get(url, headers=headers)
         html.raise_for_status()
         soup = BeautifulSoup(html.text, "html.parser")
         data = soup.find('h1', class_="video-title")
         d = re.compile('title=".*"').findall(str(data))  # 一次筛选 通过正则表达式来筛选从(title=")到(")之间的字段
         d1 = re.compile('\".*?\"').findall(str(d))  # 二次筛选
         title = str(d1[0])
         title = title.replace('"', '')
         return title
      except:  # 如果错误的话
         print("error")
         return
   else:
      url='https://www.bilibili.com/read/'+webNumber
      try:  # 尝试
         html = requests.get(url, headers=headers)
         html.raise_for_status()
         soup = BeautifulSoup(html.text, "html.parser")
         data = str(soup.find('h1', class_="title"))
         start_pos=data.find('>')
         end_pos=data.rfind('<')
         title = data[start_pos+1:end_pos]
         return title
      except:  # 如果错误的话
         print("error")
         return


def fileNameCleaning(file_name):
   file_name=file_name.replace('?','').replace('<','').replace('>','')\
      .replace('|','').replace('╲','').replace('/','').replace('.','')\
      .replace('*','').replace('、','')
   return file_name

if __name__ == '__main__':
   print('___Coded by @Sansheng 2021___')
   time.sleep(2)
   comment_list = []  #创建评论空字典
   type_dict={'BV':'1','cv':'12'}
   webNumber=input("请输入BV号或者cv号（包括BV和cv字样）:")
   while 1:
      if webNumber.startswith('BV')|webNumber.startswith('cv'):
         print('解析成功~')
         type=type_dict[webNumber[0:2]]
         video_title=getTitle(webNumber)
         print('标题为：'+video_title)
         if(webNumber[0:2]=='BV'):
            print('类型为：视频')
            oid=bv2av(webNumber[2:len(webNumber)])
         else:
            print('类型为：专栏')
            oid = webNumber[2:len(webNumber)]
         break
      else:
         webNumber=input('解析失败，请确认输入是否正确\n请重新输入：')
   print('oid为：'+str(oid)+'\n')
   print('开始爬取评论')
   print('________________________________')

   page_order=0
   while 1:
      page_order = page_order + 1
      url = 'https://api.bilibili.com/x/v2/reply?jsonp=jsonp&type='+type+'&oid='+oid+'&sort=2&pn='+str(page_order) #评论接口
      headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36' } #代理用户进行浏览器伪装
      html = requests.get(url = url,headers = headers)
      data = html.json()
      comment=[]  #创建本页评论空字典
      #解析json
      if data['data']['replies']:
         for item in data['data']['replies']:
            comment.append({'Name':item['member']['uname'],'Comment':item['content']['message']})

      numOfComments=len(comment)
      if numOfComments==0: #如果本页未找到评论则跳出循环
         page_order=page_order-1
         break
      comment_list.extend(comment) #将本页评论加入到评论列表中
      print('第' + str(page_order) + '页，找到' + str(numOfComments) + '条评论')
      time.sleep(1+2*random.random())

   print('________________________________')
   if page_order==0:
      print('爬取失败！请检查是否输入了正确的av/bv/cv号')
   else:
      print('评论爬取完成!')
      print('共'+str(page_order)+'页，共计'+str(len(comment_list))+'条评论')
   video_title=fileNameCleaning(video_title)
   relDir=os.getcwd()
   dir=relDir+'\\'+video_title+'.txt'
   print('输出文件路径：'+dir+'\n')
   comment_txt = open(dir,'w',encoding='utf-8') #创建txt文本
   for item in comment_list:
      comment_txt.write(item['Name']+'\n'+item['Comment']+'\n\n') #写入txt文本
