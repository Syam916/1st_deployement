import pytest
from app import app
from app import *

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_register(client):
    # Clean up the user if it exists
    connection = get_db_connection()
    cursor = connection.cursor()

    # Use parameterized query to delete the user
    cursor.execute("DELETE FROM users WHERE username = %s", ('akhilesh',))

    connection.commit()
    cursor.close()
    connection.close()


    # Register the user
    response = client.post('/register', data={'username': 'akhilesh', 'password': 'akhilesh123'})
    
    # Check for success message
    assert b"Registration successful" in response.data

    # Try registering the same user again to check error handling
    response = client.post('/register', data={'username': 'akhilesh', 'password': 'akhilesh123'})
    assert b"Error" in response.data or b"already exists" in response.data


def test_login(client):
     # Test login
    response = client.post('/login', data={'username': 'syam', 'password': 'syamp916'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Math Operations" in response.data  # Check for successful login page content

def test_math_operations(client):
# Simulate login and maintain session
    client.post('/login', data={'username': 'syam', 'password': 'syamp916'})

    # Test math operations
    response = client.post('/math', data={'num1': 5, 'num2': 3, 'operation': 'add'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Result" in response.data
    assert b"8.0" in response.data

def test_logout(client):
    client.post('/register', data={'username': 'syam', 'password': 'syamp916'})
    client.post('/login', data={'username': 'syam', 'password': 'syamp916'})
    response = client.get('/logout')
    assert response.status_code == 302  # Redirect to login
