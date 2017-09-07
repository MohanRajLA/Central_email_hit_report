import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date, timedelta
import pymysql
import ConfigParser



# Function to provide DB connection details
def py_db(HOST, USERNAME, PASSWD, PORT, DB_NAME):
    conn = pymysql.connect(HOST, user=USERNAME,
                           passwd=PASSWD, db=DB_NAME, connect_timeout=5)
    cursor=conn.cursor()
    return conn,cursor

#SQL Query to fetch the results from the DB
def selectHearusFrom(conn,cursor,query):
    cursor.execute("SET @cnt:=0")
    cursor.execute(query)
    stmt=cursor.fetchall()
    return stmt


#Function to send email in HTML display format to recipients
def py_mail(SUBJECT, BODY, TO, FROM, SMTP_SSL_HOST, SMTP_SSL_PORT, PASSWD):
    MESSAGE = MIMEMultipart('alternative')
    MESSAGE['subject'] = SUBJECT
    MESSAGE['To'] =TO
    MESSAGE['From'] = FROM
    # Record the MIME type text/html.
    HTML_BODY = MIMEText(BODY, 'html')

    # Attach parts into message container.
    MESSAGE.attach(HTML_BODY)

    # The actual sending of the e-mail
    server = smtplib.SMTP_SSL(SMTP_SSL_HOST+':'+SMTP_SSL_PORT)
    password = PASSWD

    server.login(FROM, password)
    server.sendmail(FROM,TO.split(',') , MESSAGE.as_string())
    server.quit()

def htmlTop(SUBJECT):
    yesterday = date.today() - timedelta(1)
    yest_date = yesterday.strftime('%Y-%m-%d')
    todays_date = date.today().strftime('%Y-%m-%d')
    head_content = """\
          <html>
            <head></head>
            <body>
              <p><div style=\"line-height:0px\"><p><h2><font color=\"blue\">"""+str(SUBJECT)+"""</font></h2><p><b><font color=\"blue\">
                 (""" + str(yest_date) + """ 9:01 PM - """ + str(todays_date) + """ 9:00 PM )</font></b></p>
                 </div>"""
    return head_content

def htmlTail():
    tail_content="""</p>
          </body>
        </html>"""
    return tail_content



def displayHearusfrom(stmt,SUBJECT):
    htable=htmlTop(SUBJECT)
    header = u'<table border ="0" cellspacing="0"><tr><th align ="center" bgcolor="#00FFFF"><b> No.     	</b></p></th>' \
             u'<th align ="center" bgcolor="#00FFFF"><b> 	Media   	</b></p></th>' \
             u'<th align ="center" bgcolor="#00FFFF"><b>      Count   	</b></p></th></tr >'
    htable += ' '.join([header])
    total=0
    for row in stmt:
        newrow = u'<tr>'
        newrow = newrow + ' '.join([u'<td align="center">' + "   "+unicode(x)+ "  " + u'</td>' for x in row])
        total += x
        newrow += u'</tr>'
        htable += newrow
    htable += u' <tr><td></td><td align ="right" bgcolor="#FFFFFF"><b> 	Total   	</b> </td>' \
              u'<td align ="center">'+   str(total)  +'</td></tr>'
    htable += u'</table>'
    htable += htmlTail()
    return htable


def lambda_handler(event,context):


    config=ConfigParser.RawConfigParser()
    config.read('config.properties')
    conn,cursor=py_db(config.get('db-config','HOST'), config.get('db-config','USERNAME'), config.get('db-config','PASSWD'), config.get('db-config','PORT'), config.get('db-config','DB_NAME'))

    # ---------------------------------------------------- Jakarta--------------------------------------------------------------
    # call JKTLAquery
    LAstmt = selectHearusFrom(conn, cursor, config.get('query-config', 'JKTLAquery'))
    LAAstmt = selectHearusFrom(conn, cursor, config.get('query-config', 'JKTLAAquery'))
    ESYNCstmt = selectHearusFrom(conn, cursor, config.get('query-config', 'JKTESYNCquery'))

    # call JKTSUBJECT
    displayHearusfrom(LAstmt, config.get('email-config', 'JKTLA_SUBJECT'))
    displayHearusfrom(LAAstmt, config.get('email-config', 'JKTLAA_SUBJECT'))
    displayHearusfrom(ESYNCstmt, config.get('email-config', 'JKTESYNC_SUBJECT'))

    # send JKT LEADS mail
    py_mail(config.get('email-config', 'JKTLA_SUBJECT'), displayHearusfrom(LAstmt, config.get('email-config', 'JKTLA_SUBJECT')),
                config.get('email-config', 'JKT_TO'), config.get('email-config', 'JKT_FROM'),
                config.get('email-config', 'SMTP_SSL_HOST'), config.get('email-config', 'SMTP_SSL_PORT'),
                config.get('email-config', 'JKT_PASSWD'))
    py_mail(config.get('email-config', 'JKTLAA_SUBJECT'),
                displayHearusfrom(LAAstmt, config.get('email-config', 'JKTLAA_SUBJECT')),
                config.get('email-config', 'JKT_TO'), config.get('email-config', 'JKT_FROM'),
                config.get('email-config', 'SMTP_SSL_HOST'), config.get('email-config', 'SMTP_SSL_PORT'),
                config.get('email-config', 'JKT_PASSWD'))
    py_mail(config.get('email-config', 'JKTESYNC_SUBJECT'),
                displayHearusfrom(ESYNCstmt, config.get('email-config', 'JKTESYNC_SUBJECT')),
                config.get('email-config', 'JKT_TO'), config.get('email-config', 'JKT_FROM'),
                config.get('email-config', 'SMTP_SSL_HOST'), config.get('email-config', 'SMTP_SSL_PORT'),
                config.get('email-config', 'JKT_PASSWD'))


    cursor.close()
    return "success"
