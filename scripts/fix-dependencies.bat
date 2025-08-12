@echo off
echo Fixing Python dependencies for Windows...

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing/upgrading required packages...
pip install --upgrade pydantic-settings==2.1.0
pip install --upgrade pydantic==2.5.0
pip install --upgrade fastapi==0.104.1
pip install --upgrade uvicorn==0.24.0

echo Installing all requirements...
pip install -r requirements.txt

echo Verifying installation...
python -c "from pydantic_settings import BaseSettings; print('pydantic-settings installed successfully')"
python -c "import pydantic; print(f'Pydantic version: {pydantic.VERSION}')"

echo Dependencies fixed successfully!
echo You can now run: uvicorn app.main:app --reload
pause
