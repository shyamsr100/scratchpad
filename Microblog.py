# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template,flash, redirect,jsonify,request
from models import db,User
from dbModels import db,User_Response
import os,socket
import json
import csv
import unicodecsv
import shutil, glob
from operator import itemgetter
from pandas import DataFrame
import pandas as pd
import unicodedata
import urllib2
import mysql.connector
import codecs
import StringIO
from StringIO import StringIO
from flask import Response
from flask import make_response
from bs4 import BeautifulSoup,Tag
from bs4 import NavigableString
import itertools
import nltk
import re
import nltk
from nltk.corpus import stopwords
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser
from cassandra.cluster import Cluster
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotVisibleException
import unicodecsv
from lxml import etree
import xml
from google.cloud import language, client
import os, json
from time import sleep


def init_driver():
    driver = webdriver.Chrome('/Users/ShyamR/Downloads/chromedriver')
    driver.wait = WebDriverWait(driver, 5)
    return driver


def lookup(driver, query):
    driver.get("http://www.google.com")
    try:
        box = driver.wait.until(EC.presence_of_element_located(
            (By.NAME, "q")))
        button = driver.wait.until(EC.element_to_be_clickable(
            (By.NAME, "btnK")))
        box.send_keys(query)
        try:
            button.click()
            time.sleep(3)
            results = driver.find_elements_by_xpath('//*[@id="rso"]/div[4]/div[1]/div/h3')
            return results
        except ElementNotVisibleException:
            button = driver.wait.until(EC.visibility_of_element_located(
                (By.NAME, "btnG")))
            button.click()
            return None
    except TimeoutException:
        print("Box or Button not found in google.com")
        return None

def clean_html(html):


        # First we remove inline JavaScript/CSS:
        cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
        # Then we remove html comments. This has to be done before removing regular
        # tags since comments can contain '>' characters.
        cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
        # Next we can remove the remaining tags:
        cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
        # Finally, we deal with whitespace
        cleaned = re.sub(r"&nbsp;", " ", cleaned)
        cleaned = re.sub(r"  ", " ", cleaned)
        cleaned = re.sub(r"  ", " ", cleaned)
        result = cleaned.strip()
        return result

app = Flask(__name__)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/corasgpd_20`50626'
db.init_app(app)


global accept_list_file_dict
global reject_list_file_dict
global only_displayed_reviews
global rejected_reviews_file_dict

directory_path="/Users/ShyamR/Desktop/internal_dashboard/Microblog/"
treemap_clusters_full_file_name="/Users/ShyamR/Downloads/document_clusters_elbow_method_from_git_final.json"
accept_list_file = open(os.path.join(directory_path+"static/results_positive.txt"),'r+')
reject_list_file = open(os.path.join(directory_path+"static/results_negative.txt"),'r+')
# for the list of rejected reviews
rejected_reviews_list_file=open(os.path.join(directory_path+"static/rejected_reviews.txt"),'r+')

accept_list_file_dict = {word: 'true' for word in accept_list_file}
reject_list_file_dict = {word: 'true' for word in reject_list_file}
rejected_reviews_file_dict= {word.split('~')[0]+'~'+word.split('~')[1]+'~'+word.split('~')[2]: 'true' for word in rejected_reviews_list_file}

# Data frame initialization
global df3
df3 = DataFrame()
only_displayed_reviews=list()
#df1=pd.read_csv(os.path.join(directory_path+"static/full_diverse_reviews_mix_new2_2015-05-05.txt"),delimiter="~", encoding="utf-8-sig")
#print(len(df1))
#df2=pd.read_csv(os.path.join(directory_path+"static/source_reviews_tokenised_2015-12-08_tablets.txt"),delimiter="~", encoding="utf-8-sig")
#print (len(df2))
#df3=df1.merge(df2,how='inner',on='source-review-id')
#print len(df3)
#df3=df3[df3['diverse'] == 1]

# End Data frame initialization
# String to unicode problemo
def to_unicode(unicode_or_str):
    if isinstance(unicode_or_str, str):
        try:
            value = unicode_or_str.decode('utf-8')
        except UnicodeDecodeError:
            print unicode_or_str
            exit()
    else:
        value = unicode_or_str
    return value  # Instance of unicode


def to_str(unicode_or_str):
    if isinstance(unicode_or_str, unicode):
        value = unicode_or_str.encode('utf-8')
    else:
        value = unicode_or_str
    return value  # Instance of str

# Google oAuth stuff
GOOGLE_CLIENT_ID = '644499655555-oklvcc2ci1dufi8r1ki69u1e340aotf5'
GOOGLE_CLIENT_SECRET = 'bnny967zOZFkPmpn6r3V9moO'
REDIRECT_URI = '/authorized' # one of the Redirect URIs from Google APIs console
# Google oAuth stuff


@app.route('/')
def hello_world():

    print len(accept_list_file_dict)
    print accept_list_file_dict
    print len(reject_list_file_dict)
    print reject_list_file_dict
    return 'Hello world!'


@app.route('/index')
def index():
    user = {'nickname': 'Shyam Ramakrishnan'}  # fake user
    posts = [  # fake array of posts
        {
            'author': {'nickname': 'Mark Twain'},
            'body': 'The Adventures of Tom Sawyer'
        },
        {
            'author': {'nickname': 'Daniel Defoe'},
            'body': 'Robinson Crusoe'
        }
    ]
    return render_template("index.html",
                           title='Home',
                           user=user,
                           posts=posts)

'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for OpenID="%s", remember_me=%s' %
              (form.openid.data, str(form.remember_me.data)))
        return redirect('/index')
    return render_template('login.html',
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])

'''
#@app.route('/test')
#def test():
 #   newuser = User("It's a dog-eat-dog world. Hello")
  #  db.session.add(newuser)
 #   db.session.commit()
  #  return 'Hello Beautiful world'


@app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)

@app.route('/compute')
def compute():
    return render_template('compute.html')


@app.route('/start')
def start():
    return render_template('seed.html')


@app.route('/work')
def work():
    #number of lines to find out how many chunks
    num_lines = sum(1 for line in open('../../../PycharmProjects/Microblog/static/processor_lexicons.txt'))
    num_chunks=num_lines/400
    return render_template('admin-ui.html',results=num_chunks+1,summary='Summary from document')



@app.route('/_show_seed_words')
def show_seed_words():
    aspect=request.values.get('parameter')

    resultant = str(os.getcwd())
    options_group=''
    file_name=aspect
    print file_name
    seed_words_file = open("/home/shyamsunderramakrishnan/PycharmProjects/Microblog/static/"+file_name+".txt",'rb')
    options_group = ''
    for line in seed_words_file:
        line = line.strip()
        options_group += '<option value=' + '"' + line + '"' + '>' + line + '</option>'
    return jsonify(options=options_group)


@app.route('/_show_list_for_input_output')
def show_list_for_input_output():
    section_number = int(request.values.get("section_number"))
    print 'Section number is' + str(section_number)
    selected_parameter = request.values.get('parameter')
    print 'Selected Parameter is '+selected_parameter
    start_line=1+(section_number-1)*400
    print 'Start Line is ' + str (start_line)
    line_counter=1
    resultant = str(os.getcwd())
    options_group=''
    seed_words_file = open('/home/shyamsunderramakrishnan/Desktop/enixta-machine-learning/python/lexicon_generation_optmised_code/saved_model/graph_lexicons/'+selected_parameter+".txt_lexicons.txt",'rb')
    options_group = '<table class="table table-striped table-bordered table-hover" id="sample_2"><thead><tr><th>Sl. No</th><th>Word</th><th>Status</th><th>Action</th></tr></thead><tbody>'

    for line_number, line in enumerate(seed_words_file, start=start_line):
        keyword = line.strip().split('\t')[0]
        keyword=keyword.replace("_"," ")
        #line=line.strip()
        #options_group += '<tr class="odd gradeX"><td>'+str(line_number)+'</td><td>'+keyword+'</td><td><div id="slider-snap-inc'+str(line_number)+'" class="slider bg-grey-steel"></div><div class="slider-value"><input type="hidden" id="amount'+str(line_number)+'"></div></td><td><span class="label label-sm label-success">Approved </span></td></tr>'
        options_group += '<tr class="odd gradeX"><td>'+str(line_number)+'</td><td id="word-'+str(line_number)+'">'+keyword+'</td><td><div id="slider-snap-inc'+str(line_number)+'" class="slider bg-grey-steel"></div><div class="slider-value"><input type="hidden" id="amount'+str(line_number)+'" value = "1"></div></td><td><button type="submit" class="btn btn-success"> Submit</button></td></tr>'
        line_counter+=1
        if (line_counter==401):
            break
    options_group += '</tbody></table>'
    return jsonify(options=options_group)



@app.route('/slide')
def slide():
    return render_template('slider.html')


@app.route('/run_bash')
def run_bash():
    os.getcwd()
    os.chdir('../../../Downloads/shyam_code_graph_propagation')
    
    os.system('bash run.sh')
    return render_template('index.html')


@app.route('/save_results')
def save_results():
    accept = request.values.get('accept')
    reject = request.values.get('reject')
    #accept_string = ','.join(accept)
    #reject_string = ','.join(reject)
    reject_list = json.loads(reject)
    accept_list = json.loads(accept)
    accept_list_file = open("../../../PycharmProjects/Microblog/static/results_positive.txt",'r+')
    reject_list_file = open("../../../PycharmProjects/Microblog/static/results_negative.txt",'r+')
    options_group = ''
    for word in accept_list:
        if word not in accept_list_file_dict.keys():
            accept_list_file.write(word+'\n')
            accept_list_file_dict.update({word:'true'})
    for word in reject_list:
        if word not in reject_list_file_dict.keys():
            reject_list_file.write(word+'\n')
            reject_list_file_dict.update({word:'true'})
    return jsonify(results=reject)


@app.route('/add_phones')
def add_phones():
    compare_phones_file = open(os.path.join(directory_path+"static/matched_mobile_phones3.csv"),'rb')
    reader = csv.reader(compare_phones_file)
    list_of_records = list()
    for row in reader:
        tuple_row = (row[1],row[2],row[3])
        list_of_records.append(tuple_row)
    return render_template('compare_data.html',results=list_of_records)


@app.route('/save_compare_results')
def save_compare_results():
    accept = request.values.get('accept')
    reject = request.values.get('reject')
    #accept_string = ','.join(accept)
    #reject_string = ','.join(reject)
    reject_list = json.loads(reject)
    accept_list = json.loads(accept)
    print len(accept_list)
    print len(reject_list)
    accept_list_file = open("../../../PycharmProjects/Microblog/static/mobile_accept.txt",'r+')
    reject_list_file = open("../../../PycharmProjects/Microblog/static/mobile_reject.txt",'r+')
    options_group = ''
    for word in accept_list:
        accept_list_file.write(word+'\n')
    for word in reject_list:
        reject_list_file.write(word+'\n')
    return jsonify(results=reject)



@app.route('/save_words_and_process', methods=['GET', 'POST'])
def save_words_and_process():
    keywords_results = request.values.getlist('keywords[]')
    aspect=request.values.get('selected_aspect')
    print aspect
    print keywords_results
    print len(keywords_results)
    print type(keywords_results)
    filelist = glob.glob("/home/shyamsunderramakrishnan/Desktop/enixta-machine-learning/python/lexicon_generation_optmised_code/seed_words/*.txt")
    for f in filelist:
        print 'removing files'
        os.remove(f)
    new_start_file = open("/home/shyamsunderramakrishnan/Desktop/enixta-machine-learning/python/lexicon_generation_optmised_code/seed_words/"+aspect+'.txt','w')
    new_start_file.seek(0)
    new_start_file.truncate()
    for word in keywords_results:
        new_start_file.write(word+'\n')
    new_start_file.close()
    os.getcwd()
    os.chdir('/home/shyamsunderramakrishnan/Desktop/enixta-machine-learning/python/lexicon_generation_optmised_code/')
    os.system('bash run.sh')
    num_lines = sum(1 for line in open('/home/shyamsunderramakrishnan/Desktop/enixta-machine-learning/python/lexicon_generation_optmised_code/saved_model/graph_lexicons/'+aspect+'.txt_lexicons.txt'))
    num_chunks=num_lines/400
    return render_template('admin-ui.html',results=num_chunks+1,selected_feature=aspect)


@app.route('/take_feedback')
def take_feedback():
    return render_template('feedback_form.html')

'''
@app.route('/save_feedback')
def save_feedback():

    answer_1 = request.values.get('answer_1')
    answer_1extra=request.values.get('answer_1extra')
    answer_2 = request.values.get('answer_2_array')
    answer_3=request.values.get('answer_3')
    answer_3extra=request.values.get('answer_3extra')
    answer_4=request.values.get('answer_4_array')
    #accept_string = ','.join(accept)
    #reject_string = ','.join(reject)
    answer_2_list=json.loads(answer_2)

    answer_4_list=json.loads(answer_4)
    print("Answer1/n")
    print(answer_1)
    print("Answer2/n")
    print(answer_2)
    print("Answer3/n")
    print(answer_3)
    print("Answer4/n")
    print(answer_4)
    new_comment = User_Response(1,answer_1)
    new_response=User_Response(3,answer_3)
    db.session.add(new_comment)
    db.session.add(new_response)

    if(answer_1extra is not None):
        new_record=User_Response(5,answer_1extra)
        db.session.add(new_record)
    if(answer_3extra is not None):
        new_story=User_Response(6,answer_3extra)
        db.session.add(new_story)
    for row in answer_2_list:
        new_row=User_Response(2,row)
        db.session.add(new_row)

    for row in answer_4_list:
        new_row=User_Response(4,row)
        db.session.add(new_row)

    db.session.commit()
    return 'Hello Beautiful world'
'''
'''
@app.route('/approve_frontend_reviews')
def approve_frontend_reviews():
    frontend_reviews_file = open(os.path.join(directory_path+"static/full_diverse_reviews_mix_new2_2015-05-05.txt"),'rb')

    for line_number, line in enumerate(frontend_reviews_file, start=1):
        keyword = line.strip().split('~')[0]
        tuple_row = (line.strip().split('~')[0],line.strip().split('~')[1],line.strip().split('~')[2],line.strip().split('~')[3],line.strip().split('~')[4],line.strip().split('~')[5],line.strip().split('~')[6],line.strip().split('~')[7],line.strip().split('~')[8],line.strip().split('~')[9],line.strip().split('~')[10],line.strip().split('~')[11])
        #if (tuple_row[11]=='1'):
        only_displayed_reviews.append(tuple_row)
    print (len(only_displayed_reviews))
    num_chunks=len(only_displayed_reviews)/400
    return render_template('approve_front_end_review.html',results=num_chunks+1)
'''



@app.route('/approve_frontend_reviews',methods=['GET', 'POST'])
def approve_frontend_reviews():

    print (len(df3))
    num_chunks=len(df3)/400
    return render_template('approve_front_end_review.html',results=num_chunks+1)


@app.route("/_show_reviews_for_section")
def _show_reviews_for_section():

    section_number = int(request.values.get("section_number"))
    print 'Section number is' + str(section_number)
    start_line=1+(section_number-1)*400
    print 'Start Line is ' + str (start_line)
    print 'DF3 length is ' + str(len(df3))
    df4=df3
    df4=df4.reset_index()
    df4['sentiment']=df4['sentiment'].replace(['most-positive','most-negative'],['positive','negative'])
    df4=df4.loc[start_line-1:start_line+398,:]
    print 'Length of DF4 is ' + str(len(df4))
    options_group=''
    options_group = '<table class="table table-striped table-bordered table-hover" id="sample_2"><thead><tr><th>Phone ID</th><th>Phone Name</th><th>Review Text</th><th>Review Tag</th><th style="width=250px">Correct?</th></tr></thead><tbody>'
    for index, row in df4.iterrows():
        check_rejected=row['aspect']+'~'+row['sentiment']+'~'+row['source-review-id']
        if check_rejected not in rejected_reviews_file_dict.keys():
            text_start_index=row['text-start-index']
            text_end_index=row['text-end-index']
            review_text=row['review-text']
            sentiment = row['sentiment']
            if (text_start_index-200<0):
                snippet_starting_index = 0
            else:
                snippet_starting_index=text_start_index-200
            if(text_end_index+200>len(review_text)):
                snippet_ending_index=len(review_text)
            else:
                snippet_ending_index=text_end_index+200
            final_text=review_text[snippet_starting_index:snippet_ending_index]
            final_text_part_one=final_text[0:final_text.lower().find(row['sentiment-text'])]
            final_text_part_two=final_text[final_text.lower().find(row['sentiment-text'])+text_end_index-text_start_index:]

            if (sentiment=='positive'):
                flag_color='#E1FFEE'
            else:
                flag_color='#FFE5E5'

            options_group += '<tr class="odd gradeX"><td>'+str(to_unicode(row['common-id_x']))+'</td><td id="word-'+to_unicode(row['mobile-name'])+'">'+to_unicode(row['mobile-name'])+'</td><td style="background-color:'+flag_color+'">'+final_text_part_one +'<b style="background-color:#ff9"> '+to_unicode(row['sentiment-text'])+'&nbsp;</b>'+final_text_part_two+'</td><td>'+row['aspect']+' '+ sentiment+'</td><td><div class="radio-list"><label><input type="radio" class = "radiobutton" name="optionsRadios'+row['source-review-id']+row['sentiment']+row['aspect']+'" id="optionsRadiosCorrect'+row['source-review-id']+row['sentiment']+row['aspect']+'" value="CORRECT" checked> Correct </input></label><label><input type="radio" class = "radiobutton" name="optionsRadios'+row['source-review-id']+row['sentiment']+row['aspect']+'" id="optionsRadiosIncorrect'+row['source-review-id']+row['sentiment']+row['aspect']+'" value="INCORRECT"> Incorrect</input></label><input type="text" class = "text-reject" style="display:none" name="rejectReason'+row['source-review-id']+row['sentiment']+row['aspect']+'" id="rejectReasonID'+row['source-review-id']+row['sentiment']+row['aspect']+'" placeholder="type reason here"> </div></td></tr>'

        #options_group += '<tr class="odd gradeX"><td>'+str(row['common_id'])+'</td><td id="word-'+str(row['mobile-name'])+'">'+str(row['mobile-name'])+'</td><td style="background-color:'+flag_color+'">'+final_text_part_one +'<b style="background-color:#ff9"> '+row['sentiment-text']+'&nbsp;</b>'+final_text_part_two+'</td><td>'+row['aspect']+' '+ sentiment+'</td><td><div class="form-group"><label>Radio</label><div class="radio-list"><label><input type="radio" name="optionsRadios" id="optionsRadios1" value="option1" checked> Option 1</label><label><input type="radio" name="optionsRadios" id="optionsRadios2" value="option2"> Option 2 </label><label><input type="radio" name="optionsRadios" id="optionsRadios3" value="option3" disabled> Disabled </label></div></div></td></tr>'
    options_group += '</tbody></table>'
    return jsonify(options=options_group)


# save rejected words into a new file

@app.route('/save_new_results')
def save_new_results():

    reject = request.values.get('reject')
    print reject
    count = 0


    reject_list = json.loads(reject)
    rejected_reviews_list_file=open(os.path.join(directory_path+"static/rejected_reviews.txt"),'a')
    #print reject_list
    for word in reject_list:
        print word['review_aspect']
        #if count==0:
            #rejected_reviews_list_file.write('\n')
        word_insert=word['review_aspect']+'~'+word['review_sentiment_type']+'~'+word['review_id']
        if word_insert not in rejected_reviews_file_dict.keys():
            print word_insert
            rejected_reviews_list_file.write(word_insert+'~'+word['review_reject_reason']+'\n')
            rejected_reviews_file_dict.update({word_insert:'true'})
        count+=1
    rejected_reviews_list_file.close()
    return jsonify(results='23')


@app.route('/show_rejected_reviews',methods=['GET', 'POST'])
def show_rejected_reviews():
    rejected_reviews_file=open(os.path.join(directory_path+"static/rejected_reviews.txt"),'r+')
    list_of_records = list()

    for line in rejected_reviews_file:
        catcher_in_the_rye=line.strip().split('~')
        print len(catcher_in_the_rye)
        if (len(line.strip().split('~'))==4):
            aspect = line.strip().split('~')[0]
            sentiment = line.strip().split('~')[1]
            source_review_id=line.strip().split('~')[2]
            curator_comment=line.strip().split('~')[3]

            df5=df3[df3['aspect']==aspect]
            df5['sentiment']=df5['sentiment'].replace(['most-positive','most-negative'],['positive','negative'])
            df5=df5[df5['sentiment']==sentiment]
            df5=df5[df5['source-review-id']==source_review_id]
            if len(df5)>0:
                for index, row in df5.iterrows():
                    tuple_row=(row['common-id_x'],row['mobile-name'],row['aspect'],row['sentiment'],row['source-review-id'],curator_comment)
            #tuple_row=(df5['common_id'],df5['mobile_name'],df5['aspect'],df5['sentiment'],df5['source_review_id'],curator_comment)
                    list_of_records.append(tuple_row)

    print list_of_records
    #return "Hello - What a wonderful world"
    return render_template('rejected_reviews.html', results=list_of_records)


@app.route('/clear_rejected_review')
def clear_rejected_review():
    #This removes a review from the reject list, i.e. puts it back into the selected list
    review_line=request.values.get('review-id')
    review_line=to_str(review_line)

    print review_line
    f=open(os.path.join(directory_path,"static/rejected_reviews.txt"))
    output = []
    for line in f:
        if(len(line.strip().split('~'))==4):
            if not review_line == line.strip().split('~')[0]+'~'+line.strip().split('~')[1]+'~'+line.strip().split('~')[2]:
                output.append(line)
            else:
                print 'hello world'
                del rejected_reviews_file_dict[review_line]
    f.close()
    f = open(os.path.join(directory_path,"static/rejected_reviews.txt"), 'w')
    f.writelines(output)
    f.close()
    return jsonify(results='success')



@app.route('/show_flipkart_api')
def show_flipkart_api():
    #newbie=db
    #newbie2 = mysql.connector.connect(user='root',host="localhost",database="corasgpd_20`50626")
    #cursor =newbie2.cursor(buffered=True)
    #query = ("SELECT * from aspect_weight")
    #cursor.execute(query)
    #cursor.close()
    #newbie2.close()
    return render_template('flipkart_api.html')


