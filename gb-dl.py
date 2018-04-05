#!/usr/bin/python
from __future__ import unicode_literals

import os
import re

import requests,lxml.html
import sys
import getpass
import youtube_dl



from bs4 import BeautifulSoup
from blessings import Terminal




class dl:

    global s
    global t


    t = Terminal()





    s = requests.session()



    def login(self):

        self.course_url         =      raw_input("Enter course url : ")
        self.email       =      raw_input("Email : ")
        self.password    =      getpass.getpass(prompt="Password : " , stream=sys.stderr)


        if self.email and self.password and self.course_url:
            try:

                print "Trying to Login ..."

                if  "stackskills"  in self.course_url:

                    login_url = "https://sso.teachable.com/secure/1453/users/sign_in?flow_school_id=1453"

                elif "infosec4tc" in self.course_url:

                    login_url = "https://sso.teachable.com/secure/100167/users/sign_in?flow_school_id=100167"



                login = s.get(login_url)
                login_html = lxml.html.fromstring(login.text)

                hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')

                form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}

                form['user[email]'] = self.email
                form['user[password]'] = self.password

                response = s.post(login_url,data=form)





                if "Invalid email or password" in response.text:

                    print "[-]" + t.red("Login failed.Invalid username or password.")
                    sys.exit(1)

                else:
                    print "[+]" + t.green("Login succesful.")
                    self.getSectionAndLinks(self.course_url)





            except Exception as e:
                print "[-]" + t.red("Connection failed.Please check your internet connection and try again!")
                sys.exit(1)



        else:


            print t.red("Please enter course url ,email and password")
            sys.exit(1)


    def getSectionAndLinks(self,url):
        self.url = url
        index = url.index('com') + 3
        self.domain = self.url[0:index]

        try:

            print "Collecting course information ..."

            data = requests.get(self.url)

            soup = BeautifulSoup(data.text, 'html.parser')


            courseName = soup.find('h1', attrs={'class': 'course-title'})
            courseName = str(courseName.get_text()).strip()


            print "\nCourse name : " + t.cyan(courseName)



            try:
                os.mkdir(courseName)
                os.chdir(courseName)

            except Exception as e:
                os.chdir(courseName)




            print "Getting course sections ..."

            c = 1
            for i in soup.find_all('span', {'class':'section-lock'}):
                section = i.next_sibling.strip()
                folder = str(c) + "." + str(section).strip()

                try:
                    os.mkdir(folder)
                    os.chdir(folder)
                except Exception as e:
                    os.chdir(folder)



                print "\nFound Section : " , t.cyan(section) + "\n"


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


            self.sanitizeFileNames()
            print t.green("\nDownload completed.")

        except Exception as e:
            print t.red("Course not found or You need to purchase course.")

    def prepareDownload(self,links):

            c = 1
            totalLectures = len(links)

            Attachments= []

            for link in links:
                print "Preparing  lecture " + str(c) + " of " + str(totalLectures) + " download ... "


                data2 =  s.get(link)
                soup1 = BeautifulSoup(data2.text, 'html.parser')


                # wistia= soup1.findAll("div", id=lambda x: x and x.startswith('wistia-'))

                for attachment in soup1.findAll('iframe'):
                    Attachments.append(attachment.get('src'))




                for i in soup1.findAll('div', {"class": 'attachment-wistia-player'}):


                    wistia_id=(i.get('data-wistia-id'))

                    self.download(wistia_id)

                self.download(0,Attachments)

                Attachments=[]

                c += 1






    def download(self,id,*attachments):

        if id != 0:
            self.wistia_url = "http://fast.wistia.net/embed/iframe/"
            course_url = self.wistia_url+id

            try:
                print "Starting download ... "
                ydl_opts = {}
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([course_url])


            except Exception as e:
                print e
        else:
            for attachment in attachments:

                try:
                    os.popen("wget " +attachment )



                except Exception as e:
                    print e

    def sanitizeFileNames(self):
        print "sanitizing file names ..."

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
        print "[+]" + t.green("sanitize completed")


    def main(self):
        banner = '''  
                              
                   _____ ____                 _ _ 
                  / ____|  _ \               | | |
                 | |  __| |_) |  ______    __| | |
                 | | |_ |  _ <  |______|  / _` | |
                 | |__| | |_) |          | (_| | |
                  \_____|____/            \__,_|_|
             
           			        Version : 0.1
                            Author  : BarakaGB
                            Visit   : https://github.com/barakagb



                    '''
        print t.cyan(banner)
        print t.green('''A python based utility to download courses from infosec4tc.teachable.com and stackskills for personal offline use. \n\n''')


        self.login()




if __name__ == '__main__':
    try:
        dl= dl()
        dl.main()
    except KeyboardInterrupt:
        print ("User Interrupted.")
        sys.exit(1)







