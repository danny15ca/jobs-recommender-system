from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import re

origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000/api/recommend",
    "http://localhost:4200",
    "http://localhost:4200/jobs",
]

# Declaring our FastAPI instance
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Creating class to define the request body
# and the type hints of each attribute
class UserData(BaseModel):
    user_skills : str
    user_education_level : str
    user_experience_level : str
    top_k : int

# Declare constants for all CSV Files' Path
OCCUPATION_FILE = "data/occupation.csv"
OCCUPATION_SKILLS_FILE = "data/occupation_skill.csv"
OCCUPATION_EXPERIENCE_FILE = "data/occupation_experience.csv"
OCCUPATION_EDUCATION_FILE = "data/occupation_education.csv"
OCCUPATION_JOB_POSTINGS_FILE = "data/occupation_jobposting_new.csv"

# Loading all the available csv files
occ_df = pd.read_csv(OCCUPATION_FILE, delimiter="|")
occ_skill_df = pd.read_csv(OCCUPATION_SKILLS_FILE, delimiter="|")
occ_exp_df = pd.read_csv(OCCUPATION_EXPERIENCE_FILE, delimiter="|")
occ_edu_df = pd.read_csv(OCCUPATION_EDUCATION_FILE, delimiter="|")

# Merging all of the above dataframes into one
jobs = occ_df.merge(occ_skill_df, on="OccupationCode")
jobs = jobs.merge(occ_exp_df, on="OccupationCode")
jobs = jobs.merge(occ_edu_df, on="OccupationCode")
jobs = jobs.rename(columns={"OccupationCode": "JobCode",
                            "OccupationTitle": "Title",
                            "OccupationDescription": "Description"})

# Vectorize the text features using TF-IDF
tfidf = TfidfVectorizer(stop_words="english")

# Concatenate 'Skill', 'Description', and 'EducationLevel' columns for each job
corpus = jobs["Skill"] + " " + \
            jobs["Description"] + " " + \
            jobs["EducationLevel"]
tfidf_matrix = tfidf.fit_transform(corpus)

def tokenize(text):
    # simple tokenization by splitting text based on spaces
    tokens = text.split()
    # remove non-alphabetic tokens and convert them to lowercase
    tokens = [token.lower() for token in tokens if token.isalpha()]
    return tokens

def check_titles(job_posting_title_arr, job_title_arr):
    for job_posting_title in job_posting_title_arr:
        for job_title in job_title_arr:
            if (job_posting_title != "") and \
                (job_posting_title != "and") and \
                (len(job_posting_title) > 3) and \
                (job_posting_title.lower() != "manager") and \
                (job_posting_title.lower() in job_title.lower()):
                return True
    return False

def add_new_posting(df, idx):
    new_posting = {}
    new_posting["p_title"] = df.iloc[idx, 1]
    new_posting["p_href"] = df.iloc[idx, 2]
    return new_posting
 
# Defining path operation for root endpoint
@app.get('/api/')
def main():
    return {'message': "Welcome to our Recommender System's API!"}
 
# Defining path operation for /name endpoint
@app.get('/api/{name}')
def hello_name(name : str):
    # Defining a function that takes only string as input and output the
    # following message.
    return {'message': f"Welcome to our Recommender System's API!, {name}"}

@app.post('/api/recommend')
def recommend(data : UserData):
    # user = {
    #     data.user_skills,
    #     data.user_education_level,
    #     data.user_experience_level
    # }
    # Convert the above object into a DataFrame
    # user_df = pd.DataFrame([data])

    # Vectorize user's skills
    # user_data = user_df["user_skills"] + " " + \
    #             user_df["user_education_level"] + " " + \
    #             user_df["user_experience_level"]
    user_data = data.user_skills + " " + \
                data.user_education_level + " " + \
                data.user_experience_level

    # Tokenize the concanated data by keeping only alphabetic tokens
    user_data_tokens = tokenize(user_data)
    # Concanate the above tokens into string again
    user_data = " ".join(user_data_tokens)
    # Vectorize the user data string
    user_skill_vector = tfidf.transform([user_data])

    # Choose top k-related jobs
    k = data.top_k

    # Calculate the cosine similarity between the user and each job based on
    # the text features and return indices of the jobs sorting in descending order
    cosine_similarity_indices = cosine_similarity(
                                    user_skill_vector, \
                                    tfidf_matrix).argsort()[0][::-1]
    # Drop duplicates in the Title column
    recommended_titles = jobs.iloc[cosine_similarity_indices]["Title"] \
                            .drop_duplicates()
    recommended_jobs = []
    # Looping through the job list tiles and take only K titles
    for i in range(0, k):
        recommended_jobs.append(recommended_titles.iloc[i])
    
    occ_postings_df = pd.read_csv(OCCUPATION_JOB_POSTINGS_FILE,
                                    delimiter="|",
                                    encoding="cp1252")
    
    job_recommended_list = {"jobs": []}
    for job in recommended_jobs:
        job_title_postings = {}
        job_title_postings["title"] = job
        job_title_postings["postings"] = []
        for i in range(occ_postings_df.shape[0]):
            # if occ_postings_df.iloc[i, 1].lower().split("-----")[0].strip().__contains__(job.lower()):
            #     new_posting = {}
            #     new_posting["p_title"] = occ_postings_df.iloc[i, 1]
            #     new_posting["p_href"] = occ_postings_df.iloc[i, 2]
            #     job_title_postings["postings"].append(new_posting)

            # Getting the job posting title that is in front of the '-----' symbol
            new_job_posting_title = occ_postings_df.iloc[i, 1].split("-----")[0]
            # Splitting the above job posting title by white space
            new_job_posting_title_splitted = new_job_posting_title.split()
            for jpt in new_job_posting_title_splitted:
                job_splitted = job.split()
                if jpt.find("/") != -1:
                    jpt_splitted = jpt.split("/")
                    if check_titles(jpt_splitted, job_splitted):
                        new_posting = add_new_posting(occ_postings_df, i)
                        job_title_postings["postings"].append(new_posting)
                else:
                    jpt_splitted = jpt.split()
                    if check_titles(jpt_splitted, job_splitted):
                        new_posting = add_new_posting(occ_postings_df, i)
                        job_title_postings["postings"].append(new_posting)
        job_recommended_list["jobs"].append(job_title_postings)
    
    return job_recommended_list

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