@app.route('/call_api')
def call_api():
    '''
    req = urllib2.Request('https://affiliate-api.flipkart.net/affiliate/feeds/marketing40/category/v1:reh.json?expiresAt=1432938878466&sig=a268a129374d9418a4612b20cb153449')
    req.add_header('Fk-Affiliate-Id', 'marketing40')
    req.add_header('Fk-Affiliate-Token','c7dd02b4eda2432aa06a3f24bf7fa5ac')
    resp = urllib2.urlopen(req)
    content=resp.read()
    result_data = json.loads(content)
    print(type(result_data))
    print 'Next URL is '+ result_data['nextUrl']

    #jason=json.loads(resp)
    #content = resp.read().decode('utf-8')
    #print content[0]
'''
    print request.values.get('selected_option')
    category = request.values.get('selected_option')
    req = urllib2.Request('https://affiliate-api.flipkart.net/affiliate/api/marketing40.json')
    response=urllib2.urlopen(req)
    result_data=json.loads(response.read())
    print (type(result_data))
    print(result_data['apiGroups']['affiliate']['apiListings'][category]['availableVariants']['v0.1.0']['get'])
    category_specific_url=str(result_data['apiGroups']['affiliate']['apiListings'][category]['availableVariants']['v0.1.0']['get'])


    req = urllib2.Request(category_specific_url)
    req.add_header('Fk-Affiliate-Id', 'marketing40')
    req.add_header('Fk-Affiliate-Token','4a7fd5132cac4fccab1117e49a55faf6')
    resp = urllib2.urlopen(req)
    content=resp.read()
    content=str(content)
    result_data = json.loads(content)
    print(type(result_data))
    print(result_data)
    print 'Next URL is '+ result_data['nextUrl']

    return 'Hello - This is a beautiful world!'


@app.route('/add_product')
def add_product():
    return render_template('add_product.html')


