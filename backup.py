from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            gamespot_url = "https://www.gamespot.com/search/?i=site&q=" + searchString
            uClient = uReq(gamespot_url)
            gamespotpage = uClient.read()
            uClient.close()
            gamespot_html = bs(gamespotpage, "html.parser")
            game = requests.get(game_link)

            # this will find all the related game links according to the search string
            all_games = gamespot_html.find_all('li', {'class': 'media clearfix'})
            game_title_div = all_games[0].find('div',{'class': 'media-body'})
            game_link = 'https://www.gamespot.com' + game_title_div.a['href'] + 'reviews'
            game = requests.get(game_link)
            game_page = game.text
            game_html_page = bs(game_page,'html.parser')
            pagination_box = game_html_page.find_all('a',{'class': 'btn'})
            pagenumbers = []
            for i in range(len(pagination_box)):
                if pagination_box[i] and pagination_box[i].text.isdigit():
                    pagenumbers.append(int(pagination_box[i].text))

            # max page number
            max_page_number = max(pagenumbers)
            if max_page_number >= 5:
                max_page_number = 5

            review_links = []
            for i in range(1,max_page_number+1):
                review_links.append('https://www.gamespot.com' + pagination_box[0]['href'] + f'?page={i}')

            all_user_full_review = []
            count =0
            for i in range(len(review_links)):
                review_section_page = requests.get(review_links[i])
                review_section = review_section_page.text
                review_section_html_page = bs(review_section,'html.parser')
                reviews = review_section_html_page.find_all('li',{'class':'media media-game userReview-list__item clearfix'})
                for j in range(len(reviews)):
                    full_review_link = 'https://www.gamespot.com' + reviews[j].a['href']
                    full_review_page= requests.get(full_review_link)
                    full_review = full_review_page.text
                    review = bs(full_review,'html.parser')
                    user_details = review.find('section',{'class':'userReview-hdr border-bottom--thin--75 vertical-spacing-bottom-rem inner-space-bottom-small-rem'})
                    try:
                        user_rating = user_details.div.span.text
                    except:
                        user_rating = 'no rating'
                        logging.info('user_rating')
                    #print(user_rating)
                    try:
                        user_name = user_details.a.text
                    except:
                        logging.info('user_name')
                    #print(user_name)
                    try:
                        review_summary = review.find_all('section',{'class':'userReview-body typography-format'})
                        final_review= review_summary[0].text
                    except Exception as e:
                        logging.info(e)

                    #print(final_review)
                    count+=1
                    print(count)
                    all_user_full_review.append({'Product':searchString,'Name': user_name,'Rating': user_rating,'Review': final_review})
            logging.info("log my final result {}".format(all_user_full_review))
        

            return render_template('result.html', reviews=all_user_full_review[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            print(e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0")
