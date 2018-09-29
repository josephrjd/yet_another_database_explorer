# What is this?
This is a backend service built on django with following in mind and expose the features as HTTP APIs
###### Requirement
Multi tenant backend for a companies and their employees with following in mind
- Testability
- An overall admin who can add and remove companies.
- An admin of a company who can Invite, add and remove employees.
- Employees who can edit their profile and update their details.

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

