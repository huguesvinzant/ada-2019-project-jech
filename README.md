# A short guide on where to safely eat delicious food in Chicago

Supporting notebook with extensive analysis: `Descriptive Analysis.ipynb`  
Link to data story: https://huguesvinzant.github.io/ada-2019-project-jech/

# Abstract
Whether being a simple tourist or long-standing inhabitant of a big city, everybody cares about eating delicious food while staying safe from both food poisoning or the like and neighborhood criminality. In this project, our goal is to offer a better overall understanding of Chicago's food places by combining insights from three different datasets. After an analysis of the evolution of food safety since 2010, we will aim to explore the correlation of inspection data on food facilities with Yelp restaurant ratings to see whether the ratings somehow reflect the outcomes of the authority’s controls. In order to provide a better overview of safety in the city, we will also investigate the geographical distribution of crime rates and superimpose these results to the food safety and Yelp rating results. Accordingly, the final project would entitle the reader to knowledge on general public and food safety, thus ensuring a better experience within the city and its neighbourhoods, for tourists or inhabitants.

# Research questions
## General food safety analysis:
- How did the food safety in Chicago evolve geographically since the year 2010? Does the same area/restaurants remain safe over time?
- Are large food chains or specific cuisine types more prone to fail food inspections?

## Correlation analysis between the three datasets:
- Are there correlates between the food inspection fail rate of areas and public safety, measured through crime rates?
- Are there correlates between the food inspection fail rate of areas and online Yelp ratings of restaurants?

## Concluding analysis:
- Where can one safely eat delicious food in Chicago?
- Do certain neighborhoods offer a better overall dining experience based on customer reviews, and food as well as neighborhood safety? 


# Dataset

We intend to use the following three different datasets, where the first two are obtained from the Chicago data portal:

## Chicago Food Inspections (CFI): 
This will be our main [dataset](https://www.kaggle.com/chicago/chicago-food-inspections), where the information is derived from inspections of restaurants and other food establishments in Chicago from January 1, 2010 to the present. Inspections are performed by staff from the Chicago Department of Public Health’s Food Protection Program using a standardized procedure. This dataset contains 22 columns and 194’615 rows (updated frequently, so subject to change). The set is in a simple csv file, which makes it easy to read using Pandas. The dataset is maintained in Kaggle via two APIs: Socrata’s API and Kaggle’s API. In this dataset, we have information on the location of the restaurants, where 7 columns contain spatial indicators, excluding the columns on the community area and zip codes, which are full of NaN values and will hence be disregarded. Information on the inspections consist of 5 columns including the inspection type, date, id, results and possible violations. The remaining columns are related to the restaurant itself, including the facility type, licence number, DBA, AKA names and risk.

## Crimes: 
This [dataset](https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-present/ijzp-q8t2) reflects reported incidents of crime that occurred in the City of Chicago from 2001 to present, and is updated daily with a seven-day lag. For our project, we will however only focus on the data from January 1, 2010 onwards to match with the CFI dataset. Data is extracted from the Chicago Police Department's CLEAR system and due to privacy concerns, addresses are only shown at the block level. This level of resolution is however more than sufficient for the analyses we aim to undertake. The whole dataset includes almost 7M entries and 30 columns, but only roughly 3M entries pertain to our study period. The columns contain information regarding the time and type of the incidence (using the Illinois Uniform Crime Reporting code, IUCR). It also reports various location measures at different aggregation levels, where the latitude and longitude as well as the community area code will be of greatest importance for our intended analysis framework.  

## Yelp Reviews (YR): 
Yelp.com is a website that helps people find great local businesses such as restaurants based on customer reviews. Each business has a page where visitors can write comments and add a general grade reflecting their experience there. We can access these business ratings through their Yelp Fusion API for all businesses with at least one review. The API also gives us other relevant information such as the number of reviews, which will be a factor taken into account while ranking the restaurants. Moreover, it is possible to search for the businesses via their latitude and longitude location data, which is of great interest in our project framework, as our main CFI dataset contains the latitude and longitude of the restaurants as well. A more detailed description of the API can be found [here](https://www.yelp.com/developers/documentation/v3/business_search).


# A list of internal milestones 
**Due by Monday, November 4**

- Clean CFI dataset
- Set up blog skeleton for data story

**Due by Monday, November 11**

- Clean crime dataset
- Scrape Yelp website to get YR dataset

**Due by Monday, November 18**

Descriptive analysis of: 
- evolution of the food inspection results
- food chains / food categories (type of cuisine, facility type etc.)
- a possible correlation of hygienic standards of the food places and their respective customer reviews
- patterns of neighborhood crime rates 

**Due by Monday, November 25**

- Prepare first data visualisations for the notebook
- Set up goals and plans for the second milestone
- Discuss narrative of the data story based on the analysis results
- Finalize notebook with descriptive analysis to hand in
---

**Milestone 2 - Review:**

Working on three datasets simultaneously has proven to be quite a demanding and non-trivial task. The two datasets from the Chicago Data Portal required some data cleaning and wrangling to make it ready for our analyses but have proven to suit well our project needs. The Yelp reviews are extremely challenging to obtain and it has taken us several attempts before we managed to properly scrape the data. But we believe it is worth the effort as this will truly add a valuable element to our analysis. Our initial idea depicted in the README still fits with the current state of our project and we believe it is possible to attain our goals. In the next weeks, we will intensively work on performing correlation analyses among the three datasets to understand the underlying patterns. As an ultimate goal, we also aim to build some kind of recommender system that allows a tourist to get a tailored recommendation on where to eat deliciously, while staying safe in Chicago, based on their food preferences.

---

**Due by Friday, Nov 29**

- Finish to scrap yelp and clean it
- Merge yelp dataset with CFI by adding info on reviews and cuisine type
- Do a more advanced correlation analysis of reviews and food inspections outcomes

**Due by Friday, Dec 06**

- Finish the analysis on food chains and cuisine types
- Perform correlation analysis of crimes and food inspections outcomes on the community area level
- Create all interactive plots for the data story
- Draft a plan for the data story


**Due by Friday, Dec 13**

- Wrap up the analysis and code a recommender system 
- Write the data story around the plots


**Due by Friday, Dec 20 - Project deadline**

- Finalize items to hand in: data story and final notebook 


**Due by Monday, Jan 20 - Poster presentation**

- Design a project poster
- Prepare the 3-minute presentation


# Contributions of group members

- Camille: CFI pre-processing & analysis; elaboration of CFI score; write data story
- Eliane: crimes dataset pre-processing & analyis; folium plots; write data story
- Hugues: CFI pre-processing, food chains analysis; website for data story
- Jérémie: Yelp reviews scraping, pre-processing & analysis; folium plots

We will all together design the poster and prepare the 3-minute presentation.

# Questions for TAa
- Is there a way to automatically launch the Yelp Fusion API everyday? As we are limited to 5’000 requests per day and our CFI dataset contains inspections of roughly 30’000 different food establishments, this would mean that we need at least 6 days to obtain all ratings.
- When doing a comparative analysis, how can we best deal with the fact that all three measures (Yelp rating, sanitation risk level and crime rate) fluctuate and may change over time? Would it be a good approach to look at the averaged data over the last two years (since this corresponds to the maximum interval for food inspections) to analyse whether there is any correlation between the measures?

