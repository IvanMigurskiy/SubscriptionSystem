FROM python:3.11-alpine

ENV TZ=Europe/Moscow
ENV PYTHONPATH=/work_dir

RUN mkdir work_dir
WORKDIR /work_dir
COPY system system

RUN addgroup -g 1000 user && adduser -h /home/user -u 1000 -G user -s /bin/sh -D user
RUN addgroup -g 1001 docker && addgroup user docker
RUN chown -R user:user /var
RUN chown -R user:user /work_dir

RUN ln -sf /proc/1/fd/1 /var/log/container_logs.log

USER user

RUN pip install wheel setuptools pip --upgrade
RUN pip install -r system/requirements.txt

CMD [ "python", "system/main.py" ]