# Core Python module 
import pickle
from pathlib import Path 

import streamlit_authenticator as stauth

users = ["fernando","miceli"]
usernames = ["lisboa","luciana"]
passwords = ["lisboa2311","luciana2311"]

#convert plain text passwords to hashed passwords 
hashed_passwords= stauth.Hasher(passwords).generate()
# streamlit_authenticator used bcrypt for password hashing 


file_path=Path(__file__).parent / "hashed_passwords.pkl"

with file_path.open("wb") as file:
	pickle.dump(hashed_passwords,file)