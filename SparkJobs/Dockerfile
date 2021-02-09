FROM sdesilva26/spark_submit:0.0.2

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9998

CMD [ "python", "./streaming.py" ]