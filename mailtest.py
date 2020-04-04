
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import numpy as np
import pandas as pd
import config

def sendEmail(df, email, passwordy, errors_and_warnings, program_emails):
    emails_not_found = []
    # Create a list of all of the program names from df
    programs = df.Program.unique() # As df only includes bad stuff, programs with zero issues will not get an email.
    # Create a dict of program names: email recipients e.g. "Clearview (GH0079)":clearviewgh@scarc.org
    programEmails = program_emails# {"TEST GROUP HOME":["mnoah@scarc.org", "mnoah@scarc.org"], "Test Day Program":["Mnoah@scarc.org"]}
    # Create separate df from each program
    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.office365.com", 587) as server:
        sender_email = email
        password= passwordy
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        try:
            server.login(sender_email, password)
        except smtplib.SMTPAuthenticationError:
            errors_and_warnings['errors'].append("Could not login.  Check credentials and try again.")
            return errors_and_warnings
        except TypeError as terror:
            errors_and_warnings['errors'].append(f'Please enter valid email credentials and try again.')
            return errors_and_warnings
        except smtplib.SMTPSenderRefused:
            errors_and_warnings['errors'].append(f'Please enter valid email credentials and try again.')
            return errors_and_warnings
        for program in programs:
            #df = df[["Program Name"] == program]
            #df_html=df.to_html()
            try:
                receiver_email = programEmails[program.lower()]
            except KeyError as ke:
                errors_and_warnings['warnings'].append(str(ke))
                continue
            message = MIMEMultipart("alternative")
            message["Subject"] = "MONTHLY QA AUDIT"
            message["From"] = sender_email
            message["To"] = ", ".join(receiver_email)
            # Create the plain-text and HTML version of your message
            text = """\
            An HTML email could not be delivered.  Please reply to this email at your earliest convenience."""
            html =  '''<html><head><style>#customers {
  font-family: Arial, Helvetica, sans-serif;
  font-size: 12px;
  border-collapse: collapse;
  width: 90%;
}

#customers td, #customers th {
  border: 1px solid #ddd;
  padding: 8px;
}

#customers tr:nth-child(even){background-color: #f2f2f2;}

#customers tr:hover {background-color: #ddd;}

#customers th {
  padding-top: 12px;
  padding-bottom: 12px;
  text-align: left;
  background-color: #003366;
  color: white;
}"
</style>
</head>
</body>
<p>Please see below for the monthly data review of all of your program's documentation.  Issues do not need to be fixed.  Please review the issues/concerns moving forward.  Please see the flag descriptions at the bottom of the email.</p>
'''

            df_html = df[df["Program"]==program].to_html(index=False).replace("<table border", "<table id=customers border")
            notes = '''
            <ul>
              <li>
                DUPLICATED NOTES: there should only be one note per person per shift.  A duplicated note indicates that there are two notes for the same date and start time.
              </li>
              <li>
                DUPLICATED CONTENT: Vary your progress notes, make it more person-centered, etc.  Please do not copy-paste.
              </li>
              <li>
                FORM: the Progress Note - Residential form must be included with all progress notes except where otherwise indicated.
              </li>
              <li>
                SHORT NOTE: Generally, this is due to an additional progress note that was started and not finished.  Otherwise, check to see if notes are actually being completed.
              </li>
              <li>
                SERVICE TYPE: In group homes, we generally only provide the following services: Individual Supports, Behavioral Supports, Physical Therapy.  If the Service Type=Not Applicable, you will have to modify their plan in Plans and Reviews and choose the correct Service Type.
              </li>
              <li>
                PN's < 3: This is not always bad.  If there was no staff on a 7-3, for example, then this would be fine.  But if you know that that does not happen much in your program, then this flag will help you identify staff that missed notes.
              </li>
                <li>
                Note: an extra rating for a note that was started and never finished or deleted will result in many flags being triggered.
              </li>
              <li>
                NOTE TYPE: all residential services (except for PT/OT/Speech/Transp/BehSupp) must be Service/Treatment Plan Linked notes.
              </li>
              <li>
                NAME CHECKER: there may be false positives.  Please don't use names of individuals in notes other than their own.
              </li>
            </ul>
            '''

            html+=df_html + notes+ "</body></html>"
            #print(html)
            # Turn these into plain/html MIMEText objects
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")

            # Add HTML/plain-text parts to MIMEMultipart message
            # The email client will try to render the last part first
            message.attach(part1)
            message.attach(part2)
            try:
                server.sendmail(sender_email, receiver_email, message.as_string())
            except smtplib.SMTPSenderRefused as e:
                errors_and_warnings['errors'].append(str(e))
            except smtplib.SMTPServerDisconnected as e:
                errors_and_warnings['errors'].append(str(e))
            except:
                errors_and_warnings['errors'].append("An uknown issue occurred.")

    return errors_and_warnings
#if __name__ == "__main__":
#    sendEmail(df)
