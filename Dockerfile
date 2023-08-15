FROM python:3.11.4-slim
WORKDIR /app/

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple && pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]