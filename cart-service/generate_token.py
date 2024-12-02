# generate_token.py
import jwt
import datetime

def generate_test_token():
    token = jwt.encode(
        {
            'user_id': 1,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)  # Token valid for 24 hours
        },
        'e1a00e39bd827b47334cff98872e82ac4568ea673115f88b04769f89714d6a1a',
        algorithm='HS256'
    )
    return token

if __name__ == "__main__":
    token = generate_test_token()
    print(f"\nTest Token: {token}\n")
