import os
import sqlite3
from flask import Flask, flash, request, redirect, url_for,render_template,send_file
from werkzeug.utils import secure_filename
app = Flask(__name__)
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import docx2txt
from PyPDF2 import PdfFileReader, PdfFileWriter
from sklearn.feature_extraction.text import TfidfVectorizer
from pandas import DataFrame
import resume_parser
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import MWETokenizer
from pyresparser import ResumeParser
from docx import Document
import numpy as np
import pandas as pd
import re
from ftfy import fix_text
from nltk.corpus import stopwords
from sklearn.neighbors import NearestNeighbors
import resume_parser
import csv
stopw  = set(stopwords.words('english'))

df =pd.read_csv('C:/EDI SEM1/job_final.csv',encoding_errors= 'replace') 
df['test']=df['Job_Description'].apply(lambda x: ' '.join([word for word in str(x).split() if len(word)>2 and word not in (stopw)]))


@app.route('/download')
def download():
    path = 'data.csv'
    return send_file(path, as_attachment=True)


UPLOAD_FOLDER = 'C:/EDI SEM1/uploaded_resume'
DESCRIPTION_FOLDER='C:\EDI SEM1\job_desciptions'
ALLOWED_EXTENSIONS = {'txt','pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


import analyser

import resume_parser




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


 
@app.route("/")
def index():
    return render_template("index.html")


 
# reading the data in the csv file
d = pd.read_csv('data.csv')
d.to_csv('data.csv', index=None)
  


@app.route('/admin')
def admin():
    
    # converting csv to html
    data = pd.read_csv('data.csv')
    return render_template('admin.html', tables=[data.to_html()], titles=[''])
  






@app.route("/candidate")
def candidate():
    return render_template("candidate.html")
    
@app.route("/resume_comparison", methods=['GET', 'POST'])
def resume_comparison():
    if request.method == 'POST':    
        select = request.form.get('job-desc')
        name=request.form.get('Name')
        path=DESCRIPTION_FOLDER+'/'+str(select)+".txt"
        
        if 'file' not in request.files: 
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        pdf_path=UPLOAD_FOLDER+'/'+file.filename
       
        data = ResumeParser(file.filename).get_extracted_data()
        name=data['name']
        email=data['email']

            
        with open('data.csv', 'a',newline='') as outfile:  

          w = csv.writer(outfile)
          w.writerow([name, email,str(round(analyser.resume_analyser(UPLOAD_FOLDER+'/'+file.filename,path))),str(select)])
            
        return "           similarity of resume and job description is :"+str(round(analyser.resume_analyser(UPLOAD_FOLDER+'/'+file.filename,path)))
    return render_template("resume_comparison.html")

@app.route("/resume_par", methods=['GET', 'POST'])
def resume_par():
    if request.method=='POST':
        f = request.files['file']
        f.save(f.filename)
        
        
        data = ResumeParser(f.filename).get_extracted_data()
        name=data['name']
        email=data['email']
        phone=data['mobile_number']
        education=data['college_name']
        skills=data['skills']

                
                
        
            
        return render_template("resume_par.html",name=name,email=email,phone=phone,skills=skills,education=education)
    return render_template("resume_par.html")




@app.route('/cv_job_sugg',methods=['GET', 'POST'])
def submit_data1():
    if request.method == 'POST':
        
        f=request.files['userfile']
        f.save(f.filename)
        try:
            doc = Document()
            with open(f.filename, 'r') as file:
                doc.add_paragraph(file.read())
                doc.save("text.docx")
                data = ResumeParser('text.docx').get_extracted_data()
                
        except:
            data = ResumeParser(f.filename).get_extracted_data()
        resume=data['skills']
        
    
        skills=[]
        skills.append(' '.join(word for word in resume))
        org_name_clean = skills
        
        def ngrams(string, n=3):
            string = fix_text(string) 
            string = string.encode("ascii", errors="ignore").decode() 
            string = string.lower()
            chars_to_remove = [")","(",".","|","[","]","{","}","'"]
            rx = '[' + re.escape(''.join(chars_to_remove)) + ']'
            string = re.sub(rx, '', string)
            string = string.replace('&', 'and')
            string = string. replace(',', ' ')
            string = string.replace('-', ' ')
            string = string.title()
            string = re.sub(' +',' ',string).strip() 
            string = ' '+ string +' ' 
            string = re.sub(r'[,-./]|\sBD',r'', string)
            ngrams = zip(*[string[i:] for i in range(n)])
            return [''.join(ngram) for ngram in ngrams]
        vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams, lowercase=False)
        tfidf = vectorizer.fit_transform(org_name_clean)
       
        
        def getNearestN(query):
          queryTFIDF_ = vectorizer.transform(query)
          distances, indices = nbrs.kneighbors(queryTFIDF_)
          return distances, indices
        nbrs = NearestNeighbors(n_neighbors=1, n_jobs=-1).fit(tfidf)
        unique_org = (df['test'].values)
        distances, indices = getNearestN(unique_org)
        unique_org = list(unique_org)
        matches = []
        for i,j in enumerate(indices):
            dist=round(distances[i][0],2)
  
            temp = [dist]
            matches.append(temp)
        matches = pd.DataFrame(matches, columns=['Match confidence'])
        df['match']=matches['Match confidence']
        df1=df.sort_values('match')
        df2=df1[['Position', 'Company','Location']].head(10).reset_index()
        
        
        
        
        
 
        return render_template('model.html',tables=[df2.to_html(classes='job')],titles=['na','Job'])
    return render_template('model.html')
    
       

