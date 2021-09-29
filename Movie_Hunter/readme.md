# Movie Hunter project

This repository contains everything about the 'Movie Hunter' project as I developped. 'Movie Hunter' enalbes a user to rate movies among a database of 85,000 references and computes customed recommandations based on three algorithms :
1. Collaborative filtering (based on truncated SVD)
2. Item-based (distance between movies)
3. Item-based on synopsis (distance between tf-idf of movies synopsis)

### demo

This folders contains a presentation of the project along with a recorded demo.

### django_app

Code source for the web app developed using Django framework. This app is fully functional (creation of users, rate movies, get recommendations).

### SVD

Studies conducted for the implementation of a collaborative filtering algorithm using Truncated SVD.

### Others

Contains notebook regarding :
1. Item-based models ('distance' between movies features and between synopsis)
2. Data processing in order to feed the app database with data from IMDb and from the different models accordingly to the architecture of the database developped.
