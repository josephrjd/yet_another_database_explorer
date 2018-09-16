# What is this?
This is a backend service built on django with following in mind and expose the features as HTTP APIs
###### Requirement
Write a multi tenant backend for a companies and their employees using libraries/framework of your choice in python. 
- Also write a usable frontend for it. (Libraries and frameworks at your discretion.) 
- Should contain the following features at the very least. 
- Your code will be evaluated on readability, testability and design decisions (especially for performance)
- An overall admin who can add and remove companies.
- An admin of a company who can Invite, add and remove employees.
- Employees who can edit their profile and update their details.
Teams - Use reasonable assumptions for features in this particular task

# How does this service work?

    CLIENT    |                          1. Login(pass credential)                      |  BACKEND SERVICE
              |   ------------------------------------------------------------------>   |      (APIs)
              |                                                                         |
              |                          2. JWT(token)                                  |
              |   <------------------------------------------------------------------   |
              |                                                                         |  
              |                                                                         |      
              |                          3. Request an API(pass token as header)        |
              |   ------------------------------------------------------------------>   | ------
              |                                                                         |      |
              |                                                                         |   Is the user authenticated
              |                                                                         |   and authorized to access the API
              |                                                                         |      |           |
              |                          4.a. Respond with result                       |      |YES        |NO
              |   <------------------------------------------------------------------   |<------           |
              |                                                                         |                  |
              |                          4.b. Respond with unauthorised/bad request     |                  |
              |   <------------------------------------------------------------------   |<------------------
              
# How is the DB schema defined?
                                                    -------------------
                                                    |  DimUserType    |
                                                    -------------------
                                                    | id (PK)         |                
                                                    | user_type       |
                                                    | description     |
                                                    -------------------
                                                             |
                                                             |
                                                            /|\                                                    
        ----------------------                      -------------------
        |  User              |                      | UserTypeMapping  |
        ----------------------                      --------------------
        | id (PK)            |                      | id (PK)          |
        | username           |--------------------|-| user (FK)        |
        | email              |                      | user_type (FK)   |
        | password(encrypted)|                      | company (FK)     |
        | first_name         |                      -------------------- 
        | last_name          |                              \|/
        ----------------------                               |
                                                             |
                                                    -------------------
                                                    |  DimCompany     |
                                                    -------------------
                                                    | id (PK)         |                
                                                    | company_name    |
                                                    | description     |
                                                    -------------------

