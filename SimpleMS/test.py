# import pymongo (Pip install first)

# client = pymongo.MongoClient(
#         "mongodb+srv://jxyong2021:Rypc9koQlPRa0KgC@esdg5.juoh9qe.mongodb.net/?retryWrites=true&w=majority")
#     db = client.get_database('<Db name>')
#     col = db['<Collection name>']

# *Db name and Collection name for each database is in the database planning doc

# To find all items in the collection:
#     for item in col.find():
#         print(item)

# To find item by query (e.g. find all pets in Pet db which are dogs):
#   pet_db = client.get_database('pet_db')
#   pet_col = pet_db['pet']
#   dogs = pets_col.find('species':'dog')

# To edit/update value in the database (e.g. Change Pet Sitter's (Name: Daryl) Blocked status from false to true):
# pet_sitter_db=client.get_database('pet_sitter_db')
# pet_sitter_col=pet_sitter_db['pet_sitter']
# update_pet_sitter=pet_sitter_col.update_one({'Name':'Daryl'},{"$set":{'Blocked':True}})



# Python Program to Convert seconds
# into hours, minutes and seconds
 
# def convert(seconds):
#     seconds = seconds % (24 * 3600)
#     hour = seconds // 3600
#     seconds %= 3600
#     minutes = seconds // 60
#     seconds %= 60
     
#     return "%d:%02d:%02d" % (hour, minutes, seconds)
     
# # Driver program
# # n = 12345
# print(convert(n))