# @app.route('/skiils_job',methods=['GET', 'POST'])
# def submit_data2():
#     if request.method == 'POST':
        
#         print(request.form['list_jobs'])
       
#         resume=list(request.form['list_jobs'])
#         print(type(resume))
#         skills=[]
#         skills.append(' '.join(word for word in resume))
#         org_name_clean = skills
        
#         def ngrams(string, n=3):
#             string = fix_text(string) 
#             string = string.encode("ascii", errors="ignore").decode() 
#             string = string.lower()
#             chars_to_remove = [")","(",".","|","[","]","{","}","'"]
#             rx = '[' + re.escape(''.join(chars_to_remove)) + ']'
#             string = re.sub(rx, '', string)
#             string = string.replace('&', 'and')
#             string = string.replace(',', ' ')
#             string = string.replace('-', ' ')
#             string = string.title() 
#             string = re.sub(' +',' ',string).strip()
#             string = ' '+ string +' ' # pad names for ngrams...
#             string = re.sub(r'[,-./]|\sBD',r'', string)
#             ngrams = zip(*[string[i:] for i in range(n)])
#             return [''.join(ngram) for ngram in ngrams]
#         vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams, lowercase=False)
#         tfidf = vectorizer.fit_transform(org_name_clean)
      
        
        
#         def getNearestN(query):
#           queryTFIDF_ = vectorizer.transform(query)
#           distances, indices = nbrs.kneighbors(queryTFIDF_)
#           return distances, indices
#         nbrs = NearestNeighbors(n_neighbors=1, n_jobs=-1).fit(tfidf)
#         unique_org = (df['test'].values)
#         distances, indices = getNearestN(unique_org)
#         unique_org = list(unique_org)
#         matches = []
#         for i,j in enumerate(indices):
#             dist=round(distances[i][0],2)
  
#             temp = [dist]
#             matches.append(temp)
#         matches = pd.DataFrame(matches, columns=['Match confidence'])
#         df['match']=matches['Match confidence']
#         df1=df.sort_values('match')
#         df2=df1[['Position', 'Company','Location']].head(10).reset_index()
        
        
        
        
        
     
#         return render_template('new_model.html',tables=[df2.to_html(classes='job')],titles=['na','Job'])
#     return render_template("new_model.html")
    

     

if __name__ == "__main__":
    app.run(debug=True)