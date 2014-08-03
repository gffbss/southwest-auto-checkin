import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

SOUTHWEST_CHECKIN_URL = 'http://www.southwest.com/flight/retrieveCheckinDoc.html'


class ResponseStatus:
    def __init__(self, code, search_string):
        self.code = code
        self.search_string = search_string


RESPONSE_STATUS_SUCCESS = ResponseStatus(1, "Continue to Create Boarding Pass/Security Document? ")
RESPONSE_STATUS_TOO_EARLY = ResponseStatus(0, "Boarding Pass is more than 24 hours")
RESPONSE_STATUS_INVALID = ResponseStatus(-1, "The confirmation number entered is invalid.")
RESPONSE_STATUS_RES_NOT_FOUND = ResponseStatus(-2, "we were unable to retrieve your reservation from our database")
RESPONSE_STATUS_INVALID_PASSENGER_NAME = ResponseStatus(-3, "The passenger name entered does not match one of the "
                                                            "passenger names listed under the confirmation number")
RESPONSE_STATUS_UNKNOWN_FAILURE = ResponseStatus(-100, None)


def _post_to_southwest_checkin(confirmation_num, first_name, last_name):
    """

    :param confirmation_num:
    :param first_name:
    :param last_name:
    :return:
    """
    payload = {
        'confirmationNumber': confirmation_num,
        'firstName': first_name,
        'lastName': last_name
    }
    response = requests.post(SOUTHWEST_CHECKIN_URL, data=payload)
    return response


def attempt_checkin(confirmation_num, first_name, last_name, **kwargs):
    response = _post_to_southwest_checkin(confirmation_num, first_name, last_name)

    # todo: try post on save and fail if not success or more than 24 hour status
    if response.status_code is 200:
        if response.content.find(RESPONSE_STATUS_SUCCESS.search_string) is not -1:
            print 'Success for reservation ' + confirmation_num
            if kwargs.get('email', None):
                try:
                    browser = webdriver.Firefox()
                    browser.implicitly_wait(5)
                    browser.get(str(response.url))
                    browser.find_element_by_id('printDocumentsButton').click()
                    checkboxes = browser.find_elements_by_xpath("//input[@type='checkbox']")
                    for checkbox in checkboxes:
                        if checkbox.is_selected():
                            checkbox.click()
                    browser.find_element_by_id('optionEmail1').click()
                    browser.find_element_by_id('emailAddress').clear()
                    browser.find_element_by_id('emailAddress').send_keys(kwargs['email'])
                    browser.find_element_by_id('checkin_button').click()
                    browser.close()
                except WebDriverException as e:
                    print "Exception thrown while attempting to email boarding pass: " + e
                    RESPONSE_STATUS_UNKNOWN_FAILURE.code, response.content
            return RESPONSE_STATUS_SUCCESS.code, response.content
        elif response.content.find(RESPONSE_STATUS_TOO_EARLY.search_string) is not -1:
            # more than 24 hours before
            print 'Checking in too early for reservation ' + confirmation_num
            return RESPONSE_STATUS_TOO_EARLY.code, response.content
        elif response.content.find(RESPONSE_STATUS_INVALID.search_string) is not -1:
            # invalid format
            print 'Invalid confirmation number ' + confirmation_num
            return RESPONSE_STATUS_INVALID.code, response.content
        elif response.content.find(RESPONSE_STATUS_INVALID.search_string) is not -1:
            # incorrect name or confirmation number
            print "Can't find reservation in data base " + confirmation_num
            return RESPONSE_STATUS_RES_NOT_FOUND.code, response.content
        elif response.content.find(RESPONSE_STATUS_INVALID_PASSENGER_NAME.search_string) is not -1:
            print "Invalid passenger name " + confirmation_num
            return RESPONSE_STATUS_INVALID_PASSENGER_NAME.code, response.content
        else:
            print response.content
            print 'WTF: '
            return RESPONSE_STATUS_UNKNOWN_FAILURE.code, response.content

    print 'received status other then 200 for ' + confirmation_num
    print response.content
    return RESPONSE_STATUS_UNKNOWN_FAILURE.code, response.content