@app.route('/fetch_specifications', methods=['GET','POST'])
def fetch_specifications():

    brand = ''
    model_name=''
    operating_system=''
    processor_speed=''
    gpu=''
    sim_size=''
    sim_type=''
    dimensions_size=''
    dimensions_weight=''
    display_size=''
    display_resolution=''
    display_type=''
    primary_camera=''
    secondary_camera=''
    camera_flash=''
    camera_video_recording=''
    camera_hd_recording=''
    camera_other_features=''
    storage_internal=''
    storage_expandable=''
    performance_ram=''
    battery_capacity=''
    battery_talktime_2g=''
    battery_talktime_3g=''
    battery_talktime_4g=''
    connectivity_data=''
    connectivity_data_reporter=''
    connectivity_data_has_2g=False
    connectivity_data_has_3g=False
    connectivity_data_has_4g=False
    networks_already_traversed=False
    connectivity_bluetooth=''
    connectivity_wifi=''
    connectivity_tethering=''
    connectivity_navigation_tech=''
    connectivity_DLNA=''
    connectivity_HDMI=''
    release_date=''
    source_id=''
    novelty=''
    performance_chipset=''
    performance_number_cores=''
    camera_frame_rate=''
    design_color=''
    design_body_material=''
    connectivity_networks=''
    performance_ui_os=''
    performance_cpu=''
    display_touch_features=''
    features_sensors=''
    camera_secondary_video_rate=''
    camera_secondary_frame_rate=''
    av_radio=''
    usb_connector_type=''
    usb_version=''
    usb_features=''
    connectivity_connector_type=''
    primary_video_resolution=''
    secondary_video_resolution=''
    av_audio_format=''
    av_video_format=''
    battery_type=''
    battery_features=''
    display_ppi=''
    display_screen_protection=''
    battery_standby_3g=''
    battery_standby_2g=''
    battery_standby_4g=''
    camera_sensor_type=''
    camera_sensor_model=''
    camera_sensor_size=''
    camera_pixel_size=''
    camera_aperture=''
    camera_extra_features=''
    secondary_camera_extra_features=''
    line_item_string=""
    master_list=list()
    product_id= request.values.get('product_id')
    req = urllib2.Request('http://www.devicespecifications.com/en/model/'+product_id)
    response=urllib2.urlopen(req)
    content=response.read()
    print type(content)
    soup=BeautifulSoup(content)
    all_tables_list=soup.find_all('table', attrs={'class':'model-information-table row-selection'})
    for word in all_tables_list:
        #print word
        rows = word.findAll('tr')
        for element in rows:
            element_data=element.findAll('td')
            #if (element_data[0].contents[0]=='Brand'):
                #brand=element_data[0].findNext('td').contents[0]
            master_list.append(element_data)
            #print element_data
            #print master_list
    for line in master_list:
        if line[0]:
            if line[0].contents:
                if line[0].contents[0]=='Brand':
                    brand=line[0].WARRANTY('td').contents[0]
                if line[0].contents[0]=='Model':
                    model_name=line[0].findNext('td').contents[0]
                if line[0].contents[0]=='Operating system (OS)':
                    operating_system=line[0].findNext('td').contents[1]
                if line[0].contents[0]=='CPU frequency':
                    processor_speed=line[0].findNext('td').contents[0]
                if line[0].contents[0]=='GPU':
                    gpu=line[0].findNext('td').contents[0]
                if line[0].contents[0]=='SIM card type':
                    sim_size=line[0].findNext('td').contents[1]
                if line[0].contents[0]=='Number of SIM cards':
                    sim_type=line[0].findNext('td').contents[0]
                if line[0].contents[0]=='Width' or line[0].contents[0]=='Height' or line[0].contents[0]=='Thickness':
                    if line[0].parent and line[0].parent.parent and line[0].parent.parent.previousSibling:

                        #print line[0].parent
                        #print line[0].parent.parent
                        #print line[0].parent.parent.parent
                        section_heading= line[0].parent.parent.previousSibling
                        table_heading = line[0].parent.parent.previousSibling.find('h2',attrs={'class':'header'})
                        for headings in table_heading:
                            if headings:
                                data_point_type=headings
                                print data_point_type
                                result_data = line[0].findNext('td').contents
                                for line_item in result_data:
                                    print type(line_item)
                                    if isinstance(line_item,NavigableString):
                                        line_item_string=to_str(line_item)
                                        if line_item_string.find(' mm')>0:
                                            print line_item_string.find(' mm')
                                            if data_point_type=="Design":
                                                dimensions_size+=line_item_string+' X '
                                                break
                                        #dimensions_size=line_item
                                        #break

                                print result_data
                if line[0].contents[0]=='Weight':
                    weight_container=line[0].findNext('td').contents
                    for weight_item in weight_container:
                                    print type(weight_item)
                                    if isinstance(weight_item,NavigableString):
                                        weight_item_string=to_str(weight_item)
                                        if weight_item_string.find(' g ')>0:
                                            print weight_item_string.find(' g ')
                                            dimensions_weight=weight_item_string
                                            break
                if line[0].contents[0]=='Resolution':
                    display_resolution=line[0].findNext('td').contents[0]
                if line[0].contents[0]=='Type/technology':
                    display_type=line[0].findNext('td').contents[0]
                    display_size_container=line[0].findNext('td').findNext('td').findNext('td').contents
                    for display_item in display_size_container:
                                    print type(display_item)
                                    if isinstance(display_item,NavigableString):
                                        display_item_string=to_str(display_item)
                                        if display_item.find(' in ')>0:
                                            #print weight_item_string.find(' g ')
                                            display_size=display_item_string
                                            break
                if line[0].contents[0]=='Image resolution':
                    if line[0].parent and line[0].parent.parent and line[0].parent.parent.previousSibling:

                        #print line[0].parent
                        #print line[0].parent.parent
                        #print line[0].parent.parent.parent
                        section_heading= line[0].parent.parent.previousSibling
                        table_heading = line[0].parent.parent.previousSibling.find('h2',attrs={'class':'header'})
                        for headings in table_heading:
                            if headings:
                                data_point_type=headings
                                print data_point_type
                                result_data = line[0].findNext('td').contents
                                for line_item in result_data:
                                    print type(line_item)
                                    if isinstance(line_item,NavigableString):
                                        line_item_string=to_str(line_item)
                                        if line_item_string.find(' MP')>0:
                                            print line_item_string.find(' MP')
                                            if data_point_type.lower()=="primary camera":
                                                primary_camera=line_item_string
                                                break
                                            elif data_point_type.lower() == 'secondary camera':
                                                secondary_camera=line_item_string
                                                break

                if line[0].contents[0]=='Flash type':
                    camera_flash=line[0].findNext('td').contents[0]
                if line[0].contents[0]=='Features':
                    if line[0].parent and line[0].parent.parent and line[0].parent.parent.previousSibling:

                        #print line[0].parent
                        #print line[0].parent.parent
                        #print line[0].parent.parent.parent
                        section_heading= line[0].parent.parent.previousSibling
                        table_heading = line[0].parent.parent.previousSibling.find('h2',attrs={'class':'header'})
                        for headings in table_heading:
                            if headings:
                                data_point_type=headings
                                print data_point_type
                                result_data = line[0].findNext('td').contents
                                for line_item in result_data:
                                    print type(line_item)
                                    if isinstance(line_item,NavigableString):
                                        line_item_string=to_str(line_item)
                                        if data_point_type=="Primary camera":
                                            camera_other_features+=line_item_string+' , '
                                            result_data_for_camera_extra_features = line[0].findNext('td').findNext('td').findNext('td').contents
                                            camera_extra_features=''
                                            for element in result_data_for_camera_extra_features:
                                                if isinstance(element,NavigableString):
                                                    camera_extra_features+=element
                                        elif data_point_type=='USB':
                                            usb_features=line_item_string
                                        elif data_point_type=='Battery':
                                            battery_features+=line_item_string+ " , "
                if line[0].contents[0]=='Storage':
                    storage_internal=line[0].findNext('td').contents[1]
                    try:
                        if not line[0].findNext('td').contents[5] is None:
                            storage_internal=storage_internal+' / '+line[0].findNext('td').contents[5]
                        if not line[0].findNext('td').contents[9] is None:
                            storage_internal=storage_internal+' / '+line[0].findNext('td').contents[9]
                    except IndexError as err:
                        print 'indexError'
                if line[0].contents[0]=='RAM capacity':
                    performance_ram=line[0].findNext('td').contents[1]
                if line[0].contents[0]=='Capacity':
                    battery_capacity=line[0].findNext('td').contents[0]
                if line[0].contents[0]=='3G talk time':
                    talk_time_container=line[0].findNext('td').contents
                    for talk_time in talk_time_container:
                                    print type(talk_time)
                                    if isinstance(talk_time,NavigableString):
                                        talk_time_string=to_str(talk_time)
                                        if talk_time_string.find(' hours ')>0:
                                            print talk_time_string.find(' hours ')
                                            battery_talktime_3g=talk_time_string
                                            break
                    connectivity_data_has_3g=True
                if line[0].contents[0]=='2G talk time':
                    talk_time_container=line[0].findNext('td').contents
                    for talk_time in talk_time_container:
                                    print type(talk_time)
                                    if isinstance(talk_time,NavigableString):
                                        talk_time_string=to_str(talk_time)
                                        if talk_time_string.find(' hours ')>0:
                                            print talk_time_string.find(' hours ')
                                            battery_talktime_2g=talk_time_string
                                            #battery_talktime_2g=talk_time_string
                                            break
                    connectivity_data_has_2g=True
                if line[0].contents[0]=='4G talk time':
                    talk_time_container=line[0].findNext('td').contents
                    for talk_time in talk_time_container:
                                    print type(talk_time)
                                    if isinstance(talk_time,NavigableString):
                                        talk_time_string=to_str(talk_time)
                                        if talk_time_string.find(' hours ')>0:
                                            print talk_time_string.find(' hours ')
                                            battery_talktime_4g=talk_time_string
                                            break
                    connectivity_data_has_4g=True
                if connectivity_data_has_2g==True:
                    connectivity_data+='2G'
                if connectivity_data_has_3g==True:
                    connectivity_data+=" /3G "
                if connectivity_data_has_4g==True:
                    connectivity_data+=" /4g"


                if line[0].contents[0]=='3G stand-by time':
                    talk_time_container=line[0].findNext('td').contents
                    for talk_time in talk_time_container:
                                    print type(talk_time)
                                    if isinstance(talk_time,NavigableString):
                                        talk_time_string=to_str(talk_time)
                                        if talk_time_string.find(' h')>0:
                                            print talk_time_string.find(' h')
                                            battery_standby_3g=talk_time_string
                                            break
                if line[0].contents[0]=='4G stand-by time':
                    talk_time_container=line[0].findNext('td').contents
                    for talk_time in talk_time_container:
                                    print type(talk_time)
                                    if isinstance(talk_time,NavigableString):
                                        talk_time_string=to_str(talk_time)
                                        if talk_time_string.find(' h')>0:
                                            print talk_time_string.find(' h')
                                            battery_standby_4g=talk_time_string
                                            break


                if line[0].contents[0]=='2G stand-by time':
                    talk_time_container=line[0].findNext('td').contents
                    for talk_time in talk_time_container:
                                    print type(talk_time)
                                    if isinstance(talk_time,NavigableString):
                                        talk_time_string=to_str(talk_time)
                                        if talk_time_string.find(' hours ')>0:
                                            print talk_time_string.find(' hours ')
                                            battery_standby_2g=talk_time_string
                                            break

                if line[0].contents[0]=='Version':
                    if line[0].parent and line[0].parent.parent and line[0].parent.parent.previousSibling:

                        #print line[0].parent
                        #print line[0].parent.parent
                        #print line[0].parent.parent.parent
                        section_heading= line[0].parent.parent.previousSibling
                        table_heading = line[0].parent.parent.previousSibling.find('h2',attrs={'class':'header'})
                        for headings in table_heading:
                            if headings:
                                data_point_type=headings
                                print data_point_type
                                result_data = line[0].findNext('td').contents
                                for line_item in result_data:
                                    print type(line_item)
                                    if isinstance(line_item,NavigableString):
                                        line_item_string=to_str(line_item)
                                        if data_point_type=="Bluetooth":
                                            connectivity_bluetooth=line_item_string
                                        elif data_point_type=="USB":
                                            usb_version=line_item_string
                if line[0].contents[0]=='Wi-Fi':
                    result_data = line[0].findNext('td').contents
                    for line_item in result_data:
                        print type(line_item)
                        if isinstance(line_item,NavigableString):
                            line_item_string=to_str(line_item)
                            if line_item_string.find('802.11a')>0:
                                connectivity_wifi+='802.11a'
                            if line_item_string.find('802.11b')>0:
                                connectivity_wifi+=' /b '
                            if line_item_string.find('802.11g')>0:
                                connectivity_wifi+=' /g '
                            if line_item_string.find('802.11n')>0:
                                connectivity_wifi+=' /n '
                            if line_item_string.find('802.11ac')>0:
                                connectivity_wifi+=' /ac '
                            if line_item_string.find('802.11')<0:
                                connectivity_tethering+=line_item_string + " / "

                if line[0].contents[0]=='Tracking/Positioning':
                    result_data = line[0].findNext('td').contents
                    for line_item in result_data:
                        print type(line_item)
                        if isinstance(line_item,NavigableString):
                            line_item_string=to_str(line_item)
                            connectivity_navigation_tech+=line_item_string + " / "

                if line[0].contents[0]=='Connectivity':
                    result_data = line[0].findNext('td').contents
                    for line_item in result_data:
                        print type(line_item)
                        if isinstance(line_item,NavigableString):
                            line_item_string=to_str(line_item)
                            connectivity_connector_type+=line_item_string + " / "

                if line[0].contents[0]=='SoC':
                    performance_chipset=line[0].findNext('td').contents[0]

                if line[0].contents[0]=='CPU cores':
                    performance_number_cores=line[0].findNext('td').contents[0]

                if line[0].contents[0]=='Video FPS':
                    if line[0].parent and line[0].parent.parent and line[0].parent.parent.previousSibling:

                        #print line[0].parent
                        #print line[0].parent.parent
                        #print line[0].parent.parent.parent
                        section_heading= line[0].parent.parent.previousSibling
                        table_heading = line[0].parent.parent.previousSibling.find('h2',attrs={'class':'header'})
                        for headings in table_heading:
                            if headings:
                                data_point_type=headings
                                print data_point_type
                                result_data = line[0].findNext('td').contents
                                for line_item in result_data:
                                    print type(line_item)
                                    if isinstance(line_item,NavigableString):
                                        line_item_string=to_str(line_item)
                                        if data_point_type.lower()=="primary camera":
                                            camera_frame_rate=line_item_string
                                            break
                                        elif data_point_type.lower()=="secondary camera":
                                            camera_secondary_frame_rate=line_item_string
                                            secondary_camera_extra_features_set = line[0].findNext('td').findNext('td').findNext('td').contents
                                            secondary_camera_extra_features=''
                                            for element in secondary_camera_extra_features_set:

                                                if isinstance(element,NavigableString):
                                                    secondary_camera_extra_features+=element

                                            break

                if line[0].contents[0]=='Colors':
                    result_data = line[0].findNext('td').contents
                    for line_item in result_data:
                        print type(line_item)
                        if isinstance(line_item,NavigableString):
                            line_item_string=to_str(line_item)
                            design_color+=line_item_string + " / "

                if line[0].contents[0]=='Body materials':
                    result_data = line[0].findNext('td').contents
                    for line_item in result_data:
                        print type(line_item)
                        if isinstance(line_item,NavigableString):
                            line_item_string=to_str(line_item)
                            design_body_material+=line_item_string + " / "



                if line[0].parent and line[0].parent.parent and line[0].parent.parent.previousSibling:
                    table_heading = line[0].parent.parent.previousSibling.find('h2',attrs={'class':'header'})
                    for headings in table_heading:
                        if headings:
                            data_point_type=headings
                            print data_point_type
                            if data_point_type=='Networks':
                                if networks_already_traversed==False:
                                    networks_already_traversed=True
                                    new_result_set_data=table_heading.findNext('table')
                                    new_table_rows_list=new_result_set_data.findAll('tr')

                                    for table_row in new_table_rows_list:

                                        table_dee=table_row.find('td')
                                        for individual_stuff in table_dee:
                                            if isinstance(individual_stuff,NavigableString):
                                                connectivity_networks+=individual_stuff+ ' / '
                                                break

                if line[0].contents[0]=='User interface (UI)':
                    performance_ui_os=line[0].findNext('td').contents[0]

                if line[0].contents[0]=='CPU':
                    performance_cpu=line[0].findNext('td').contents[0]

                if line[0].contents[0]=='Other features':
                    result_data = line[0].findNext('td').contents
                    for line_item in result_data:
                        print type(line_item)
                        if isinstance(line_item,NavigableString):
                            line_item_string=to_str(line_item)
                            display_touch_features+=line_item_string + " / "
                    display_features_set=line[0].nextSibling.findNext('td').nextSibling
                    for line_item in display_features_set:
                        if isinstance(line_item,NavigableString):
                            line_item_string=to_str(line_item)
                            display_touch_features+=line_item_string + " / "


                if line[0].contents[0]=='Sensors':
                    result_data = line[0].findNext('td').contents
                    for line_item in result_data:
                        print type(line_item)
                        if isinstance(line_item,NavigableString):
                            line_item_string=to_str(line_item)
                            features_sensors+=line_item_string + " / "

                if line[0].contents[0]=='Video resolution':
                    if line[0].parent and line[0].parent.parent and line[0].parent.parent.previousSibling:

                        #print line[0].parent
                        #print line[0].parent.parent
                        #print line[0].parent.parent.parent
                        section_heading= line[0].parent.parent.previousSibling
                        table_heading = line[0].parent.parent.previousSibling.find('h2',attrs={'class':'header'})
                        for headings in table_heading:
                            if headings:
                                data_point_type=headings
                                print data_point_type
                                result_data = line[0].findNext('td').contents
                                for line_item in result_data:
                                    print type(line_item)
                                    if isinstance(line_item,NavigableString):
                                        line_item_string=to_str(line_item)
                                        if line_item_string.find(' pixels')>0:
                                            print line_item_string.find(' pixels')
                                            if data_point_type.lower()=="primary camera":
                                                primary_video_resolution=line_item_string
                                                break
                                            elif data_point_type.lower() == 'secondary camera':
                                                secondary_video_resolution=line_item_string
                                                break

                if line[0].contents[0]=='Radio':
                    av_radio=line[0].findNext('td').contents[0]

                if line[0].contents[0]=='Connector type':
                    usb_connector_type=line[0].findNext('td').contents[0]

                if line[0].contents[0]=='Audio file formats/codecs':
                    result_data = line[0].findNext('td').contents
                    for line_item in result_data:
                        print type(line_item)
                        if isinstance(line_item,NavigableString):
                            line_item_string=to_str(line_item)
                            av_audio_format+=line_item_string + " / "

                if line[0].contents[0]=='Video file formats/codecs':
                    result_data = line[0].findNext('td').contents
                    for line_item in result_data:
                        print type(line_item)
                        if isinstance(line_item,NavigableString):
                            line_item_string=to_str(line_item)
                            av_video_format+=line_item_string + " / "

                if line[0].contents[0]=='Type':
                    battery_type=line[0].findNext('td').contents[0]

                if line[0].contents[0]=='Pixel density':
                    weight_container=line[0].findNext('td').contents
                    for weight_item in weight_container:
                                    print type(weight_item)
                                    if isinstance(weight_item,NavigableString):
                                        weight_item_string=to_str(weight_item)
                                        if weight_item_string.find(' ppi ')>0:
                                            print weight_item_string.find(' ppi ')
                                            display_ppi=weight_item_string
                                            break

                if line[0].contents[0]=='Sensor model':
                    camera_sensor_model=line[0].findNext('td').contents[0]

                if line[0].contents[0]=='Sensor type':
                    camera_sensor_type=line[0].findNext('td').contents[0]

                if line[0].contents[0]=='Aperture':
                    camera_aperture=line[0].findNext('td').contents[0]

                if line[0].contents[0]=='Sensor size':
                    weight_container=line[0].findNext('td').contents
                    for weight_item in weight_container:
                                    print type(weight_item)
                                    if isinstance(weight_item,NavigableString):
                                        weight_item_string=to_str(weight_item)
                                        if weight_item_string.find(' mm ')>0:
                                            print weight_item_string.find(' mm ')
                                            camera_sensor_size=weight_item_string
                                        if weight_item_string.find(" in ")>0:
                                            camera_sensor_size+=weight_item_string
                                            break

                if line[0].contents[0]=='Pixel size':
                    weight_container=line[0].findNext('td').contents
                    for weight_item in weight_container:
                                    print type(weight_item)
                                    if isinstance(weight_item,NavigableString):
                                        weight_item_string=to_str(weight_item)
                                        if weight_item_string.find(' µm ')>0:
                                            print weight_item_string.find(' µm ')
                                            camera_pixel_size=weight_item_string[:-4]+" micrometers "
                                        if weight_item_string.find(" mm ")>0:
                                            camera_pixel_size+=weight_item_string
                                            break
                #User interface (UI)
                if line[0].contents[0]=='HDMI':
                    weight_container=line[0].findNext('td').contents
                    for weight_item in weight_container:
                                    print type(weight_item)
                                    if isinstance(weight_item,NavigableString):
                                        weight_item_string=to_str(weight_item)
                                        connectivity_HDMI=weight_item_string
                                        break
                if line[0].contents[0]=='User interface (UI)':
                    weight_container=line[0].findNext('td').contents
                    for weight_item in weight_container:
                                    print type(weight_item)
                                    if isinstance(weight_item,NavigableString):
                                        weight_item_string=to_str(weight_item)
                                        performance_ui_os=weight_item_string
                                        break

                print connectivity_networks













                                        #dimensions_size=line_item
                                        #break






                    #print dimensions_size
    if (connectivity_wifi==''):
        connectivity_div=soup.find('div', attrs={"id":'model-brief-specifications'})
        for item in connectivity_div.contents:
            if type(item) is Tag:
                if len(item.contents)>0:
                    if(item.contents[0]=='Wi-Fi'):
                        connectivity_wifi=item.next_sibling
                        break

    print brand
    print model_name
    print dimensions_weight
    dimensions_size
    dimension_size = dimensions_size[:-2]
    print dimensions_size
    print primary_camera
    print secondary_camera
    print display_resolution
    print display_type
    if connectivity_data.find('2G')>0:
        connectivity_data_reporter+="2G"
    if connectivity_data.find("3G")>0:
        connectivity_data_reporter+="3G"
    if connectivity_data.find("4G")>0:
        connectivity_data_reporter+="4G"
    connectivity_data_reporter.replace("G","G/ ")
    #connectivity_data_reporter=connectivity_data_reporter[:-2]

    with open(os.path.join(directory_path+"static/device_specs.csv"),"r+") as outcsv:
        writer = csv.writer(outcsv)
        writer.writerow(["Brand", "Model Name","Price", "Operating System", "CPU Frequency", "GPU","SIM Size","SIM Type","Dimensions Size","","",
                         "Dimensions Weight","Display Size","Display Resolution","Display Type","Primary Camera","Secondary Camera",
                         "Camera Flash","Camera Video Recording","Camera HD Recording","Camera Other Features","Internal Storage","Expandable Storage",
                         "Performance RAM","Battery Capacity","Battery 2G Talktime","Battery 3G Talktime","Battery 4G Talktime","Connectivity Data",
                         "Connectivity Bluetooth","Connectivity Wifi", "Connectivity Tethering","Tracking/Positioning","HDMI",
                         "Release Date","","","Performance Chipset","Performance Cores",
                         "Camera Frame rate","Design Color","Design Body Material","Connectivity networks","","","","","","Performance UI Os","Performance CPU",
                         "Soc Other features","Features Sensors","Camera Secondary Video Rate","Camera Secondary Frame Rate","AV Radio",
                         "USB Connector Type","USB Version","USB Features","Connectivity Connector Type","AV Audio Format",
                         "AV Video Format","Battery Type","Battery Features","Display PPI","Display Screen Protection","Battery 2g Standby",
                         "Battery 3g standby","Battery 4G standby",
                         "Camera Sensor Model","Camera Sensor Type","Camera Sensor Size","Camera Pixel size","Camera Aperture",
                         "Display Extra features","Primary Camera Extra","Secondary Camera Extra"])
        writer.writerow([brand,model_name,"",operating_system,processor_speed,gpu,sim_size,sim_type,dimensions_size,"","",dimensions_weight,display_size,
                         display_resolution,display_type,primary_camera,secondary_camera,camera_flash,primary_video_resolution,camera_hd_recording,
                         camera_other_features,storage_internal,storage_expandable,performance_ram,battery_capacity,battery_talktime_2g,battery_talktime_3g,battery_talktime_4g,
                         connectivity_data_reporter,connectivity_bluetooth,connectivity_wifi,connectivity_tethering,connectivity_navigation_tech,connectivity_HDMI,
                         release_date,"","",performance_chipset,performance_number_cores,camera_frame_rate,design_color,design_body_material,connectivity_networks,"","","","","",
                         performance_ui_os,performance_cpu,display_touch_features,features_sensors,secondary_video_resolution,camera_secondary_frame_rate,
                         av_radio,usb_connector_type,usb_version,usb_features,connectivity_connector_type,av_audio_format,
                         av_video_format,battery_type,battery_features,display_ppi,display_touch_features,battery_standby_2g,battery_standby_3g,
                         battery_standby_4g,camera_sensor_model,
                         camera_sensor_type,camera_sensor_size,camera_pixel_size,camera_aperture,display_touch_features,to_str(camera_extra_features),secondary_camera_extra_features])


    return 'Halleluia'


