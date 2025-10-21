import pandas as pd
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Annotated
from user_auth import authenticate_user, get_current_user, fake_users_db, Token, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, UserLogin,User
from datetime import timedelta

# Initialize FastAPI application
app = FastAPI(
    title="Sales Data Server",
    description="Server to provide sales data from a CSV file.",
    version="1.0.0"
)

# CSV file location
CSV_FILE_PATH = "server/data_penjualan.csv"

@app.get("/get-sales-data", tags=["Data"])
def get_sales_data(
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint to read sales data from a CSV file and send it as JSON.
    """
    try:
        # Read data from CSV file using pandas
        df = pd.read_csv(CSV_FILE_PATH)
        
        # Convert dataframe to JSON format
        data_json = df.to_dict(orient="records")
        
        print("Successfully read data and sent it to the client.")
        return JSONResponse(content=data_json)

    except FileNotFoundError:
        print(f"Error: File {CSV_FILE_PATH} not found.")
        raise HTTPException(status_code=404, detail=f"File {CSV_FILE_PATH} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    

@app.post("/token")
async def login_for_access_token(
    user_login: UserLogin
) -> Token:
    user = authenticate_user(fake_users_db, user_login.username, user_login.password)
    if not user:
        print("Authentication failed for user:", user_login.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
