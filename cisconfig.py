#!/usr/bin/python
"""
cisconfig.py 

Script that automatically configures Cisco wireless controllers
to change the password for as many IP addresses as desired. Login 
credentials have been replaced with asterisks ("uname****") within the
code.

Written by Gabriel Miller
6/9/2016

"""

def main():

    """
    Parse IP_LIST.txt for IP and location info.

    The IP_LIST.txt file contains a list of IP addresses for 
    the wireless controllers as well as a location, delimited 
    with a colon.
    """
    def parse_ips():
        f = open("IP_LIST_TEST.txt", "r")
        line_list = []
        for line in f:
            line = line.strip('\n')
            line_list.append(line)
        f.close()
        return line_list

    """
    Generate randomized password in format: 
    "pass****"
    """
    def generate_password():
    	import random
        pw = 'pass'
        pw_ext = ''.join(["%s" % random.randint(0, 9) for num in range(0, 4)])
        final_pw = pw + str(pw_ext)
        print "Generated Password: " + final_pw
        return final_pw

    """
    Connect to specified controller with ip address using SSH2 
    and set the new password.
    """
    def configure_controller(ip_info, uname, pword, new_pw):
        import paramiko
        import time

        # Open the log file to append data
        f = open('SHELL_LOG.txt', 'a')

        # Split ip_info into IP address and location
        ip, location = ip_info.split(":")
        f.write("############################################")
        f.write("  CISCO CONFIGURATION LOG FOR: " + location)
        f.write("############################################\n\n")
        print "Configuring controller at IP: " + ip + " in " + location

        # Setup client and connect via SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(ip, username=uname, password=pword)
            f.write("SSH Connection established with %s" % ip)
            print "SSH Connection established with %s" % ip
        except:
            f.write("Failed to establish SSH connection with %s\n" % ip)
            print "Failed to establish SSH connection with %s" % ip

        # Invoke an interactive shell session
        remote_conn = ssh.invoke_shell()
        f.write("Interactive SSH session established\n")
        print "Interactive SSH session established"

        # Login automation process (sleep for time between prompts)
        time.sleep(3)
        remote_conn.send("uname******\n")
        remote_conn.send("pword******\n")

        # Configure controller with new password
        time.sleep(3)
        remote_conn.send("config wlan disable 2\n")
        time.sleep(3)
        remote_conn.send(
            "config wlan security wpa akm psk set-key ascii " + new_pw + " 2\n")
        time.sleep(3)

        remote_conn.send("save config\n")
      	time.sleep(3)
        remote_conn.send("y")
        time.sleep(8)

      	# TODO Send output to text file, and email to enterprise support
        output = remote_conn.recv(3000)

        # Close connection
        f.write(output)
        print output
        ssh.close()
        f.write("SSH Connection Closed.\n")
        print "SSH Connection Closed."
        f.close()

    """
	Send email notification containing new password.
	"""
    def send_email(user, recipient, subject, body):
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        #TO = recipient if type(recipient) is list else [recipient]

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = user
        msg['To'] = ", ".join(recipient)

        # Create the body of the message (a plain-text and an HTML version).
        text = "Hi!\n\nThe new wifi password is " + body
        html = """\
		<html>
		<body>
		<div id="wifi">
		    <h3>The Guest Wifi Password Has Changed!</h3>
		    <span><b>     New Password: </b>""" + body + """</span>
		</div> 
		</body>      
		</html>
		"""
        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        msg.attach(part1)
        msg.attach(part2)

        # Send message.
        try:
            server = smtplib.SMTP("SMTP server****", 25)
            server.ehlo()
            server.sendmail(user, recipient, msg.as_string())
            server.close()
            print 'successfully sent the mail'
        except:
            print "failed to send mail"

    """
    PRIMARY RUN SEQUENCE
    """

    # Clear shell log file
    open('SHELL_LOG.txt', 'w').close()

    # Parse text file to list
    ip_list = parse_ips()

    # Generate Password
    new_pw = generate_password()

    # Configure each controller in list
    for ip_address in ip_list:
        configure_controller(ip_address, 'uname****', 'pword****', new_pw)

    # Send out email containing new password information
    send_email('FROM_EMAIL', 'TO_EMAIL', 'New Password for Guest Wifi', new_pw)

if __name__ == "__main__":
    main()
