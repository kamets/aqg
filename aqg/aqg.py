from optparse import OptionParser

import yaml
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select


def translate_sep(sep):
    if sep == 'comma':
        return ','
    elif sep == 'tab':
        return '\t'
    elif sep == 'pipe':
        return '|'

def check_valid_df_id(driver, df_id):
    try:
        driver.find_element_by_css_selector("div.errorCode")
    except NoSuchElementException:
        return
    raise Exception("The data feed id <{id}> doesn't match with any existing data feed.".format(id=df_id))

def log_in(driver, sudo_email, sudo_pass, target_email):
    sudoer_email = driver.find_element_by_id("sudoer-username")
    sudoer_password = driver.find_element_by_id("password")
    targer_user_email = driver.find_element_by_id("username")
    sudoer_email.send_keys(sudo_email)
    sudoer_password.send_keys(sudo_pass)
    targer_user_email.send_keys(target_email)
    driver.find_element_by_css_selector(".submit").click()
    return driver

def get_bucket(driver, destination):
    df_bucket = "https://hub.signal.co/sites/LeosxDl/destinations"
    driver.get(df_bucket)
    driver.find_element_by_link_text(destination).click()
    bucket = driver.find_element_by_id("add-destination_bucket").get_attribute('value')
    return bucket

def get_fields(driver, df_id):
    df_properties= 'https://hub.signal.co/sites/LeosxDl/data-feeds/{df_id}/data-collection'.format(df_id=df_id)
    driver.get(df_properties)
    check_valid_df_id(driver, df_id)

    fields_li = driver.find_element_by_id("fields") \
                      .find_elements_by_tag_name("li")
    fields = {}
    for li in fields_li:
        f = li.find_element_by_tag_name("input")
        fields[f.get_attribute('value')] = "string"
    return fields

def get_configs(driver, df_id):
    df_destinations= 'https://hub.signal.co/sites/LeosxDl/data-feeds/{df_id}/destinations'.format(df_id=df_id)
    driver.get(df_destinations)
    check_valid_df_id(driver, df_id)

    configs = {}

    # table name
    table_name = '_'.join(driver.find_element_by_id('page-name-heading').text.lower().split(' '))
    configs['table_name'] = table_name

    #destination
    destination = driver.find_element_by_css_selector("label[for='5362']").text
    configs['destination'] = destination

    # format
    fmt_select = Select(driver.find_element_by_id('format'))
    fmt_selected_option = fmt_select.first_selected_option
    format = fmt_selected_option.get_attribute("value")
    configs['format'] = format

    # seperator
    sep_select = Select(driver.find_element_by_id('fieldSeparator'))
    sep_selected_option = sep_select.first_selected_option
    separator = sep_selected_option.get_attribute("value")
    configs['separator'] = separator

    # upload dir
    upload_dir = driver.find_element_by_id('directory').get_attribute("value")
    configs['upload_dir'] = upload_dir

    # included column name
    with_header = driver.find_element_by_id('header').get_attribute("value")
    configs['with_header'] = with_header
    return configs

def construct_sql(database_name, configs, bucket, fields):
    create_db = "CREATE DATABASE IF NOT EXISTS {db};\n".format(db=database_name)
    fmt_fields = ""
    for k, v in fields.items():
        fmt_fields += '`{name}` {type},\n'.format(name=k, type=v)
    fmt_fields = fmt_fields[:-2]
    create_table = "CREATE EXTERNAL TABLE IF NOT EXISTS {db}.{table_name} (\n" \
                      "{fds}\n"\
                    ")\n".format(db=database_name, table_name=configs['table_name'], fds=fmt_fields)
    row_format_serde = "ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'\n"
    with_serdeproperities = "WITH SERDEPROPERTIES (\n" \
                            "'separatorChar' = '{field_separator}',\n" \
                            "'quoteChar' = '\\\"'\n" \
                            ") ".format(field_separator=translate_sep(configs['separator']))
    full_path = bucket + configs['upload_dir'] + '/'
    location = "LOCATION 's3://{loc}'\n".format(loc=full_path)
    skip_headers = ", 'skip.header.line.count'='1'" if configs['with_header'] == 'true' else ""
    tblproperties = "TBLPROPERTIES ('has_encrypted_data'='false'{skip});".format(skip=skip_headers)

    return {
        "db": create_db,
        "table": create_table + row_format_serde + with_serdeproperities + location + tblproperties
    }

def print_query(query):
    print("==" * 15, 'CREATE DATABASE QUERY', "==" * 15, '\n')
    print(query['db'])
    print("==" * 15, 'CREATE TABLE QUERY', "==" * 15, '\n')
    print(query['table'])
    print("\n", "==" * 20, 'END', "==" * 20)

def parse_cmd():
    # parse cmd line
    parser = OptionParser()
    parser.add_option("-d", "--db", dest="database_name", help="Database name", metavar="DATABASE_NAME")
    parser.add_option("-i", "--id", dest="data_feed_id", help="Data feed id", metavar="DATA_FEED_ID")

    # parse cmd line
    (options, args) = parser.parse_args()
    options_dict = vars(options)
    database_name = options_dict["database_name"]
    data_feed_id = options_dict["data_feed_id"]

    # check data feed id
    if data_feed_id is None:
        raise Exception("Please enter a data feed id.")

    # check database name
    if database_name is None:
        raise Exception("Please enter a database.")

    print("You entered: {op}".format(op=options_dict))
    return options_dict

def get_user_conf():
    # get user conf
    try:
        user_conf = yaml.load(open('secret.yml'))
    except OSError:
        fname = 'secret.yml'
        with open(fname, 'w') as f:
            correct_flag = False
            while not correct_flag:
                email = input("Please enter your email: ")
                pwd = input("Please enter your password: ")
                target = input("Please enter target user email: ")
                user_conf = {
                    "secret": {
                        "email": email,
                        "password": pwd,
                        "target": target
                    }
                }
                print("You enter: {credential}".format(credential=user_conf))
                while True:
                    ans = input("Are those correct?[Y/n]")
                    if ans.lower() not in ('y', 'n'):
                        print("Sorry, I don't understand your response.")
                    else:
                        correct_flag = ans.lower() == 'y'
                        break
            print("Confirmed. Your credentials are saved in {file}.".format(file=fname))
            yaml.dump(user_conf, f, default_flow_style=False)
    return user_conf

def main():
    # get db and data feed id
    options = parse_cmd()
    database_name = options['database_name']
    data_feed_id = options['data_feed_id']

    # get user conf
    user_conf = get_user_conf()

    # start building query
    print("Building query takes a while, we really appreciate your patience...")

    # get credential
    sudoer_email = user_conf['secret']['email']
    sudoer_password = user_conf['secret']['password']
    targer_user_email = user_conf['secret']['target']

    # start browser
    start_url = 'https://hub.signal.co/sudo'
    driver = webdriver.Chrome()
    driver.get(start_url)

    # login
    driver = log_in(driver, sudoer_email, sudoer_password, targer_user_email)
    if driver.current_url == start_url:
        raise Exception("login failed. Please make sure your `secret.yaml` file contains the right credentials.")

    # get all configs
    configs = get_configs(driver, data_feed_id)
    if configs['format'] != 'csv':
        raise '{} format not supported'.format(configs['format'])

    # get table fields
    fields = get_fields(driver, data_feed_id)

    # get bucket name
    bucket = get_bucket(driver, configs['destination'])

    # build query
    query = construct_sql(database_name, configs, bucket, fields)
    print_query(query)
    return

if __name__ == "__main__":
    main()