@app.route('/show_bogus_prices')
def show_bogus_prices():
    list_of_rows = list()
    new_connection = mysql.connector.connect(user='root',host="localhost",database="corasgpd_20`50626")
    cursor =new_connection.cursor(buffered=True)
    query = ("select p.id,p.product_name,pd.maxprice,pd.minprice from product p inner join product_detail pd where p.id = pd.product_id and (pd.minprice<2500 or pd.maxprice<2500)")
    cursor.execute(query)
    for (product_id,product_name,minprice,maxprice) in cursor:
        tuple_row = (product_id,product_name,minprice,maxprice)
        list_of_rows.append(tuple_row)
    cursor.close()
    new_connection.close()
    return render_template('show_bogus_prices.html',results=list_of_rows)


@app.route('/show_clusters_page')
def show_clusters():
    return render_template('cluster_naming.html')


@app.route('/display_clusters')
def display_clusters():
    print 'Hollow World'
    new_json_data_file = open(os.path.join(directory_path+"static/document_clusters.json"),"r")
    options=""
    data=json.loads(new_json_data_file.read())
    print data.keys()
    for key, value in data.iteritems():
        options+= '{ "id" : "'+key+'", "parent" : "#", "text" : "'+key+'" },'
        if isinstance(value,dict):
            for inner_key, inner_values in value.iteritems():
                #print inner_key
                #print inner_value
                #print to_str(key)+to_str(inner_key)+''.join(inner_values)
                options+= '{ "id" : "'+inner_key+'", "parent" : "'+key+'", "text" : "'+inner_key+'" },'
                for inner_value in inner_values:
                    options+= '{ "id" : "'+inner_value+'", "parent" : "'+inner_key+'", "text" : "'+inner_value+'" },'
    return jsonify(results='254')


@app.route('/get_dummy_json')
def get_dummy_json():
    print 'Hollow World'
    print 'Gella world'
    new_json_data_file = open(os.path.join(directory_path+"static/document_clusters_test.json"),"r")
    options="["
    data=json.loads(new_json_data_file.read())
    print data.keys()
    for key, value in data.iteritems():
        options+= '{ "id" : "'+key+'", "parent" : "#", "text" : "'+key+'" },'
        if isinstance(value,dict):
            for inner_key, inner_values in value.iteritems():
                #print inner_key
                #print inner_value
                #print to_str(key)+to_str(inner_key)+''.join(inner_values)
                options+= '{ "id" : "'+inner_key+'", "parent" : "'+key+'", "text" : "'+inner_key+'" },'
                for inner_value in inner_values:
                    options+= '{ "id" : "'+inner_value+'", "parent" : "'+inner_key+'", "text" : "'+inner_value+'" },'
    options=options[:-1]
    options+="]"
    print "options = " + options
    return jsonify(results=options)


@app.route('/get_ajax_json_jstree',methods=['GET', 'POST'])
def get_ajax_json_jstree():
    #return jsonify(results='[{"id":1,"text":"Root node","children":[{"id":2,"text":"Child node 1","children":true},{"id":3,"text":"Child node 2"}]}]')

    appi = request
    id = request.args.get('id')
    response_data={}
    response_data['id']=1
    response_data['text']='Root Node'
    response_data['children']=[{"id":2,"text":"Child node 1","children":True},{"id":3,"text":"Child node 2"}]
    response_list=[response_data]
    result = json.dumps([{  "id":1,"text":"Root node","children":[{"id":2,"text":"Child node 1","children":True}, {"id":3,"text":"Child node 2"}]}])



    if id=="#":
        response = Response(response=result,status=200,content_type="application/json")
        return response
    elif id=="2":
        result=json.dumps(["Child node 3","Child node 4"])
        return Response(response=result,status=200,content_type="application/json")


@app.route('/show_review_clusters_page')
def show_review_clusters_page():
    review_categories=[]
    reviews_json_data_file= open(treemap_clusters_full_file_name,"r")
    data=json.loads(reviews_json_data_file.read())
    for key in data.keys():
        review_categories.append(key)
    return render_template('show_review_clusters.html',results=review_categories)


@app.route('/show_review_clusters',methods=['GET', 'POST'])
def show_review_clusters():
    appi = request
    aspect_senti_combo = request.values.get('keywords')
    print aspect_senti_combo
    list_of_review_tuples = []
    if request.files['userfile'].filename =='':
        reviews_cluster_data_file = open(treemap_clusters_full_file_name,"r")
        data=json.loads(reviews_cluster_data_file.read())
        print data.keys()
        for key, value in data.iteritems():
            if key == aspect_senti_combo:
                if isinstance(value,dict):
                    for inner_key, inner_values in value.iteritems():
                        #print inner_key
                        #print inner_value
                        #print to_str(key)+to_str(inner_key)+''.join(inner_values)
                        for inner_value in inner_values:
                            tuple_row = (inner_key,inner_value,"",key)
                            list_of_review_tuples.append(tuple_row)
        #print list_of_review_tuples
        return jsonify(results=list_of_review_tuples)
    else:
        user_file=request.files['userfile']
        reader = csv.reader(user_file)
        header=next(reader)
        for row in reader:
            tuple_row = (row[0],row[1],row[2],row[3])
            list_of_review_tuples.append(tuple_row)
        return jsonify(results=list_of_review_tuples)

