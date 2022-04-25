Program Use: Creates a buying and selling platform for users in a local region
Status: Full Prototype Implemented

Program Info:
    Login Verification: Successfully determines if username and password are valid. Also determines if the user has a
                        valid seller account before being able to preform seller actions.

    Listing a New Product: Ensures fields are filled in. Verifies that Category is a valid category

    Check Info: Displays a user's information. The password update works correctly and hashes the password for
                data security. The user has to enter their password twice and the same way before it is
                allowed to update to prevent typos.

    Browse Products: The users can select a category to get all the in it and its sub categories.

Program Design: The program uses an individual webpage for every action and then goes to a successful or
                unsuccessful webpage depending on validity then loops back on itself or follows the path depending on
                appropriate action. The webpage system also provides checks to ensure that incorrect Users can not
                preform certain actions(i.e. A buyer cannot list new Product). The webpages act as nodes in a directed
                graph with buttons preforming actions being the edges taking us around the graph. There are loops
                throughout allowing the user to navigate correctly through the whole program.