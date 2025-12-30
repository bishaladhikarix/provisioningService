
This is a fastapi provisioning server code to create new-site, user and install apps upon request.




How to run:
#
pip install fastapi uvicorn pydantic(install dependency)
#
uvicorn provisioning:app --host 127.0.0.1 --port 9010 (to run this server)

#

POST:http://127.0.0.1:9010/createsite


requestBody:
{
  "site_name": "superthing.localhost",
  "apps": ["something"],
  "email": "godb@gmail.com",
  "password": "hello@123",
  "first_name":"Godb"
}
