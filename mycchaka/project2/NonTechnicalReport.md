# Non Technical Report
## On the prediction of probable salaries for job listings.

As we are all aware, our contracting firm is expanding at a tremendous pace, and the task of estimating the probable salary of a particular job has placed a great strain on our human resources. As requested, I have used machine learning to build a model that - given a job title and job location - will output a crude prediction of the salary a candidate might be offered if their application is successful.

The information we used to develop this model was obtained by scouring through 6800+ job listings for Data Scientist posted at Indeed.com, corresponding to the cities of London, Liverpool, Leeds, Manchester and Edinburgh. However, only 480 job listings included salary information, and thus we were not able to make any use of the other 6300+ jobs we found.

This lack of salary information was by far the biggest obstacle in our task. Without a larger amount of data with which to calibrate our model, subtle differences between job listings could not be explored without sacrificing having a useful model capable of reasonably accurate predictions on new data. In the end our model is able recognize 50 carefully selected words from a job's title, together with the job's city, to predict whether a candidate will be offered a yearly salary in the range of:
    
     0 to 25k
     25k to 35k
     35k to 50k
     50k to 75k
     65k to 75k
     75k+
    
In doing so our model predicts the correct salary bracket in approximately 54.6% of the data - a significant improvement on merely assuming all jobs land within the most common salary range (75k+), which would have resulted in 29% accuracy. Due to our rigorous process of testing, we expect the model to retain this performance when exposed to new data.

Two avenues of improvement are available at this time: to increase the accuracy of the model, and to increase the specificity of the predictions. For either, we would request additional resources - such as an experienced member of our firm - to help us to manually estimate salaries for more jobs. With sufficient data we could look into the subtle differences between job listings, such as the inclusion of other words in the title, the specific location within each city, and even the content of the job description.