
# 📚 Glassdoor

This is a personal effort where I researched "Data Analyst" job openings in Melbourne. As a result, this project shows minimum and maximum salary of a Data Analyst in Melbourne, Australia according to job advertisements gathered from https://www.glassdoor.com.au/ and saves the results in a PostgreSQL database in order to have historical data for further analysis. 

![image](https://github.com/emadam/glassdoor/blob/master/glassdoor2022-03-28.png)
<br>
App home: https://data-jobanalyst.herokuapp.com/
   

### ENV Variables
Create `.env` file
```
touch .env
```
Inside `.env`, set these variables.
```
server = your_own_server_name
database = your_own_database_name
pymssql_username = your_own_sql_username
pymssql_password = your_own_sql_password
```

### Data Sources
- <a href="https://www.glassdoor.com.au/">www.glassdoor.com.au/</a>


## Built With
- <a href="https://streamlit.io/">Streamlit</a>
- [Heroku](https://heroku.com/) - Deployment
- [MSSQL](https://www.microsoft.com/en-au/sql-server/) - Database


## Team Members
- [EMAD AMINMOGHADAM](https://www.linkedin.com/in/emad-aminmoghadam/)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


