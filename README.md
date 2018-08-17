## Athena Query Generator

An Amazon Athena Query Generator built with Selenium and Python3.

### Details that don't matter

author: Ruiqi Li (rli@signal.co)
date: Aug 14 2018

### Words from author 

Hi Ladies and Gentlemen,
 	
   This is Ruiqi Li, 2018 summer software engineering intern, at your service.
	
	Amazon’s Athena, just like every other girls in our real life, is lovely to stay with but at a cost, which is your time. 
	Huge thanks to Nate Granatir for coming up this idea to automate the table fields extraction from Datahub.
	
	It’s time to talk about time efficiency.

	Yo.

	- Ruiqi

### Step 0: Get the directory

First thing first, get the code!
Also make sure you have access to `hub.signal.co`

### Step 1: Set up your environment

To do this:

	> // install all required packages
	> pip install -r requirements.txt

### Step 2: Keep your credentials save

To make everything easy, please take 3s to create a `secret.yml` file which contains the following information:
	
secret:
    email: <your signal email>
	password: <your hub password>
	target: jgraeser@signal.co or <your target email>

Sssh, keep it safe and don't tell anyone!

### Step 3: Run script. Run!

If you are a command line lover, please enjoy these 10 seconds by reading the following:

Usage: aqg.py [options]

Options:
	-h, --help        show this help message and exit
	-d DATABASE_NAME, --db=DATABASE_NAME
						Database name
	-i DATA_FEED_ID, --id=DATA_FEED_ID
						Data feed id

TL;DR? FINE.
	> python aqg.py -d <database_name> -i <data_feed_id> 

### Step 4: Copy the query to Amazon S3 Bucket and use the time your saved to enjoy a cup of tea.

C'mon, you don't need help on doing copy-and-paste, do you?

### See error?
- Missing Package
	Always try this first:
	> pip install xxx
	Not working? Grow up and Google it.
- Can't start the script
	Make sure you include all flags, those are REQUIRED!
	You don't wanna create a table on someone else's database right?
- Credential Error
	Check you `secret.yml` file to make sure those secrets are correctly entered.
- Data_feed_id Error
	Nah, get a new data_feed_id dude, the one you entered does not exist.
- Other Error
	You are on your own...Haha, i'm kidding...No I'm serious...

### Need help...

	Email Ruiqi Li (rli@signal.co) if she hasn't been fired.
	She is more than happy (most of the time) to help you.

### Peace out



	


	

	


