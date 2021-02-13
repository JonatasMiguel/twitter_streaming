FROM sdesilva26/spark_submit:0.0.2

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9998

CMD [ "$SPARK_HOME/bin/spark-submit --conf spark.executor.cores=3 --conf spark.executor.memory=5G --master spark://spark-master:7077", "streaming.py" ]