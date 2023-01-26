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
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import io
file_path = "C:/EDI SEM1/Affan_Shaikh_Resume.pdf"


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            
            resource_manager = PDFResourceManager()
            
           
            fake_file_handle = io.StringIO()
            
            
            converter = TextConverter(
                                resource_manager, 
                                fake_file_handle, 
                                codec='utf-8', 
                                laparams=LAParams()
                        )

            
            page_interpreter = PDFPageInterpreter(
                                resource_manager, 
                                converter
                            )

            
            page_interpreter.process_page(page)
            
            
            text = fake_file_handle.getvalue()
            yield text

          
            converter.close()
            fake_file_handle.close()



def resume_analyser(resume,job_desc):
        
    text=''
    for page in extract_text_from_pdf(resume):
        text += ' ' + page
      
    lemmatizer=WordNetLemmatizer()
     

    lst = []
    for line in text.split():
        lst.append(line)
    lst = ([lemmatizer.lemmatize(w) for w in lst])
    
    new_words = [word for word in lst if word.isalnum()]
        
    WordSet = []
    for word in new_words:
        if word not in set(stopwords.words("english")):
            WordSet.append(word)
    string = " ".join(WordSet)
    # print(string)
    
    f = open(job_desc, "r")
    lst=[]
        
    for line in f:
        for i in line.split(" "):
            lst.append(i)
    lst = ([lemmatizer.lemmatize(w) for w in lst])
    new_words=[]
    new_words = [word for word in lst if word.isalnum()]



    WordSet = []
    for word in new_words:
        if word not in set(stopwords.words("english")):
            WordSet.append(word)
    
    

    string2 = " ".join(new_words)
    # print(string2)
    content = [string2, string]

    cv = TfidfVectorizer()

    matrix = cv.fit_transform(content)


    similarity_matrix = cosine_similarity(matrix)

    return similarity_matrix[0][1]*100*6.29


# resume_analyser(file_path,"C:/EDI SEM1/job_desciptions/FullStack.txt")














lst = []


