# Mattermost 
 slack 과 같은 오픈소스 메신저이다.

#### 관련정보
 - <https://mattermost.com/>
 - <https://github.com/mattermost?page=1>
 - <https://docs.mattermost.com/guides/administrator.html#installing-mattermost>
 - <https://www.howtoforge.com/tutorial/install-mattermost-with-postgresql-and-nginx-on-centos7/>
 - <https://qiita.com/murachi1208/items/3bdd57dc6bce0f44de1f?>

#### 설정
 - 먼저 루트계정으로 접속후 방화벽을 비활성화 합니다. 
```
# systemctl status firewalld
# systemctl stop firewalld
# systemctl disabel firewalld
```
 
 - PostgreSQL, MySQL DB중 하나를 설치하면된다.
 - PostgreSQL DB를 설치하는 방법
```
* 루트권한으로
# yum -y install postgresql-server postgresql-contrib
# postgresql-setup initdb
# systemctl start postgresql
# systemctl enable postgresql
# systemctl status postgresql
# su - postgres
-bash-4.2$ psql
postgres=# CREATE DATABASE mattermost;
postgres=# CREATE USER mmuser WITH PASSWORD 'Fourth4th!';
postgres=# GRANT ALL PRIVILEGES ON DATABASE mattermost to mmuser;
postgres=# \q
-bash-4.2$ exit
```

 - PostgreSQL configuration 변경
```
# vi /var/lib/pgsql/data/pg_hba.conf
	host all all 127.0.0.1/32 ~~ident~~ md5
#systemctl restart postgresql
# psql --host=127.0.0.1 --dbname=mattermost --username=mmuser --password
```

 - mattermost 설치
```
# tar -xvzf mattermost.tar.gz
# mv mattermost /opt
# useradd -r mattermost -U -s /sbin/nologin
# mkdir -p /opt/mattermost/data
# chown -R mattermost:mattermost /opt/mattermost
# chmod -R g+w /opt/mattermost
```
 - mattermost configuration 변경
 - postgresSQL 정보 입력
```
/opt/mattermost/config/config.json
```

 - **Before**
```
"SqlSettings": {
 "DriverName": "mysql",
 "DataSource": "mmuser:mostest@tcp(dockerhost:3306)/mattermost_test?charset=utf8mb4,utf8",
 "DataSourceReplicas": [],
 "MaxIdleConns": 10,
 "MaxOpenConns": 10,
 "Trace": false,
 "AtRestEncryptKey": "7rAh6iwQCkV4cA1Gsg3fgGOXJAQ43QVg"
 },
```
 - **After**
```
"SqlSettings": {
 "DriverName": postgres, 
 "DataSource": "postgres://mmuser:Fourth4th!@127.0.0.1:5432/mattermost?sslmode=disable&connect_timeout=10",
 "DataSourceReplicas": [],
 "MaxIdleConns": 10,
 "MaxOpenConns": 10,
 "Trace": false,
 "AtRestEncryptKey": "7rAh6iwQCkV4cA1Gsg3fgGOXJAQ43QVg"
 },
```
 
 - email 연결구성 
 - **Before**
```
 "EmailSettings": {
 "EnableSignUpWithEmail": true,
 "EnableSignInWithEmail": true,
 "EnableSignInWithUsername": false,
 "SendEmailNotifications": false,
 "RequireEmailVerification": false,
 "FeedbackName": "",
 "FeedbackEmail": "",
 "SMTPUsername": "",
 "SMTPPassword": "",
 "SMTPServer": "",
 "SMTPPort": "",
 "ConnectionSecurity": "",
 "InviteSalt": "bjlSR4QqkXFBr7TP4oDzlfZmcNuH9YoS",
 "PasswordResetSalt": "vZ4DcKyVVRlKHHJpexcuXzojkE5PZ5eL",
 "SendPushNotifications": false,
 "PushNotificationServer":
},
```

 - **After**
```
"EmailSettings": {
 "EnableSignUpWithEmail": true,
 "EnableSignInWithEmail": true,
 "EnableSignInWithUsername": false,
 "SendEmailNotifications": false,
 "RequireEmailVerification": false,
 "FeedbackName": "",
 "FeedbackEmail": "",
 "SMTPUsername": "",
 "SMTPPassword": "",
 "SMTPServer": "127.0.0.1",
 "SMTPPort": "25",
 "ConnectionSecurity": "",
 "InviteSalt": "bjlSR4QqkXFBr7TP4oDzlfZmcNuH9YoS",
 "PasswordResetSalt": "vZ4DcKyVVRlKHHJpexcuXzojkE5PZ5eL",
 "SendPushNotifications": false,
 "PushNotificationServer": ""
 },
```

 - 내부 인터페이스 (127.0.0.1)에서만 수신 대기하도록 구성
```
"ListenAddress": "127.0.0.1:8065",
```

 - 퍼미션
```
# chown -R mattermost:mattermost /opt/mattermost
```

 - 데몬으로 설정
 - /etc/systemd/system/mattermost.service 파일 생성후 작성
```
[Unit]
Description=Mattermost
After=syslog.target network.target
```
```
[Service]
Type=simple
WorkingDirectory=/opt/mattermost/bin
User=mattermost
ExecStart=/opt/mattermost/bin/platform
PIDFile=/var/spool/mattermost/pid/master.pid
```
```
[Install]
WantedBy=multi-user.target
```

 - 데몬 재시작 및 mattermost 서비스 시작
```
# systemctl daemon-reload
# systemctl start mattermost.service
# systemctl status mattermost.service
# systemctl enable mattermost.service
```

 - mattermost 수신테스트
```
# curl -s "http://127.0.0.1:8065" | grep -b "Mattermost"
```

 - Ngix 서버 설치 : 포트매핑, 표준 요청 로그, SSL의 더많은 옵션제공등.
 ```
# yum -y install epel-release && yum update
# yum -y install nginx
```
 
 - Ngix 기본 구성 파일 변경
```
# cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak
```
```
 -- 구성내용 중 아래부분 수정--
 server {
 server_name mattermost.4thparty.co.kr;
 location / {
 client_max_body_size 50M;
 proxy_set_header Upgrade $http_upgrade;
 proxy_set_header Connection "upgrade";
 proxy_set_header Host $http_host;
 proxy_set_header X-Real-IP $remote_addr;
 proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
 proxy_set_header X-Forwarded-Proto $scheme;
 proxy_set_header X-Frame-Options SAMEORIGIN;
 proxy_pass http://127.0.0.1:8065;
 	}
 }
```

 - 구성 오류 확인 및 서비스
```
# nginx -t
# systemctl start nginx
# systemctl stasus nginx
# systemctl enable nginx
```
 
 - 방화벽 시작
```
# firewall-cmd --zone=public --add-port=80/tcp --permanent
# firewall-cmd --reload
```

