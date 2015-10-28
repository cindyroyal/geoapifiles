# 
# @author Apan Qasem
# @date 10/15/14
#    
# This program collects data via the Twitter search API and generates an HTML file. 
# Search results are filtered by geo-tagging.
# 
# The HTML file contains coordinates and text of each filtered result 
# The generated HTML file is concatenated with another file that contains the visualization script
# 
# 

import oauth2 as oauth        # oauth authorization needed for twitter API
import json                   # converting data into json object 
from pprint import pprint     # pretty print 
import os                     # for contatenating generated files 
import sys

# my keys, need all four of them. Use your own keys here.
consumer_key = "ohaVzTnC95piiNDv967FBZNsC"
consumer_secret = "FNXcMvYXYm2ZE1jK243XcheboNu2EUSexga1CP2xXHfpCfr8QO"
token_key = "1246761-39k6SCDVPLh8yIzuzRDZCVzX2Sukll6e2gPyz3zNEB"
token_secret = "MpO6F1Mb4VmD3mGsbsevepSKp3gI9VfCTigbMyz2oArcy"

# construct search term 
searchTerm = "world series"

# short name used as file prefix 
searchTermShort = "series"

#
# function to construct search url 
#   - count value is always set to 100 
#   - defaul value for max_id is 0
#
def makeurl(searchterm, max_id=0) :
    baseurl = "https://api.twitter.com/1.1/search/tweets.json"
    count = "100"
    if max_id == 0:
        url = baseurl + '?q=' + searchterm + '&' \
              + 'count=' + count    
    else:
        url = baseurl + '?q=' + searchterm + '&' \
              + 'max_id=' + str(max_id) + '&' \
              + 'count=' + count    
    return url 

#
# Following functions generates HTML output 
#

#
# start tr element and write longitude and latitude in two table cells 
# 
def write_coord(lng, lat, num, localfile) :
    localfile.write("<tr id = \"coord" + str(num) + "\">\n")
    localfile.write("<td id = \"lng\"" + ">")
    localfile.write(str(lng))
    localfile.write("</td>")
    localfile.write("<td id = \"lat\"" + ">")
    localfile.write(str(lat))
    localfile.write("</td>\n")
    return 

#
# write tweet text and end tr element 
#
def write_text_as_td(text):
    localfile.write("<td>")
    localfile.write(text)
    localfile.write("</td>\n")
    localfile.write("</tr>\n")
    return 

#
# start html body and write div element for map 
# 
def write_html_body_prefix(localfile) :
    localfile.write("<style>iframe { width: 100%; height: 468px }</style>")
    localfile.write("<body>\n")
    localfile.write("<div id = \"map\" style=\"height: 468px\"><iframe src=\"" + searchTermShort + "_tweets_map.html\"></iframe></div>")
    localfile.write("<table id = \"cTable\">\n")
    return 
#
# end table element 
# end body
#
def write_html_body_suffix(localfile) :
    localfile.write("</table>\n")
    localfile.write("</body>\n")
    localfile.write("</html>\n")
    return 
    


url = makeurl(searchTerm)

# set up oauth tokens
token = oauth.Token(token_key, token_secret)
consumer = oauth.Consumer(consumer_key, consumer_secret)

# create client and request data 
client = oauth.Client(consumer, token)

# determine loop count 
MAX_RESULTS_FROM_TWITTER = 100
desired_max_count = 10000
loopcount = desired_max_count / MAX_RESULTS_FROM_TWITTER 


# output HTML file for coords 
filename = searchTermShort + '_tweets_coords.html'
localfile = open(filename, 'w');


write_html_body_prefix(localfile)

coord_count = 0
for i in range(loopcount):
    header, contents = client.request(url, method="GET")
    data = json.loads(contents)

    results = len(data['statuses'])    
    for j in range(results):
        if data['statuses'][j]['coordinates'] != None :
            coords = data['statuses'][j]['coordinates'].values()[1]
            lng = coords[0]
            lat = coords[1]
            write_coord(lng, lat, coord_count, localfile)
            tweet_text = data['statuses'][j]['text']
            
            # need unicode encoding for tweet text 
            write_text_as_td(tweet_text.encode('utf8'))
            coord_count = coord_count + 1

    if results < 100:
        break

    next_id = data['statuses'][results - 1]['id']
    oldest_tweet_date = data['statuses'][results - 1]['created_at']
    url = makeurl(searchTerm, next_id)

write_html_body_suffix(localfile)

# done generating all output, close file 
localfile.close()

# use OS system call to concatenate generated file (HTML <body>) with file containing 
# JavaScript with calls to Google Maps API
viz_file_name = searchTermShort + '_tweets_map.html'
cat_command = "cat viz_script_marker.html " + filename + " > "  + viz_file_name
os.system(cat_command)
