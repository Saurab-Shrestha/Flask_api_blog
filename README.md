# Flask Blog API

This is a Flask_based API for a blog application that allows users to register, login, and create posts with CRUD operations.

## Installation
1. Clone the repository:

```
git clone https://github.com/Saurab-Shrestha/Flask_api_blog.git
```

2. Navigate to the project directory:
```
cd flask_blog
```

3. Create a virtual environment and activate it:
```
python -m venv venv
source venv/Scripts/activate # for windows
```

4. Install the required packages:
```
pip install -r requirements.txt
```

5. Initialize the database:
```
flask init-db
```

## Usage
1. Start the server:
```
flask run
```

2. Open a web browser or Postman and navigate to `http://localhost:5000` to use the API.

## Endpoints
The API has the following endpoints:

### Authentication
- `POST /register` - Register a new user.
- `POST /login` - Log in an existing user.
- `POST /logout` - Log out the current user.

### Posts
- `GET /posts` - Retrieve a list of all posts.
- `GET /posts/<int:id>` - Retrieve a single post by ID.
- `POST /posts` - Create a new post.
- `PUT /posts/<int:id>` - Update an existing posty by ID.
- `DELETE /posts/<int:id>` - Delete a post by ID.

### Pagination
- `GET /posts?page=<int:page>&per_page=<int:per_page>` - Retrieve a paginated list of posts.

