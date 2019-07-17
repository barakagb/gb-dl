#!/usr/bin/python
from __future__ import print_function
from __future__ import unicode_literals

import os
import re
import wget
import requests, lxml.html
import sys
import getpass
import youtube_dl

from bs4 import BeautifulSoup


class DL:

    global s

    s = requests.session()

    def login(self):
        try:

            self.course_url  = raw_input("Enter course url : ")
            self.email       =   raw_input("Email : ")
            self.password    =  getpass.getpass(prompt="Password : ", stream=sys.stderr)

        except Exception as e:
            self.course_url  = input("Enter course url : ")
            self.email       = input("Email : ")
            self.password    = getpass.getpass(prompt="Password : ", stream=sys.stderr)

        if self.email and self.password and self.course_url:
            try:

                print ("Trying to Login ...")

                if "stackskills" in self.course_url:

                    login_url = "https://sso.teachable.com/secure/1453/users/sign_in?flow_school_id=1453"

                elif "infosec4tc" in self.course_url:

                    login_url = "https://sso.teachable.com/secure/100167/users/sign_in?flow_school_id=100167"

                elif "ehacking" in self.course_url:
                    login_url = "https://sso.teachable.com/secure/13898/users/sign_in?flow_school_id=13898"

                else:
                    print ("[-] In valid course URL.")
                    self.login()

                login = s.get(login_url)
                login_html = lxml.html.fromstring(login.text)

                hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')

                form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}

                form['user[email]'] = self.email
                form['user[password]'] = self.password

                response = s.post(login_url, data=form)

                if "Invalid email or password" in response.text:

                    print ("[-] Login failed.Invalid username or password.")
                    self.login()

                else:
                    print ("[+] Login successful.")

                    self.getSectionAndLinks(self.course_url)

            except Exception as e:
                print ("[-] Connection failed.Please check your internet connection and try again!\n " + str(e))
                sys.exit(1)

        else:

            print ("[-] Please enter course url , email and password")
            self.login()

    def getSectionAndLinks(self, url):
        self.url = url
        index = url.index('com') + 3 if 'com' in self.url else url.index('net') + 3
        self.domain = self.url[0:index]

        try:
            print ("Downloading to :" + os.getcwd())
            print ("Collecting course information ...")

            data = requests.get(self.url)
            soup = BeautifulSoup(data.text, 'html.parser')

            #courseName = soup.find('h2', attrs={'class': 'row'})

            courseName = soup.find('h1', attrs={'class': 'course-title'}) 

            if courseName is None:

                courseName = soup.find('h1', attrs={'class': 'm-0'})

            if courseName is None:

                courseName = soup.find('div', attrs={'class': 'bannerHeader'}).find('h2')

            courseName = str(courseName.get_text()).strip()

            print ("\nCourse name : " + (str(courseName)))

            try:
                os.mkdir(courseName)
                os.chdir(courseName)

            except Exception as e:
                self.createAndChangeDir(courseName)
              
                #os.chdir(courseName)

            print ("Getting course sections ...")

            data = s.get(self.url)

            soup = BeautifulSoup(data.text, 'html.parser')

           # courseImage = soup.find('img',{'class':'course-image'}).get('src')
        
           # print ("Downloading course image ... ")
           
           # wget.download(str(courseImage))

           # os.rename(filesrc, str(self.name))

            c = 1
            for i in soup.find_all('span', {'class':'section-lock'}):
                section = i.next_sibling.strip()
                folder = str(c) + "." + str(section).strip()

                try:
                    if os.path.exists(folder):
                       
                        os.chdir(folder)
                    else:
                        os.mkdir(folder)
                        os.chdir(folder)

                except Exception as e:
                    self.createAndChangeDir(folder)

                print ("\n[+] Found Section : ", section + "\n")

                divs = soup.find_all('div', {'class': 'course-section'}, )

                for div in divs:
                    links = []

                    if div.find(text=re.compile(section)):

                        theDiv = div

                        soupLinks = BeautifulSoup(str(theDiv), 'html.parser')

                        for i in soupLinks.find_all('a', {'class': 'item'}):

                            links.append(self.domain+i.attrs['href'])

                        self.prepareDownload(links)
                        links = []

                        os.chdir('../')

                        break

                c += 1

            #self.sanitizeFileNames()
            print ("\n[+] Download completed.Enjoy your course " + self.email)

        except Exception as ex:
            print ("[-] Error : " + str(ex))
            sys.exit(1)




    def prepareDownload(self,links):

            c = 1
            totalLectures = len(links)

            Attachments= []

            for link in links:
                print ("Preparing  lecture " + str(c) + " of " + str(totalLectures) + " download ... ")

                data2 = s.get(link)
                soup1 = BeautifulSoup(data2.text, 'html.parser')


                # wistia= soup1.findAll("div", id=lambda x: x and x.startswith('wistia-'))

                _dict = {}
                for i in soup1.find_all('a', {'class': 'download'}):
                    _dict["href"] = i.attrs['href']
                    _dict["name"] = i.attrs['data-x-origin-download-name']
                    Attachments.append(_dict)

                for attachment in soup1.findAll('iframe'):
                    Attachments.append(attachment.get('src'))

                for i in soup1.findAll('div', {"class": 'attachment-wistia-player'}):

                    wistia_id = (i.get('data-wistia-id'))

                    self.download(wistia_id)

                self.download(0, Attachments)

                Attachments=[]

                c += 1

    def download(self,id,*attachments):

        if id != 0:
            self.wistia_url = "http://fast.wistia.net/embed/iframe/"
            course_url = self.wistia_url+id

            try:
                print ("Starting download ... ")
                ydl_opts = {}
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([course_url])

            except Exception as ex:
                print ("[-]" + "Error : " + str(ex))
        else:

            for attachment in attachments:
                try:

                    if attachment:
                        for x in attachment:
                            self.name = str(x["name"])
                            self.url = str((x["href"]).strip('[]'))
                           # self.url = self.url[2:-1].strip()

                        print ("Downloading attachment : " + self.name)
                        filesrc = wget.download(str(self.url))

                        os.rename(filesrc, str(self.name))

                except Exception as e:

                    print ("[-]" + "Error can not download attachment  : " + str(e))

    def sanitizeFileNames(self):

        if "stackskills" in self.course_url:
            return

        print("sanitizing file names ...")

        path = os.getcwd()
        for root, dirs, files in os.walk(path):

            for dir in dirs:
                subFolder = os.path.join(path, dir)
               # print subFolder, "\n"

                for root, dirs, files in os.walk(subFolder):
                    for file in files:
                        try:
                            index = file.index('mp4') + 3

                            filesrc = os.path.join(subFolder, file)
                            filedest = os.path.join(subFolder, file[0:index])

                            os.rename(filesrc, filedest)
                        except Exception as e:
                            pass
        print("[+]" + "file name sanitation completed")

    def createAndChangeDir(self, dirName):
        ''' Creates and changes directory if dir name has invalid chars '''

        invalidChars = ['<', '>', ':', '"', '/', '|', '\\', '?', '*']
        for char in invalidChars:
            if char in dirName:
                dirName = dirName.replace(char, "")
                if os.path.exists(dirName):
                    os.chdir(dirName)

                else:
                    os.mkdir(dirName)
                    os.chdir(dirName)
        return

    def main(self):
        banner = '''  
                              
                   _____ ____                 _ _ 
                  / ____|  _ \               | | |
                 | |  __| |_) |  ______    __| | |
                 | | |_ |  _ <  |______|  / _` | |
                 | |__| | |_) |          | (_| | |
                  \_____|____/            \__,_|_|
             
           			        Version : 1.3.0
                            Author  : BarakaGB
                            Visit   : https://github.com/barakagb/gb-dl
                   Paypal Donation  : barakagb[at]gmail[dot]com
                    '''
        print(banner)
        print('''A python based utility to download courses from infosec4tc.teachable.com , academy.ehacking.net and stackskills for personal offline use. \n\n''')

        self.login()


if __name__ == '__main__':
    try:
        DL = DL()
        DL.main()
    except KeyboardInterrupt:
        print ("User Interrupted.")
        sys.exit(1)
    except Exception as e:
        print (e)
sys.exit(1)