@app.route('/cluster_json_csv')
def cluster_json_csv():
    #print aspect_senti_combo
    list_of_review_tuples = []

    reviews_cluster_data_file = open(treemap_clusters_full_file_name,"r")
    data=json.loads(reviews_cluster_data_file.read())
    print data.keys()
    for key, value in data.iteritems():
        if isinstance(value,dict):
            for inner_key, inner_values in value.iteritems():
                    #print inner_key
                    #print inner_value
                    #print to_str(key)+to_str(inner_key)+''.join(inner_values)
                for inner_value in inner_values:
                    tuple_row = (inner_key,inner_value,"",key)
                    list_of_review_tuples.append(tuple_row)
    #print list_of_review_tuples
    clusters_csv_output_file=open(os.path.join(directory_path+"clusters_outputs.csv"),'w')
    csv_out=unicodecsv.writer(clusters_csv_output_file,delimiter='~')
    csv_out.writerow(["Cluster name",'cluster entry',"","senti-aspect combo"])
    for line in list_of_review_tuples:
        csv_out.writerow(line)
    return "I wanna go home"


@app.route('/show_advanced_tables')
def show_advanced_tables():
    return render_template('table_advanced_test.html')



@app.route('/show_treemap_viz')
def show_treemap_viz():
        reviews_cluster_data_file = open("/Users/ShyamR/Desktop/internal_dashboard/Microblog/static/clusters_of_similar_phones.json","r")
        data=json.loads(reviews_cluster_data_file.read())
        for line in data:
            l2=[]
            for word in line:
                if not line[word] is None:
                    l2.append(line[word])
            if(len(l2)>1):
                l3=list(itertools.permutations(l2, 2))
                for element in l3:
                    print element
        return render_template('table_advanced_test.html')


@app.route('/phones_permutations')
def show_phones_permutations():
    reviews_cluster_data_file = open("/Users/ShyamR/Desktop/internal_dashboard/Microblog/static/best_laptops.json","r")
    results_file=open("/Users/ShyamR/Desktop/internal_dashboard/Microblog/static/best_laptops.txt","r+")
    data=json.loads(reviews_cluster_data_file.read())
    l2=[]
    for word in data:
        l2.append(word)
    l3=list(itertools.combinations(l2,2))
    for element in l3:
        results_file.write(str(element)+"\n")
    return "Hello World"



@app.route('/show_variants_selector_page')
def show_variants_selector_page():
    phone_variants_file = open(os.path.join(directory_path+"static/product_source_map_mod.csv"),'r')
    reader = csv.reader(phone_variants_file)
    list_of_phone_tuples=[]
    header=next(reader)
    list_of_sources={'1':'flipkart','2':'phone arena','3':'ambest_phones_new_arrivals_list.jsonl','5':'naaptol','6':'bestbuy','7':'youtube','8':'deviceSpec'}
    for row in reader:
        tuple_row = (to_unicode(row[1]),to_unicode(list_of_sources[row[2]]),to_unicode(row[3]),to_unicode(row[4]),to_unicode(row[9]))
        list_of_phone_tuples.append(tuple_row)

    return render_template('show_product_variants.html',results=list_of_phone_tuples)


@app.route("/measure")
def show_measure():
    i=0
    file=open("/Users/ShyamR/Desktop/internal_dashboard/Microblog/static/sada_phones_pairs.txt","r+")
    for line in file:
        i=i+1
        print i
    return "Sad world"


@app.route('/cheat_sheet')
def cheat_sheet():
    cluster = Cluster(['127.0.0.1'])
    #client = SimpleClient()
    cassandra_session = cluster.connect('mykeyspace')
    list_of_cassandra_rows=list()
    master_rows = cassandra_session.execute("select * from users")
    #first_row=master_rows[0]
    #print first_row
    tuple_row=('user_id','fname','lname',)
    list_of_cassandra_rows.append(tuple_row)
    new_connection = mysql.connector.connect(user='root',host="localhost",database="corasgpd_20`50626")
    #print master_rows
    #print master_rows
    for row in master_rows:
        #print row
        cassandra_rows_dict = row.__dict__
        #print dict
        #print row[3]
        tuple_row=(cassandra_rows_dict['user_id'],cassandra_rows_dict['fname'],cassandra_rows_dict['lname'])
        list_of_cassandra_rows.append(tuple_row)
    #df_master_price_data=pd.DataFrame(master_rows)
    #print list_of_cassandra_rows
    list_of_mysql_rows=list()
    tuple_row=('user_id','fname_mysql','lname_mysql')
    list_of_mysql_rows.append(tuple_row)
    cursor =new_connection.cursor(buffered=True)
    query = ("select * from users")
    cursor.execute(query)
    #data = cursor.fetchall()
    for (user_id,fname,lname) in cursor:
        tuple_row = (user_id,fname,lname)
        #print tuple_row
        list_of_mysql_rows.append(tuple_row)
    cursor.close()
    new_connection.close()
    #print list_of_mysql_rows
    df1=pd.DataFrame.from_records(list_of_cassandra_rows,columns=['user_id','fname','lname'])
    df2=pd.DataFrame.from_records(list_of_mysql_rows,columns=['user_id','fname_mysql','lname_mysql'])
    print df1.columns
    print df2.columns
    df3=df1.merge(df2,how='outer',on='user_id')
    print df3
    return 'Hello wonderful world'


    #for row in rows:
    #    print row
    #return "Woo commerce"
@app.route('/image_scraper')
def image_scraper():
    image_urls_file = open(os.path.join(directory_path+"static/image_download_from_image_urls.csv"),'rU')
    image_data = csv.reader(image_urls_file)
    images_output_file=open(os.path.join(directory_path+"static/images_download_from_image_urls_output.csv"),'w')
    csv_out=unicodecsv.writer(images_output_file,delimiter='~')
    csv_out.writerow(['product_id','image_loc','image_type'])
    image_records_list=[]
    i =0
    for line in image_data:
        i=i+1
        if i!=1:
            folder_name=line[0]
            file_name=line[1].replace(" ","-").replace('/',"-")
            mypath="/Users/ShyamR/Desktop/images/"+str(folder_name)
            if not os.path.isdir(mypath):
                os.mkdir("/Users/ShyamR/Desktop/images/"+str(folder_name))
            os.chdir("/Users/ShyamR/Desktop/images/"+str(folder_name))
            for i in range(2,len(line)):
                if line[i] is None:
                    break
                elif line[i]!='':
                    f = open("/Users/ShyamR/Desktop/images/"+str(folder_name)+"/"+file_name+"-"+str(i-1)+".jpeg",'wb')
                    f.write(urllib2.urlopen(line[i]).read())
                    f.close()
                    if(i==2):
                        row_tuple=(line[0],str(folder_name)+"/"+file_name+"-"+str(i-1)+".jpeg","P")
                    else:
                        row_tuple=(line[0],str(folder_name)+"/"+file_name+"-"+str(i-1)+".jpeg","S")
                    image_records_list.append(row_tuple)
    for row in image_records_list:
        row_as_string = "~".join(row)
        #print row_as_string
        #print row
        csv_out.writerow(row)

    return 'alleluia'

