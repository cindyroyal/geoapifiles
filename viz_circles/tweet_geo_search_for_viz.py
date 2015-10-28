# 
# @author Apan Qasem
# @date 10/15/14
#    
# Program collects data via the Twitter search API and generates an HTML file. 
# A geo-specific search is performed to collect the data 
# 
# The HTML file contains number of tweets from a specific location 
# The generated HTML file is concatenated with another file that contains the visualization script
# 

from __future__ import division
import oauth2 as oauth        # oauth authorization needed for twitter API
import json                   # converting data into json object 
from pprint import pprint     # pretty print 
import os                     # for contatenating generated files 
import sys


searchTerm = "world series"
searchTermShort = "series"


# my keys, need all four of them. Use your own keys here.
consumer_key = "ohaVzTnC95piiNDv967FBZNsC"
consumer_secret = "FNXcMvYXYm2ZE1jK243XcheboNu2EUSexga1CP2xXHfpCfr8QO"
token_key = "1246761-39k6SCDVPLh8yIzuzRDZCVzX2Sukll6e2gPyz3zNEB"
token_secret = "MpO6F1Mb4VmD3mGsbsevepSKp3gI9VfCTigbMyz2oArcy"

#
# function to construct search url 
#   - count value is always set to 100 
#   - default value for max_id is 0
#   - default value for geo is 0
#
def makeurl(searchterm, geo=0, max_id=0) :
    baseurl = "https://api.twitter.com/1.1/search/tweets.json"
    count = "100"
    if max_id == 0:
        if geo == 0:
            url = baseurl + '?q=' + searchterm + '&' \
                  + 'count=' + count    
        else:
            url = baseurl + '?q=' + searchterm + '&' \
              + 'geocode=' + geo + '&' \
              + 'count=' + count  
    else:
        if geo == 0:
            url = baseurl + '?q=' + searchterm + '&' \
                  + 'max_id=' + str(max_id) + '&' \
                  + 'count=' + count    
        else:
            url = baseurl + '?q=' + searchterm + '&' \
              + 'max_id=' + str(max_id) + '&' \
              + 'geocode=' + geo + '&' \
              + 'count=' + count  
    return url 


#
# Following functions generate HTML output 
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
# write coordinates and radius value in three table cells inside table row
# 
def write_radii_and_geocode(radii, geocodes, localfile):
    for i in range(len(radii)):
        localfile.write("<tr id = \"city" + str(i) + "\">\n")
        localfile.write("<td id = \"radii\"" + ">")
        localfile.write(str(radii[i]))
        localfile.write("</td>")

        geocode = geocodes[i].split(",")
        localfile.write("<td id = \"lng\"" + ">")
        localfile.write(geocode[1])
        localfile.write("</td>")

        localfile.write("<td id = \"lat\"" + ">")
        localfile.write(geocode[0])
        localfile.write("</td>\n")

        localfile.write("<td id = \"sRadius\"" + ">")
        localfile.write(geocode[2])
        localfile.write("</td>\n")
        localfile.write("</tr>\n")
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
    localfile.write("<div id = \"map\" style=\"height: 512px\"><iframe src=\"" + searchTermShort + "_tweets_map.html\"></iframe></div>")
    localfile.write("<table id = \"cTable\">\n")
    return 

#
# end table element 
# end body
#
def write_html_body_suffix(localfile) :
    localfile.write("</table>\n")
    localfile.write("</body>\n")
    return 
    


# set up oauth tokens
token = oauth.Token(token_key, token_secret)
consumer = oauth.Consumer(consumer_key, consumer_secret)


# create client and request data 
client = oauth.Client(consumer, token)

# determine loop count 
MAX_RESULTS_FROM_TWITTER = 100
desired_max_count = 3000
loopcount = desired_max_count // MAX_RESULTS_FROM_TWITTER 

# output HTML file for coords 
filename = searchTermShort + '_tweets_geo.html'
localfile = open(filename, 'w');

write_html_body_prefix(localfile)

city_geocodes = ["47.6097,-122.3331,15mi", 
                 "30.2500,-97.7500,15mi", 
                 "29.45,-95.21,20mi", 
                 "32.7758,-96.7967,20mi",
                 "40.7127,-74.0059,20mi" ]

results = []
j = 0
for geo_code in city_geocodes: 
    results.append(0)
    url = makeurl(searchTerm, geo_code)
    for i in range(loopcount):
        resp, contents = client.request(url, method="GET")
        data = json.loads(contents)

        cur_results = len(data['statuses'])
        results[j] = results[j] + cur_results;

        if cur_results < 100:
            break

        next_id = data['statuses'][cur_results - 1]['id']
        oldest_tweet_date = data['statuses'][cur_results - 1]['created_at']
        url = makeurl(searchTerm, geo_code, next_id)
    
    j = j + 1
    
num_cities = len(city_geocodes)

# normalize total tweet count
total = sum(results[0:])
radii = []
for k in range(num_cities):
    radii.append((results[k]/total) * 100)

write_radii_and_geocode(radii, city_geocodes, localfile)


write_html_body_suffix(localfile) 

# done generating all output, close file 
localfile.close()

# use OS system call to concatenate generated file (HTML <body>) with file containing 
# JavaScript with calls to Google Maps API
viz_file_name = searchTermShort + '_tweets_map.html'
cat_command = "cat viz_script_circles.html " + filename + " > "  + viz_file_name
os.system(cat_command)
