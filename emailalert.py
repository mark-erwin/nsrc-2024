from email.message import EmailMessage
import ssl
import smtplib

password = "labfrpaywwohdngg"
em = EmailMessage()


def send_alert(i, plate, confidence, filename, violations, location, ddate, dtime):
    auth_email = "programdevtest@gmail.com"
    violations = ", ".join(violations)

    with open(filename, 'rb') as f:
        img_data = f.read()

    try:
        reg_email = i["E-mail"]
        recipients = [auth_email, reg_email]

        regplate = i["Plate"]
        name = i["Name"]
        qid = i["QID"]
        qidexp = i["QID Expiry"]
        licensenum = i["License Number"]
        licenseval = i["License Validity"]

        subject = ("Traffic Violation Alert: " + plate)

        body = ("Plate: " + regplate +
                "\nName: " + name +
                "\n\nQID: " + qid +
                "\nQID Expiry: " + qidexp +
                "\n\nLicense Number: " + licensenum +
                "\nLicense Validity: " + licenseval +
                "\n\nViolations: " + violations +
                "\nConfidence: " + confidence +
                "\n\nLocation: " + location +
                "\nDate: " + ddate +
                "\nTime: " + dtime)

        em['From'] = auth_email
        em['To'] = ", ".join(recipients)
        em['subject'] = subject
        em.set_content(body)
        em.add_attachment(img_data, maintype="image", subtype="jpg", filename=filename)

    except KeyError:
        recipients = auth_email

        subject = ("Traffic Violation Alert: " + plate)
        body = ("Plate: " + plate + "\nViolations: " + violations + "\nConfidence: " + confidence + "\n\nLocation: " + location + "\nDate: " + ddate + "\nTime: " + dtime)

        em['From'] = recipients
        em['To'] = auth_email
        em['subject'] = subject
        em.set_content(body)
        em.add_attachment(img_data, maintype="image", subtype="jpg", filename=filename)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(('smtp.gmail.com'), 465, context=context) as smtp:
        smtp.login(auth_email, password)
        smtp.sendmail(auth_email, recipients, em.as_string())
        del em['To']
        del em['From']
        del em['subject']
        em.clear_content()