@app.route('/video_scraper')
def video_scraper():

    DEVELOPER_KEY = "AIzaSyCNq4UR4zj4rP5M82TTMlQFoVis824HpxQ"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)
    # Yea - counter-intuitively named the video urls file as Image_Urls - any way - all it needs is product ID and productname
    video_urls_input_file = open(os.path.join(directory_path+"static/tvs_product_list.csv"),'rU')
    vide_reviews_output_file=open(os.path.join(directory_path+"static/tvs_videos.csv"),'w')
    csv_out=unicodecsv.writer(vide_reviews_output_file,delimiter='~')
    # Suprised at the square brackets below? It is required because the csv writer needs a sequence in a list. If I had just given the string, without
    # square brackets, it would have written every character in the string separately - like |p|r|o|d|u|c|t|_|i|d| instead of |product_id|
    '''
    #    delete from product_video_review;
    #set foreign_key_checks=0;
    #LOAD DATA local INFILE '/Users/ShyamR/Desktop/internal_dashboard/Microblog/static/videos.csv' INTO TABLE product_video_review FIELDS TERMINATED BY '~'	 LINES TERMINATED BY '\n' IGNORE 1 LINES (product_id, video_loc, review_title, review_date, review_text,reviewer);
    #set foreign_key_checks=1;
    '''
    csv_out.writerow(['product_id','review_title','review_date','review_text','reviewer'])

    video_data = csv.reader(video_urls_input_file)
    video_ids=''
    i =0
    for line in video_data:
        i=i+1
        if i!=1:

            search_response = youtube.search().list(q=line[1]+ " review",type="video",part="id,snippet",maxResults=10).execute()

            search_videos = []

          # Merge video ids
            for search_result in search_response.get("items", []):
                search_videos.append(search_result["id"]["videoId"])
                video_ids = ",".join(search_videos)

          # Call the videos.list method to retrieve location details for each video.

            if video_ids is not None and video_ids!='':
                video_response = youtube.videos().list(id=video_ids,part='snippet, recordingDetails').execute()

                videos = []


                # We need 5 things (dB mappings in brackets) - videoId(video_loc), title(review_title),description(review_text), publishedAt(review_date), channelTitle(reviewer)
              # Add each result to the list, and then display the list of matching videos.
                for video_result in video_response.get("items", []):
                    #print video_result['snippet']
                    #print video_result['id']
                    # Taking care to remove extra tabs, extra new line characters etc within the information fields.
                    # Also taking care to have a new line character at the end of the last field.
                    # We are going to use tilde (~) as the delimiter - so we are making sure that none of the data has any tilde signs
                    # (If any field in our data had a tilde sign, the tilde sign would mistakenly be construed as the end of that field,
                    # and it would needlessly start a new field. E.g. - say Review Text (which is one field) has the value "ABD~asd~asd".
                    # Then in that case, the value of Review Text (one field) is the one string ABD~asd~asd.
                    # However, the delimiter if used as tilde, will mistakenly consider ~ as the end of that field, and
                    # therefore, create three fields ABD, asd and asd in place of a single field.
                    # All tilde signs are replaced with @. This will make sure the CSV importer doesn't get confused.
                    '''
                    LOAD DATA local INFILE '/Users/ShyamR/Desktop/internal_dashboard/Microblog/static/videos.csv' INTO TABLE product_video_review FIELDS TERMINATED BY '~'	 LINES TERMINATED BY '\n' IGNORE 1 LINES (product_id, video_loc, review_title, review_date, review_text,reviewer);

                    '''
                    # Not required to add \n at the end of the last element. Write row takes care of it automatically. Infact, if you
                    # add \n, the import command will insert one extra empty row for each record
                    # Evil hack to make sure the stupid CSV writer is not confused. It gets confused when it sees a comma, while writing,
                    # even if you have properly informed the moronic CSV writer by entering each column separately. The hack is to replace
                    #commas by ^ symbol.
                    tuple_row=(to_unicode(line[0]),to_unicode(str(video_result['id'])),
                               to_unicode(video_result["snippet"]["title"].replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^")),
                               to_unicode(video_result['snippet']['publishedAt'].replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace("'",'').replace(",","^")),
                               to_unicode(video_result['snippet']['description'].replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace("'",'').replace(",","^")),
                               to_unicode(video_result['snippet']['channelTitle'].replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace("'",'').replace(",","^")))
                    videos.append(tuple_row)

                #print "Videos:\n", "\n".join(videos), "\n"



                    for row in videos:
                        row_as_string = "~".join(row)
                        print row_as_string
                        print row
                        csv_out.writerow(row)


    return 'Yay!'


@app.route('/greater_goal')
def greater_goal():
    list_of_rows = list()
    new_connection = mysql.connector.connect(user='root',host="localhost",database="corasgpd_20160104")
    cursor =new_connection.cursor(buffered=True)
    query = ("select product.id, product.product_name, ifnull(product_summ.summ_text1,''),ifnull(product_summ.summ_text2,''), ifnull(product_summ.pros_oneliner1,''),ifnull(product_summ.pros_oneliner2,''),ifnull(product_summ.pros_oneliner3,''), ifnull(product_summ.pros_oneliner4,''),ifnull(product_summ.pros_oneliner5,''),ifnull(product_summ.cons_oneliner1,''), ifnull(product_summ.cons_oneliner2,''),ifnull(product_summ.cons_oneliner3,''),ifnull(product_summ.cons_oneliner4,''), ifnull(product_summ.cons_oneliner5,'') from product left join product_summ on product.id = product_summ.product_id;")
    cursor.execute(query)
    for (id,product_name,summ_text1,summ_text2,pros_oneliner1,pros_oneliner2,pros_oneliner3,pros_oneliner4,pros_oneliner5,cons_oneliner1,cons_oneliner2,cons_oneliner3,cons_oneliner4,cons_oneliner5) in cursor:
        tuple_row = (id,product_name,summ_text1,summ_text2,pros_oneliner1,pros_oneliner2,pros_oneliner3,pros_oneliner4,pros_oneliner5,cons_oneliner1,cons_oneliner2,cons_oneliner3,cons_oneliner4,cons_oneliner5)
        list_of_rows.append(tuple_row)
    cursor.close()
    new_connection.close()

    return render_template("product_summary.html",results=list_of_rows)


@app.route('/submit_summary')
def submit_summary():
    summ_text1=request.values.get("summ_text1")
    summ_text2=request.values.get("summ_text2")
    pros_oneliner1 =request.values.get("pros_oneliner1")
    pros_oneliner2=request.values.get("pros_oneliner2")
    pros_oneliner3=request.values.get("pros_oneliner3")
    pros_oneliner4= request.values.get("pros_oneliner4")
    pros_oneliner5= request.values.get("pros_oneliner5")
    cons_oneliner1= request.values.get("cons_oneliner1")
    cons_oneliner2= request.values.get("cons_oneliner2")
    cons_oneliner3= request.values.get("cons_oneliner3")
    cons_oneliner4= request.values.get("cons_oneliner4")
    cons_oneliner5= request.values.get("cons_oneliner5")
    chosen_product_id=request.values.get("product_id")
    new_connection = mysql.connector.connect(user='root',host="localhost",database="corasgpd_20160104")
    cursor =new_connection.cursor(buffered=True)
    cursor2=new_connection.cursor(buffered=True)
    record_checker=False
    query=("select product_id from product_summ where product_id =%s")
    cursor.execute (query,(chosen_product_id,))
    for product_id in cursor:
        record_checker=True
        print product_id

    print 'beautiful day'
    if record_checker is True:
        #Update statement
        query="UPDATE product_summ set summ_text1 = %s, summ_text2 = %s, pros_oneliner1 = %s,pros_oneliner2 = %s, pros_oneliner3 = %s,pros_oneliner4 = %s,pros_oneliner5 = %s,cons_oneliner1 = %s,cons_oneliner2 = %s, cons_oneliner3 = %s, cons_oneliner4 = %s, cons_oneliner5 = %s where product_id = %s"
        cursor.execute(query,(summ_text1,summ_text2,pros_oneliner1,pros_oneliner2,pros_oneliner3,pros_oneliner4,pros_oneliner5,cons_oneliner1,cons_oneliner2,cons_oneliner3,cons_oneliner4,cons_oneliner5,int(chosen_product_id)))
    else:
        #insert statement
        query="insert into product_summ(product_id,summ_text1,summ_text2,pros_oneliner1,pros_oneliner2,pros_oneliner3,pros_oneliner4,pros_oneliner5,cons_oneliner1,cons_oneliner2,cons_oneliner3,cons_oneliner4,cons_oneliner5,status) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(query,(int(chosen_product_id),summ_text1,summ_text2,pros_oneliner1,pros_oneliner2,pros_oneliner3,pros_oneliner4,pros_oneliner5,cons_oneliner1,cons_oneliner2,cons_oneliner3,cons_oneliner4,cons_oneliner5,'A'))
    new_connection.commit()
    return jsonify(options="results")


@app.route("/device_specs_built_in_scraper")
def device_specs_built_in_scraper():
    upcoming_file = open(os.path.join(directory_path+"static/upcoming_products_file.csv"),'rU')
    products_data = csv.reader(upcoming_file)
    device_specs=[]
    device_specs_output=open(os.path.join(directory_path+"static/device_specs.csv"),'w')
    csv_out=unicodecsv.writer(device_specs_output,delimiter='~',quoting=unicodecsv.QUOTE_ALL)
    csv_out.writerow(["Brand", "Model Name","Price", "Operating System", "CPU Frequency", "GPU","SIM Size","SIM Type","Dimensions Size","","",
                                 "Dimensions Weight","Display Size","Display Resolution","Display Type","Primary Camera","Secondary Camera",
                                "Camera Flash","Camera Video Recording","Camera HD Recording","Camera Other Features","Internal Storage","Expandable Storage",
                                 "Performance RAM","Battery Capacity","Battery 2G Talktime","Battery 3G Talktime","Battery 4G Talktime","Connectivity Data",
                                "Connectivity Bluetooth","Connectivity Wifi", "Connectivity Tethering","Tracking/Positioning","HDMI",
                                "Release Date","","","Performance Chipset","Performance Cores",
                                "Camera Frame rate","Design Color","Design Body Material","Connectivity networks","","","","","","Performance UI Os","Performance CPU",
                                "Soc Other features","Features Sensors","Camera Secondary Video Rate","Camera Secondary Frame Rate","AV Radio",
                               "USB Connector Type","USB Version","USB Features","Connectivity Connector Type","AV Audio Format",
                               "AV Video Format","Battery Type","Battery Features","Display PPI","Display Screen Protection","Battery 2g Standby",
                              "Battery 3g standby","Battery 4G standby",
                             "Camera Sensor Model","Camera Sensor Type","Camera Sensor Size","Camera Pixel size","Camera Aperture",
                                "Display Extra features","Primary Camera Extra","Secondary Camera Extra"])
    i =0
    for line in products_data:
        i=i+1
        if i!=1:
            product_url=line[2]
            if product_url !='':
                brand = ''
                model_name=''
                operating_system=''
                processor_speed=''
                gpu=''
                sim_size=''
                sim_type=''
                dimensions_size=''
                dimensions_weight=''
                display_size=''
                display_resolution=''
                display_type=''
                primary_camera=''
                secondary_camera=''
                camera_flash=''
                camera_video_recording=''
                camera_hd_recording=''
                camera_other_features=''
                storage_internal=''
                storage_expandable=''
                performance_ram=''
                battery_capacity=''
                battery_talktime_2g=''
                battery_talktime_3g=''
                battery_talktime_4g=''
                connectivity_data=''
                connectivity_data_reporter=''
                connectivity_data_has_2g=False
                connectivity_data_has_3g=False
                connectivity_data_has_4g=False
                networks_already_traversed=False
                connectivity_bluetooth=''
                connectivity_wifi=''
                connectivity_tethering=''
                connectivity_navigation_tech=''
                connectivity_DLNA=''
                connectivity_HDMI=''
                release_date=''
                source_id=''
                novelty=''
                performance_chipset=''
                performance_number_cores=''
                camera_frame_rate=''
                design_color=''
                design_body_material=''
                connectivity_networks=''
                performance_ui_os=''
                performance_cpu=''
                display_touch_features=''
                features_sensors=''
                camera_secondary_video_rate=''
                camera_secondary_frame_rate=''
                av_radio=''
                usb_connector_type=''
                usb_version=''
                usb_features=''
                connectivity_connector_type=''
                primary_video_resolution=''
                secondary_video_resolution=''
                av_audio_format=''
                av_video_format=''
                battery_type=''
                battery_features=''
                display_ppi=''
                display_screen_protection=''
                battery_standby_3g=''
                battery_standby_2g=''
                battery_standby_4g=''
                camera_sensor_type=''
                camera_sensor_model=''
                camera_sensor_size=''
                camera_pixel_size=''
                camera_aperture=''
                camera_extra_features=''
                secondary_camera_extra_features=''
                line_item_string=""
                master_list=list()
                #product_id= request.values.get('product_id')
                req = urllib2.Request(product_url)
                response=urllib2.urlopen(req)
                content=response.read()
                print type(content)
                soup=BeautifulSoup(content)
                all_tables_list=soup.find_all('table', attrs={'class':'model-information-table row-selection'})
                for word in all_tables_list:
                    #print word
                    rows = word.findAll('tr')
                    for element in rows:
                        element_data=element.findAll('td')
                        #if (element_data[0].contents[0]=='Brand'):
                            #brand=element_data[0].findNext('td').contents[0]
                        master_list.append(element_data)
                        #print element_data
                        #print master_list
                for line in master_list:
                    if line[0]:
                        if line[0].contents:
                            if line[0].contents[0]=='Brand':
                                brand=line[0].findNext('td').contents[0]
                            if line[0].contents[0]=='Model':
                                model_name=line[0].findNext('td').contents[0]
                            if line[0].contents[0]=='Operating system (OS)':
                                operating_system=line[0].findNext('td').contents[1]
                            if line[0].contents[0]=='CPU frequency':
                                processor_speed=line[0].findNext('td').contents[0]
                            if line[0].contents[0]=='GPU':
                                gpu=line[0].findNext('td').contents[0]
                            if line[0].contents[0]=='SIM card type':
                                sim_size=line[0].findNext('td').contents[1]
                            if line[0].contents[0]=='Number of SIM cards':
                                sim_type=line[0].findNext('td').contents[0]
                            if line[0].contents[0]=='Width' or line[0].contents[0]=='Height' or line[0].contents[0]=='Thickness':
                                if line[0].parent and line[0].parent.parent and line[0].parent.parent.previousSibling:

                                    #print line[0].parent
                                    #print line[0].parent.parent
                                    #print line[0].parent.parent.parent
                                    section_heading= line[0].parent.parent.previousSibling
                                    table_heading = line[0].parent.parent.previousSibling.find('h2',attrs={'class':'header'})
                                    for headings in table_heading:
                                        if headings:
                                            data_point_type=headings
                                            print data_point_type
                                            result_data = line[0].findNext('td').contents
                                            for line_item in result_data:
                                                print type(line_item)
                                                if isinstance(line_item,NavigableString):
                                                    line_item_string=to_str(line_item)
                                                    if line_item_string.find(' mm')>0:
                                                        print line_item_string.find(' mm')
                                                        if data_point_type=="Design":
                                                            dimensions_size+=line_item_string+' X '
                                                            break
                                                    #dimensions_size=line_item
                                                    #break

                                            print result_data
                            if line[0].contents[0]=='Weight':
                                weight_container=line[0].findNext('td').contents
                                for weight_item in weight_container:
                                                print type(weight_item)
                                                if isinstance(weight_item,NavigableString):
                                                    weight_item_string=to_str(weight_item)
                                                    if weight_item_string.find(' g ')>0:
                                                        print weight_item_string.find(' g ')
                                                        dimensions_weight=weight_item_string
                                                        break
                            if line[0].contents[0]=='Resolution':
                                display_resolution=line[0].findNext('td').contents[0]
                            if line[0].contents[0]=='Type/technology':
                                display_type=line[0].findNext('td').contents[0]
                                display_size_container=line[0].findNext('td').findNext('td').findNext('td').contents
                                for display_item in display_size_container:
                                                print type(display_item)
                                                if isinstance(display_item,NavigableString):
                                                    display_item_string=to_str(display_item)
                                                    if display_item.find(' in ')>0:
                                                        #print weight_item_string.find(' g ')
                                                        display_size=display_item_string
                                                        break
                            if line[0].contents[0]=='Image resolution':
                                if line[0].parent and line[0].parent.parent and line[0].parent.parent.previousSibling:

                                    #print line[0].parent
                                    #print line[0].parent.parent
                                    #print line[0].parent.parent.parent
                                    section_heading= line[0].parent.parent.previousSibling
                                    table_heading = line[0].parent.parent.previousSibling.find('h2',attrs={'class':'header'})
                                    for headings in table_heading:
                                        if headings:
                                            data_point_type=headings
                                            print data_point_type
                                            result_data = line[0].findNext('td').contents
                                            for line_item in result_data:
                                                print type(line_item)
                                                if isinstance(line_item,NavigableString):
                                                    line_item_string=to_str(line_item)
                                                    if line_item_string.find(' MP')>0:
                                                        print line_item_string.find(' MP')
                                                        if data_point_type.lower()=="primary camera":
                                                            primary_camera=line_item_string
                                                            break
                                                        elif data_point_type.lower() == 'secondary camera':
                                                            secondary_camera=line_item_string
                                                            break

                            if line[0].contents[0]=='Flash type':
                                camera_flash=line[0].findNext('td').contents[0]
                            if line[0].contents[0]=='Features':
                                if line[0].parent and line[0].parent.parent and line[0].parent.parent.previousSibling:

                                    #print line[0].parent
                                    #print line[0].parent.parent
                                    #print line[0].parent.parent.parent
                                    section_heading= line[0].parent.parent.previousSibling
                                    table_heading = line[0].parent.parent.previousSibling.find('h2',attrs={'class':'header'})
                                    for headings in table_heading:
                                        if headings:
                                            data_point_type=headings
                                            print data_point_type
                                            result_data = line[0].findNext('td').contents
                                            for line_item in result_data:
                                                print type(line_item)
                                                if isinstance(line_item,NavigableString):
                                                    line_item_string=to_str(line_item)
                                                    if data_point_type=="Primary camera":
                                                        camera_other_features+=line_item_string+' , '
                                                        result_data_for_camera_extra_features = line[0].findNext('td').findNext('td').findNext('td').contents
                                                        camera_extra_features=''
                                                        for element in result_data_for_camera_extra_features:
                                                            if isinstance(element,NavigableString):
                                                                camera_extra_features+=element
                                                    elif data_point_type=='USB':
                                                        usb_features=line_item_string
                                                    elif data_point_type=='Battery':
                                                        battery_features+=line_item_string+ " , "
                            if line[0].contents[0]=='Storage':
                                storage_internal=line[0].findNext('td').contents[1]
                                try:
                                    if not line[0].findNext('td').contents[5] is None:
                                        storage_internal=storage_internal+' / '+line[0].findNext('td').contents[5]
                                    if not line[0].findNext('td').contents[9] is None:
                                        storage_internal=storage_internal+' / '+line[0].findNext('td').contents[9]
                                except IndexError as err:
                                    print 'indexError'
                            if line[0].contents[0]=='RAM capacity':
                                performance_ram=line[0].findNext('td').contents[1]
                            if line[0].contents[0]=='Capacity':
                                battery_capacity=line[0].findNext('td').contents[0]
                            if line[0].contents[0]=='3G talk time':
                                talk_time_container=line[0].findNext('td').contents
                                for talk_time in talk_time_container:
                                                print type(talk_time)
                                                if isinstance(talk_time,NavigableString):
                                                    talk_time_string=to_str(talk_time)
                                                    if talk_time_string.find(' hours ')>0:
                                                        print talk_time_string.find(' hours ')
                                                        battery_talktime_3g=talk_time_string
                                                        break
                                connectivity_data_has_3g=True
                            if line[0].contents[0]=='2G talk time':
                                talk_time_container=line[0].findNext('td').contents
                                for talk_time in talk_time_container:
                                                print type(talk_time)
                                                if isinstance(talk_time,NavigableString):
                                                    talk_time_string=to_str(talk_time)
                                                    if talk_time_string.find(' hours ')>0:
                                                        print talk_time_string.find(' hours ')
                                                        battery_talktime_2g=talk_time_string
                                                        #battery_talktime_2g=talk_time_string
                                                        break
                                connectivity_data_has_2g=True
                            if line[0].contents[0]=='4G talk time':
                                talk_time_container=line[0].findNext('td').contents
                                for talk_time in talk_time_container:
                                                print type(talk_time)
                                                if isinstance(talk_time,NavigableString):
                                                    talk_time_string=to_str(talk_time)
                                                    if talk_time_string.find(' hours ')>0:
                                                        print talk_time_string.find(' hours ')
                                                        battery_talktime_4g=talk_time_string
                                                        break
                                connectivity_data_has_4g=True
                            if connectivity_data_has_2g==True:
                                connectivity_data+='2G'
                            if connectivity_data_has_3g==True:
                                connectivity_data+=" /3G "
                            if connectivity_data_has_4g==True:
                                connectivity_data+=" /4g"


                            if line[0].contents[0]=='3G stand-by time':
                                talk_time_container=line[0].findNext('td').contents
                                for talk_time in talk_time_container:
                                                print type(talk_time)
                                                if isinstance(talk_time,NavigableString):
                                                    talk_time_string=to_str(talk_time)
                                                    if talk_time_string.find(' h')>0:
                                                        print talk_time_string.find(' h')
                                                        battery_standby_3g=talk_time_string
                                                        break
                            if line[0].contents[0]=='4G stand-by time':
                                talk_time_container=line[0].findNext('td').contents
                                for talk_time in talk_time_container:
                                                print type(talk_time)
                                                if isinstance(talk_time,NavigableString):
                                                    talk_time_string=to_str(talk_time)
                                                    if talk_time_string.find(' h')>0:
                                                        print talk_time_string.find(' h')
                                                        battery_standby_4g=talk_time_string
                                                        break


                            if line[0].contents[0]=='2G stand-by time':
                                talk_time_container=line[0].findNext('td').contents
                                for talk_time in talk_time_container:
                                                print type(talk_time)
                                                if isinstance(talk_time,NavigableString):
                                                    talk_time_string=to_str(talk_time)
                                                    if talk_time_string.find(' hours ')>0:
                                                        print talk_time_string.find(' hours ')
                                                        battery_standby_2g=talk_time_string
                                                        break

                            if line[0].contents[0]=='Version':
                                if line[0].parent and line[0].parent.parent and line[0].parent.parent.previousSibling:

                                    #print line[0].parent
                                    #print line[0].parent.parent
                                    #print line[0].parent.parent.parent
                                    section_heading= line[0].parent.parent.previousSibling
                                    table_heading = line[0].parent.parent.previousSibling.find('h2',attrs={'class':'header'})
                                    for headings in table_heading:
                                        if headings:
                                            data_point_type=headings
                                            print data_point_type
                                            result_data = line[0].findNext('td').contents
                                            for line_item in result_data:
                                                print type(line_item)
                                                if isinstance(line_item,NavigableString):
                                                    line_item_string=to_str(line_item)
                                                    if data_point_type=="Bluetooth":
                                                        connectivity_bluetooth=line_item_string
                                                    elif data_point_type=="USB":
                                                        usb_version=line_item_string
                            if line[0].contents[0]=='Wi-Fi':
                                result_data = line[0].findNext('td').contents
                                for line_item in result_data:
                                    print type(line_item)
                                    if isinstance(line_item,NavigableString):
                                        line_item_string=to_str(line_item)
                                        if line_item_string.find('802.11a')>0:
                                            connectivity_wifi+='802.11a'
                                        if line_item_string.find('802.11b')>0:
                                            connectivity_wifi+=' /b '
                                        if line_item_string.find('802.11g')>0:
                                            connectivity_wifi+=' /g '
                                        if line_item_string.find('802.11n')>0:
                                            connectivity_wifi+=' /n '
                                        if line_item_string.find('802.11ac')>0:
                                            connectivity_wifi+=' /ac '
                                        if line_item_string.find('802.11')<0:
                                            connectivity_tethering+=line_item_string + " / "

                            if line[0].contents[0]=='Tracking/Positioning':
                                result_data = line[0].findNext('td').contents
                                for line_item in result_data:
                                    print type(line_item)
                                    if isinstance(line_item,NavigableString):
                                        line_item_string=to_str(line_item)
                                        connectivity_navigation_tech+=line_item_string + " / "

                            if line[0].contents[0]=='Connectivity':
                                result_data = line[0].findNext('td').contents
                                for line_item in result_data:
                                    print type(line_item)
                                    if isinstance(line_item,NavigableString):
                                        line_item_string=to_str(line_item)
                                        connectivity_connector_type+=line_item_string + " / "

                            if line[0].contents[0]=='SoC':
                                performance_chipset=line[0].findNext('td').contents[0]

                            if line[0].contents[0]=='CPU cores':
                                performance_number_cores=line[0].findNext('td').contents[0]

                            if line[0].contents[0]=='Video FPS':
                                if line[0].parent and line[0].parent.parent and line[0].parent.parent.previousSibling:

                                    #print line[0].parent
                                    #print line[0].parent.parent
                                    #print line[0].parent.parent.parent
                                    section_heading= line[0].parent.parent.previousSibling
                                    table_heading = line[0].parent.parent.previousSibling.find('h2',attrs={'class':'header'})
                                    for headings in table_heading:
                                        if headings:
                                            data_point_type=headings
                                            print data_point_type
                                            result_data = line[0].findNext('td').contents
                                            for line_item in result_data:
                                                print type(line_item)
                                                if isinstance(line_item,NavigableString):
                                                    line_item_string=to_str(line_item)
                                                    if data_point_type.lower()=="primary camera":
                                                        camera_frame_rate=line_item_string
                                                        break
                                                    elif data_point_type.lower()=="secondary camera":
                                                        camera_secondary_frame_rate=line_item_string
                                                        secondary_camera_extra_features_set = line[0].findNext('td').findNext('td').findNext('td').contents
                                                        secondary_camera_extra_features=''
                                                        for element in secondary_camera_extra_features_set:

                                                            if isinstance(element,NavigableString):
                                                                secondary_camera_extra_features+=element

                                                        break

                            if line[0].contents[0]=='Colors':
                                result_data = line[0].findNext('td').contents
                                for line_item in result_data:
                                    print type(line_item)
                                    if isinstance(line_item,NavigableString):
                                        line_item_string=to_str(line_item)
                                        design_color+=line_item_string + " / "

                            if line[0].contents[0]=='Body materials':
                                result_data = line[0].findNext('td').contents
                                for line_item in result_data:
                                    print type(line_item)
                                    if isinstance(line_item,NavigableString):
                                        line_item_string=to_str(line_item)
                                        design_body_material+=line_item_string + " / "



                            if line[0].parent and line[0].parent.parent and line[0].parent.parent.previousSibling:
                                table_heading = line[0].parent.parent.previousSibling.find('h2',attrs={'class':'header'})
                                for headings in table_heading:
                                    if headings:
                                        data_point_type=headings
                                        print data_point_type
                                        if data_point_type=='Networks':
                                            if networks_already_traversed==False:
                                                networks_already_traversed=True
                                                new_result_set_data=table_heading.findNext('table')
                                                new_table_rows_list=new_result_set_data.findAll('tr')

                                                for table_row in new_table_rows_list:

                                                    table_dee=table_row.find('td')
                                                    for individual_stuff in table_dee:
                                                        if isinstance(individual_stuff,NavigableString):
                                                            connectivity_networks+=individual_stuff+ ' / '
                                                            break

                            if line[0].contents[0]=='User interface (UI)':
                                performance_ui_os=line[0].findNext('td').contents[0]

                            if line[0].contents[0]=='CPU':
                                performance_cpu=line[0].findNext('td').contents[0]

                            if line[0].contents[0]=='Other features':
                                result_data = line[0].findNext('td').contents
                                for line_item in result_data:
                                    print type(line_item)
                                    if isinstance(line_item,NavigableString):
                                        line_item_string=to_str(line_item)
                                        display_touch_features+=line_item_string + " / "
                                display_features_set=line[0].nextSibling.findNext('td').nextSibling
                                for line_item in display_features_set:
                                    if isinstance(line_item,NavigableString):
                                        line_item_string=to_str(line_item)
                                        display_touch_features+=line_item_string + " / "


                            if line[0].contents[0]=='Sensors':
                                result_data = line[0].findNext('td').contents
                                for line_item in result_data:
                                    print type(line_item)
                                    if isinstance(line_item,NavigableString):
                                        line_item_string=to_str(line_item)
                                        features_sensors+=line_item_string + " / "

                            if line[0].contents[0]=='Video resolution':
                                if line[0].parent and line[0].parent.parent and line[0].parent.parent.previousSibling:

                                    #print line[0].parent
                                    #print line[0].parent.parent
                                    #print line[0].parent.parent.parent
                                    section_heading= line[0].parent.parent.previousSibling
                                    table_heading = line[0].parent.parent.previousSibling.find('h2',attrs={'class':'header'})
                                    for headings in table_heading:
                                        if headings:
                                            data_point_type=headings
                                            print data_point_type
                                            result_data = line[0].findNext('td').contents
                                            for line_item in result_data:
                                                print type(line_item)
                                                if isinstance(line_item,NavigableString):
                                                    line_item_string=to_str(line_item)
                                                    if line_item_string.find(' pixels')>0:
                                                        print line_item_string.find(' pixels')
                                                        if data_point_type.lower()=="primary camera":
                                                            primary_video_resolution=line_item_string
                                                            break
                                                        elif data_point_type.lower() == 'secondary camera':
                                                            secondary_video_resolution=line_item_string
                                                            break

                            if line[0].contents[0]=='Radio':
                                av_radio=line[0].findNext('td').contents[0]

                            if line[0].contents[0]=='Connector type':
                                usb_connector_type=line[0].findNext('td').contents[0]

                            if line[0].contents[0]=='Audio file formats/codecs':
                                result_data = line[0].findNext('td').contents
                                for line_item in result_data:
                                    print type(line_item)
                                    if isinstance(line_item,NavigableString):
                                        line_item_string=to_str(line_item)
                                        av_audio_format+=line_item_string + " / "

                            if line[0].contents[0]=='Video file formats/codecs':
                                result_data = line[0].findNext('td').contents
                                for line_item in result_data:
                                    print type(line_item)
                                    if isinstance(line_item,NavigableString):
                                        line_item_string=to_str(line_item)
                                        av_video_format+=line_item_string + " / "

                            if line[0].contents[0]=='Type':
                                battery_type=line[0].findNext('td').contents[0]

                            if line[0].contents[0]=='Pixel density':
                                weight_container=line[0].findNext('td').contents
                                for weight_item in weight_container:
                                                print type(weight_item)
                                                if isinstance(weight_item,NavigableString):
                                                    weight_item_string=to_str(weight_item)
                                                    if weight_item_string.find(' ppi ')>0:
                                                        print weight_item_string.find(' ppi ')
                                                        display_ppi=weight_item_string
                                                        break

                            if line[0].contents[0]=='Sensor model':
                                camera_sensor_model=line[0].findNext('td').contents[0]

                            if line[0].contents[0]=='Sensor type':
                                camera_sensor_type=line[0].findNext('td').contents[0]

                            if line[0].contents[0]=='Aperture':
                                camera_aperture=line[0].findNext('td').contents[0]

                            if line[0].contents[0]=='Sensor size':
                                weight_container=line[0].findNext('td').contents
                                for weight_item in weight_container:
                                                print type(weight_item)
                                                if isinstance(weight_item,NavigableString):
                                                    weight_item_string=to_str(weight_item)
                                                    if weight_item_string.find(' mm ')>0:
                                                        print weight_item_string.find(' mm ')
                                                        camera_sensor_size=weight_item_string
                                                    if weight_item_string.find(" in ")>0:
                                                        camera_sensor_size+=weight_item_string
                                                        break

                            if line[0].contents[0]=='Pixel size':
                                weight_container=line[0].findNext('td').contents
                                for weight_item in weight_container:
                                                print type(weight_item)
                                                if isinstance(weight_item,NavigableString):
                                                    weight_item_string=to_str(weight_item)
                                                    if weight_item_string.find(' µm ')>0:
                                                        print weight_item_string.find(' µm ')
                                                        camera_pixel_size=weight_item_string[:-4]+" micrometers "
                                                    if weight_item_string.find(" mm ")>0:
                                                        camera_pixel_size+=weight_item_string
                                                        break
                            #User interface (UI)
                            if line[0].contents[0]=='HDMI':
                                weight_container=line[0].findNext('td').contents
                                for weight_item in weight_container:
                                                print type(weight_item)
                                                if isinstance(weight_item,NavigableString):
                                                    weight_item_string=to_str(weight_item)
                                                    connectivity_HDMI=weight_item_string
                                                    break
                            if line[0].contents[0]=='User interface (UI)':
                                weight_container=line[0].findNext('td').contents
                                for weight_item in weight_container:
                                                print type(weight_item)
                                                if isinstance(weight_item,NavigableString):
                                                    weight_item_string=to_str(weight_item)
                                                    performance_ui_os=weight_item_string
                                                    break

                            print connectivity_networks













                                                    #dimensions_size=line_item
                                                    #break






                                #print dimensions_size
                if (connectivity_wifi==''):
                    connectivity_div=soup.find('div', attrs={"id":'model-brief-specifications'})
                    for item in connectivity_div.contents:
                        if type(item) is Tag:
                            if len(item.contents)>0:
                                if(item.contents[0]=='Wi-Fi'):
                                    connectivity_wifi=item.next_sibling
                                    break

                #print brand
                #print model_name
                #print dimensions_weight
                dimensions_size
                dimension_size = dimensions_size[:-2]
                #print dimensions_size
                #print primary_camera
                #print secondary_camera
                #print display_resolution
                #print display_type
                if connectivity_data.find('2G')>0:
                    connectivity_data_reporter+="2G"
                if connectivity_data.find("3G")>0:
                    connectivity_data_reporter+="3G"
                if connectivity_data.find("4G")>0:
                    connectivity_data_reporter+="4G"
                connectivity_data_reporter.replace("G","G/ ")
                #connectivity_data_reporter=connectivity_data_reporter[:-2]




                    #Coz u only gotta write it once
                #my_header_list=
                #my_header_string="~".join(map(str,my_header_list))
                #f.write(my_header_string)
                    #f.write(["Brand", "Model Name","Price", "Operating System", "CPU Frequency", "GPU","SIM Size","SIM Type","Dimensions Size","","",
                     #                "Dimensions Weight","Display Size","Display Resolution","Display Type","Primary Camera","Secondary Camera",
                      #               "Camera Flash","Camera Video Recording","Camera HD Recording","Camera Other Features","Internal Storage","Expandable Storage",
                      #               "Performance RAM","Battery Capacity","Battery 2G Talktime","Battery 3G Talktime","Battery 4G Talktime","Connectivity Data",
                       #              "Connectivity Bluetooth","Connectivity Wifi", "Connectivity Tethering","Tracking/Positioning","HDMI",
                       #              "Release Date","","","Performance Chipset","Performance Cores",
                        #             "Camera Frame rate","Design Color","Design Body Material","Connectivity networks","","","","","","Performance UI Os","Performance CPU",
                        #             "Soc Other features","Features Sensors","Camera Secondary Video Rate","Camera Secondary Frame Rate","AV Radio",
                         #            "USB Connector Type","USB Version","USB Features","Connectivity Connector Type","AV Audio Format",
                         #            "AV Video Format","Battery Type","Battery Features","Display PPI","Display Screen Protection","Battery 2g Standby",
                          #           "Battery 3g standby","Battery 4G standby",
                           #          "Camera Sensor Model","Camera Sensor Type","Camera Sensor Size","Camera Pixel size","Camera Aperture",
                           #          "Display Extra features","Primary Camera Extra","Secondary Camera Extra"])
                tuple_row=(to_str(brand).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),to_str(model_name).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           "Nothing".replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(operating_system).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                            to_str(processor_speed).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                                 to_str(gpu).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(sim_size).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(sim_type).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(dimensions_size).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           "Nothing".replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),"Nothing".replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(dimensions_weight).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(display_size).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                                 to_str(display_resolution).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(display_type).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(primary_camera).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(secondary_camera).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(camera_flash).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                                 to_str(primary_video_resolution).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(camera_hd_recording).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(camera_other_features).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(storage_internal).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                                 to_str(storage_expandable).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(performance_ram).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(battery_capacity).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(battery_talktime_2g).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(battery_talktime_3g).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                                to_str(battery_talktime_4g).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(connectivity_data_reporter).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(connectivity_bluetooth).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(connectivity_wifi).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                                 to_str(connectivity_tethering).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(connectivity_navigation_tech).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(connectivity_HDMI).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(release_date).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),"Nothing".replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),"Nothing".replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                            to_str(performance_chipset).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(performance_number_cores).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(camera_frame_rate).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(design_color).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(design_body_material).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                                 to_str(connectivity_networks).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),"Nothing".replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),"Nothing".replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),"Nothing".replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),"Nothing".replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),"Nothing".replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(performance_ui_os).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(performance_cpu).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                                 to_str(display_touch_features).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(features_sensors).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(secondary_video_resolution).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(camera_secondary_frame_rate).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                                 to_str(av_radio).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(usb_connector_type).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(usb_version).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(usb_features).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(connectivity_connector_type).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                                 to_str(av_audio_format).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(av_video_format).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(battery_type).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(battery_features).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(display_ppi).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                                 to_str(display_touch_features).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(battery_standby_2g).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(battery_standby_3g).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(battery_standby_4g).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(camera_sensor_model).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                                 to_str(camera_sensor_type).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(camera_sensor_size).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(camera_pixel_size).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(camera_aperture).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(display_touch_features).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(camera_extra_features).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"),
                           to_str(secondary_camera_extra_features).replace('\t','').replace('\r','').replace('\n','').replace('~','@').replace('"','').replace(",","^"))
                device_specs.append(tuple_row)
            else:
                tuple_row=("\n")
                device_specs.append(tuple_row)

                #f.write([to_str(brand),to_str(model_name),"",to_str(operating_system),to_str(processor_speed),
                #                 to_str(gpu),to_str(sim_size),to_str(sim_type),to_str(dimensions_size),"","",to_str(dimensions_weight),to_str(display_size),
                #                 to_str(display_resolution),to_str(display_type),to_str(primary_camera),to_str(secondary_camera),to_str(camera_flash),
                #                 to_str(primary_video_resolution),to_str(camera_hd_recording),to_str(camera_other_features),to_str(storage_internal),
                #                 to_str(storage_expandable),to_str(performance_ram),to_str(battery_capacity),to_str(battery_talktime_2g),to_str(battery_talktime_3g),
                #                 to_str(battery_talktime_4g),to_str(connectivity_data_reporter),to_str(connectivity_bluetooth),to_str(connectivity_wifi),
                #                 to_str(connectivity_tethering),to_str(connectivity_navigation_tech),to_str(connectivity_HDMI),to_str(release_date),"","",
                #                 to_str(performance_chipset),to_str(performance_number_cores),to_str(camera_frame_rate),to_str(design_color),to_str(design_body_material),
                #                 to_str(connectivity_networks),"","","","","",to_str(performance_ui_os),to_str(performance_cpu),
                #                 to_str(display_touch_features),to_str(features_sensors),to_str(secondary_video_resolution),to_str(camera_secondary_frame_rate),
                #                 to_str(av_radio),to_str(usb_connector_type),to_str(usb_version),to_str(usb_features),to_str(connectivity_connector_type),
                #                 to_str(av_audio_format),to_str(av_video_format),to_str(battery_type),to_str(battery_features),to_str(display_ppi),
                #                 to_str(display_touch_features),to_str(battery_standby_2g),to_str(battery_standby_3g),to_str(battery_standby_4g),to_str(camera_sensor_model),
                #                 to_str(camera_sensor_type),to_str(camera_sensor_size),to_str(camera_pixel_size),to_str(camera_aperture),to_str(display_touch_features),to_str(camera_extra_features),to_str(secondary_camera_extra_features)])

    for row in device_specs:
        row_as_string = "~".join(row)
        #print row_as_string
        #print row
        csv_out.writerow(row)
    #csv_out.close()
    return "Alleluia"


