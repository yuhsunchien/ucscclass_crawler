import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import re

class_url='https://www.ucsc-extension.edu/certificate-program'
ucsc_url='https://www.ucsc-extension.edu/'
#Get html
def get_web_page(url):
    resp = requests.get(
        url=url)
    if resp.status_code != 200:
        #print('Invalid url:', resp.url)
        return None
    else:
        return resp.text
#Parse the courselist
def parse1(dom):
    soup = BeautifulSoup(dom, 'html5lib')
    Allist = dict()
    courses=soup.find_all('div','views-field views-field-name')
    for course in courses:
        Allist.update({course.text.strip():course.a['href']})
    return Allist
#Parse detail info
def parse2(dom,key):
    soup = BeautifulSoup(dom, 'html5lib')
    links=soup.find_all('div','post-content')
    courselists=[]

    try:
        nextpage=soup.find('a',title='Go to next page')['href']
    except:
        nextpage='ZZZ'
    for link in links:
        temp = link.find_all('table','views-table')
        name= link.parent.find('h2')
        for temp1 in temp:
            if temp1.find('a'):

                count=len(temp1.tbody.find_all('tr'))
                while count >=1:
                    #tempp=temp1.tbody.find_all('td')
                    tempp=temp1.tbody.find_all('tr')[count-1].find_all('td')
                    count-=1
                    try:
                        number=tempp[0].text
                        date=tempp[1].text
                        place=tempp[3].text
                        if not place == 'ONLINE':
                             time = tempp[2].text
                        else :time = 'NA'
                        fee=tempp[4].text
                        teacher=tempp[5].text
                        # for tempp1 in tempp:
                        #     if tempp1.find_all('a') and re.match(r'/shop.*', tempp1.find('a')['href']):
                        web=tempp[7].find('a')['href']

                        date_temp=date.split('/')
                        week_temp=datetime(int(date_temp[2].strip()),int(date_temp[0].strip()),int(date_temp[1].strip())).weekday()+1
                        week=weekday(str(week_temp))

                        temp = re.split('=|&', web)
                        href = "http://course.ucsc-extension.edu/modules/shop/defaultSections.action"
                        period, Credits = parse3(href, temp[3], temp[5])


                        courselists.append({
                            'CourseNumber': number,
                            'StartDate': date,
                            'Day': week,
                            'Campus': place,
                            'fee':fee,
                            'teacher':teacher,
                            'href':web,
                            'name': name.text.strip(),
                            'group':key,
                            'time':time,
                            'period':period,
                            'Credits':Credits

                                            })


                    except:
                        pass
    return courselists,nextpage


def parse3(url,offID,SecID):
    def post_web_page(url,postdata):
        resp = requests.post(
            url=url,data=postdata)
        if resp.status_code != 200:
            #print('Invalid url:', resp.url)
            return None
        else:
            return resp.text
    #Parse the courselist
    dom = post_web_page(url,{"OfferingID":offID,"SectionID":SecID})
    soup = BeautifulSoup(dom, 'html.parser')
    enddate=soup.find("enddate")
    startdate=soup.find("startdate")
    Credit = soup.find("credithours").text
    period = str(startdate.text[:11]).strip()+"-"+str(enddate.text[:11]).strip()
    return period,Credit
def weekday(num):
    if num=='1':
        return 'Mon'
    elif num == '2':
        return 'Tue'
    elif num == '3':
        return 'Wed'
    elif num == '4':
        return 'Thu'
    elif num == '5':
        return 'Fri'
    elif num == '6':
        return 'Sat'
    elif num == '7':
        return 'Sun'




if __name__ == '__main__':
    print('Processing...........')
    #Grab groups list
    count=0
    courselistsa=[]
    newlist = []
    resp=get_web_page(class_url)
    Allist=parse1(resp)
   #get every course detal
    for k in Allist.keys():
        newWeb=get_web_page(ucsc_url+Allist[k])
        grouplist,nextpage=parse2(newWeb,k)
        while grouplist:
            #To check nextpage bottom => Y:keep get next-page information.
            courselistsa.append(grouplist)
            count=count+1
            print("imported " + str(count) + " pages of courses")
            try:
                newWeb = get_web_page(ucsc_url + nextpage)
                print ()
                if newWeb==None:
                    break
                else:
                    grouplist, nextpage = parse2(newWeb, k)
            except:
                grouplist=[]


#Print csv
    with open('List.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(('Group', 'Name', 'CourseNumber', 'StartDate', 'Days','Time',"Period",'Credits',
                         'Campus', 'Fee', 'Teacher', 'Detail'))
        for groups in courselistsa:
            for listsa in groups:
                writer.writerow((listsa['group'], listsa['name'], listsa['CourseNumber'], listsa['StartDate'], listsa['Day'], listsa['time'],
                                 listsa["period"],listsa["Credits"],listsa['Campus'], listsa['fee'], listsa['teacher'], listsa['href']))
    print('Done!!Press any key to exit')
    input()


