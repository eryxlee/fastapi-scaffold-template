from fastapi import Depends, HTTPException, status  
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  
from jose import JWTError, jwt  
from datetime import datetime, timedelta  
from passlib.context import CryptContext  
from app.models import User, get_db  
  
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  
  
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  
  
SECRET_KEY = "your-secret-key"  # 替换成你的密钥  
ALGORITHM = "HS256"  
ACCESS_TOKEN_EXPIRE_MINUTES = 30  
  
async def get_current_user(token: str = Depends(oauth2_scheme)):  
    credentials_exception = HTTPException(  
        status_code=status.HTTP_401_UNAUTHORIZED,  
        detail="Could not validate credentials",  
        headers={"WWW-Authenticate": "Bearer"},  
    )  
    try:  
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  
        user_id: str = payload.get("sub")  
        if user_id is None:  
            raise credentials_exception  
        db = get_db()  
        user = await db.query(User).filter(User.id == user_id).first()  
        if user is None:  
            raise credentials_exception  
        return user  
    except JWTError:  
        raise credentials_exception  
  
async def get_current_active_user(current_user: User = Depends(get_current_user)):  
    if not current_user.is_active:  
        raise HTTPException(status_code=400, detail="Inactive user")  
    return current_user  
  
async def authenticate_user(form_data: OAuth2PasswordRequestForm = Depends()):  
    user = await get_db().query(User).filter(User.email