@app.route('/natgrid_search')
def natgrid_search():
    return render_template('natgrid_search.html')

@app.route('/go_for_nat_grid', methods=['GET', 'POST'])
def go_for_nat_grid():
    #keywords_results = request.values.getlist('keywords[]')
    search_term=request.values.get('query')
    print search_term

    #print keywords_results
    #print len(keywords_results)
    # Start Google Link extraction
    driver = init_driver()
    my_results = lookup(driver, search_term)
    search_term=search_term.replace(' ',"_")
    time.sleep(5)
    linkList = []
    #elems = driver.find_elements_by_xpath("//a[@href]")
    elems = driver.find_elements_by_xpath("//h3[@class='r']/a[@href]")
    news_elems =driver.find_elements_by_xpath("//div[@class='_Ivo']/a[@href]")
    for elem in elems:
        if elem.get_attribute('href')not in linkList:
            linkList.append(elem.get_attribute('href'))
    for news_elem in news_elems:
        if news_elem.get_attribute('href') not in linkList:
            linkList.append(news_elem.get_attribute('href'))
    print len(linkList)
    driver.quit()
    scraped_results_links_output_file=open('/Users/ShyamR/Desktop/link_results.csv','w')
    csv_out=unicodecsv.writer(scraped_results_links_output_file,delimiter='~')
    #csv_out.writerow(["Cluster name",'cluster entry',"","senti-aspect combo"])
    for line in linkList:
        csv_out.writerow([line])
    #return "I wanna go home"
    #for element in linkList:
    print 'Job Done.'
    scraped_results_links_output_file.close()
    # End google Link Extraction

    # Start XML generation
    gflow_data_dir = '/Users/ShyamR/Downloads/gflow-2014-9-17/data/gflowExamples/'
    link_results_file = open('/Users/ShyamR/Desktop/link_results.csv','rb')
    reader = csv.reader(link_results_file)
    #list_of_records = list()
    i=0
    for row in link_results_file:
        i=i+1
        #link = (row[0])
        #print link
        target_url = row
        req = urllib2.Request(target_url)
        try:
            response=urllib2.urlopen(req)
            content=response.read()
            print type(content)
            soup=BeautifulSoup(content)
            text_only_content = soup.get_text()
            string_html = soup.prettify()
            title=soup.title.string
            nltk_text_only_content=clean_html(string_html)
            root = etree.Element("DOC")
            doc=etree.ElementTree(root)
            etree.SubElement(root,'DATETIME').text='2017-1-30 15:58:4'
            etree.SubElement(root,'TITLE').text=title
            etree.SubElement(root,'TEXT').text=nltk_text_only_content.strip()
            s = etree.tostring(root, pretty_print=True)
            s=s.strip()
            #print s
            if not os.path.isdir(gflow_data_dir+search_term):
                os.mkdir(gflow_data_dir+search_term)
                os.mkdir(gflow_data_dir+search_term+'/'+'original')


            text_file = open(gflow_data_dir+search_term+'/'+'original/'+search_term+'_'+str(i)+".xml", "w")
            text_file.write(s)
            text_file.close()
        except (urllib2.HTTPError,urllib2.URLError,AttributeError,socket.timeout,IndexError,KeyError,TypeError,ValueError) as err:
            print "gaya re gaya"
            #End XML Generation

            # Start the magic work of Gflow
    os.chdir('/Users/ShyamR/Downloads/gflow-2014-9-17/')
    #call([]) Don't forget the pre-processing script
    #os.system('export WORDNET_DICT=/Users/ShyamR/Downloads/WordNet-3.0/dict')
    os.putenv('WORDNET_DICT','/Users/ShyamR/Downloads/WordNet-3.0/dict')
    preprocessing_string = 'python preprocessing.py /Users/ShyamR/Downloads/stanford-corenlp-full-2016-10-31/ /Users/ShyamR/Downloads/ /Users/ShyamR/Downloads/gflow-2014-9-17/data/gflowExamples/'+search_term
    os.system(preprocessing_string)
    os.system('javac src/edu/washington/cs/knowitall/*/*.java -d bin')
    os.system('java -Xmx8G -classpath bin/ edu.washington.cs.knowitall.main.GFlow data/gflowExamples/'+search_term)
            # End of Gflow
    #STart entities list
    client = language.Client.from_service_account_json("/Users/ShyamR/Downloads/My Project-75d6286abeb0.json")
    #text_content="Google, headquartered in Mountain View, unveiled the new Android phone at the Consumer Electronic Show. Sundar Pichai said in his keynote that users love  their new Android phones.'"
    #with open("/Users/ShyamR/Downloads/")
    unique_entities_list = list()
    #os.system('cd '+ gflow_data_dir+search_term+'/'+'original')
    #os.system('rm -rf .DS)
    analysis_home = '/Users/ShyamR/Downloads/gflow-2014-9-17/data/gflowExamples/'+search_term+'/original/'
    with open("/Users/ShyamR/Desktop/all_summaries/summaries_"+search_term+".csv","wb") as outcsv:
        writer = csv.writer(outcsv)
        writer.writerow(["Entity_Name","Entity_Type","Entity_Wiki_URL","Entity_Metadata","Entity_Salience","Document_source"])

        for root_dir, _, files_list in os.walk(gflow_data_dir+search_term+'/original/'):
            for file in files_list:
                if file.endswith(".xml"):
                    print file
                    xml_document = xml.etree.ElementTree.parse(analysis_home+file).getroot()
                    xml_document_title = xml_document.find('TITLE')
                    xml_document_text=xml_document.find('TEXT')
                    text_content_xml=xml_document_title.text+ " ." + xml_document_text.text

                    document = client.document_from_text(text_content_xml)
                    entities = document.analyze_entities()
                    #new_dict = dict()
                    #with open(home+"hello.json",'wb') as outfile:
                        #row_json = json.dumps(entities)
                        #new_dict['xxa.txt']=entities
                        #new_dict_json=json.dumps(entities)
                        #json.dump(new_dict_json,outfile)
                        #json.dump(row_json,outfile)

                    for i,entity in enumerate(entities):
                        print i
                        print('=' * 20)
                        print('         name: %s' % (entity.name,))
                        print('         type: %s' % (entity.entity_type,))
                        print('wikipedia_url: %s' % (entity.wikipedia_url,))
                        print('     metadata: %s' % (entity.metadata,))
                        print('     salience: %s' % (entity.salience,))
                        if entity.name not in unique_entities_list:
                            unique_entities_list.append(entity.name)

                            writer.writerow([to_str(entity.name),to_str(entity.entity_type),to_str(entity.wikipedia_url),to_str(entity.metadata),to_str(entity.salience),to_str(file)])


    outcsv.close()

    #End of entities list
    entities_file = open("/Users/ShyamR/Desktop/all_summaries/summaries_"+search_term+".csv",'rb')
    reader = csv.reader(entities_file)
    list_of_records = list()
    for row in reader:
        tuple_row = (to_unicode(row[0]),to_unicode(row[1]),to_unicode(row[2]),to_unicode(row[3]),to_unicode(row[4]),to_unicode(row[5]))
        list_of_records.append(tuple_row)
    with open('/Users/ShyamR/Desktop/summary_results.txt', 'r') as myfile:
        data=myfile.read().replace('\n', '')
        data=to_str(data)
    return render_template('natgrid_search_results.html',results=list_of_records,summary=to_unicode(data))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')




