from flask import Flask,jsonify,render_template,request
import requests
from flask_cors import CORS,cross_origin
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import csv

logging.basicConfig(filename='scrapper.log',level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods=['GET'])
def homepage():
    return render_template('index.html')

@app.route('/review', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        try:
            searchstring = request.form['content'].replace(" ","")
            flipkarturl = "https://www.flipkart.com/search?q="+searchstring
            uclient = uReq(flipkarturl)
            flipkartpage = uclient.read()
            uclient.close()
            flipkart_html = bs(flipkartpage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class":"_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productlink = flipkarturl+box.div.div.div.a['href']
            product_request = requests.get(productlink)
            product_request.encoding='UTF-8'
            product_html = bs(product_request.text, "html.parser")
            print(product_html)
            comment_box = product_html.findAll("div", {"class":"_16PBlm"})
            filename=searchstring+".csv"
            fw = open(filename,'w')
            headers = "Product,Customer Name,Rating,Heading,'Comment\n"
            fw.write(headers)
            reviews = []
            for commentbox in comment_box:
                try:
                    name = commentbox.find_all("div",{"class":"row _3n8db9"})[0].div.p.text
                except:
                    name = "No name"
                    logging.info(name)
                try:
                    rating = commentbox.div.div.div.div.text
                except:
                    rating = "No ratings"
                    logging.info(rating)
                try:
                    heading = commentbox.div.div.div.p.text
                except:
                    heading = "Comment haven't any headings"
                    logging.info(heading)
                try:
                    comtag = commentbox.div.div.find_all("div",{"class":""}) 
                    comment = comtag[0].div.text
                except Exception as e:
                    logging.error(e)
                mydict = {'Product':searchstring, "Name":name, "Rating":rating,"Heading":heading,"Comment":comment}
                logging.info(mydict)
                reviews.append(mydict)
                # filename=searchstring+".csv"
                # fw = open(filename,'w',newline='')
                # file_write = f"{searchstring},{name},{rating},{heading},{comment}"
                # fw.write(file_write)
            return render_template("result.html", reviews = reviews[0:len(reviews)-1])
        except Exception as e:
            logging.error(e)
            return "Something went wrong"
    else:
        return render_template('index.html')
        
if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)
