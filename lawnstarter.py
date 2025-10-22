from seleniumbase import BaseCase
import random

#The Page Object can be splited to another script. I just keep it here to turn easier to follow...
class pageobjectsPO:

    def open_start_page(self):
        """
        Open the URL to start the test
        """

        base_url = (
            "https://dev-signup-web.lawnstarter.com/cart/contact-info/"
            "?address=1016 Kirk Street, Orlando, FL 32808, Orlando, FL 32808"
        )

        full_url = (
            "https://dev-signup-web.lawnstarter.com/cart/contact-info/"
            "?address=1016 Kirk Street, Orlando, FL 32808, Orlando, FL 32808"
            "&name=Jay+Doe&phone=999-999-9999&intent=bushTrimming&googlePlace=true"
        )

        self.open(base_url)
        self.open_if_not_url(full_url)
        self.maximize_window()

    def choose_yard_location(self, *labels):
        """
        Function created to select Yard location by the text.
        Should use the same as it's on the page
        """
        for label in labels:
            selector = f"//div[contains(@data-testid, 'checkbox')][.//text()[contains(., '{label}')]]"
            self.click(selector)


    def qt_shrubs_and_hedges(self, input_selector, option_index):
        """
        Expand the React Dropdown and select the option by the INDEX.
        All options has same structure for selector
        """
        self.click(input_selector)
        self.wait_for_element_visible("//div[@role='option']", timeout=3)
        # Build the XPATH changing only the INDEX
        xpath = f"(//div[@role='option'])[{option_index}]"
        # Select the INDEX
        self.click(xpath)


    def click_button_by_text(self, testid, text):
        """
        All the options have the same data-testid, so you can choose the option by the TEXT
        """
        # Xpath to select the data-testid number (1 or 2) and text (monthly, weekly...)
        xpath = f"//div[@data-testid='{testid}' and normalize-space(text())='{text}']"
        self.wait_for_element_visible(xpath)
        self.click(xpath)


    def select_calendar_day_next_month(self, input_selector, day=10):
        """
        Expand and click at day 10 for next month. You can choose any day you want with this function
        """
        # Expand the calendary
        self.click(input_selector)

        # Go to the next month
        self.click("svg[data-testid='ArrowRightIcon']")

        # Waiter to avoid problems
        self.wait_for_element_visible("div.MuiDayCalendar-monthContainer button.MuiPickersDay-root", timeout=3)

        # Each day has button identifier. In that case, we can choose each day like it was a button number
        day_buttons = self.find_elements("div.MuiDayCalendar-monthContainer button.MuiPickersDay-root")
        for btn in day_buttons:
            if btn.text.strip() == str(day):
                btn.click()
                return
            
        # In case the next month has less days (like 31 for a month with 30 days)
        raise Exception(f"Day {day} not found in next month's calendar")


    def fill_random_email(self):
        """
        Create a random email (because it must be single everytime)
        danielmaiaXXXXXX@hireme.com
        where XXXXXX are 6 random numbers
        """
        random_digits = "".join([str(random.randint(0, 9)) for _ in range(6)])
        email = f"danielmaia{random_digits}@hireme.com"

        # Fill email field
        self.type('input[data-testid="text-input-email"]', email)
        return email #in case you need to check the created email
    

    def fill_credit_card_info(self, card_number, exp_date, cvc):
        """
        Fill data thinking about the iFrames
        Args:
            card_number: Card Number
            exp_date: Card valid date
            cvc: Security Code
        """

        fields = {
            "cardnumber": card_number,
            "exp-date": exp_date,
            "cvc": cvc
        }

        for name, value in fields.items():
            selector = f"input[name='{name}']"
            self.switch_to_frame_of_element(selector)
            self.type(selector, value)
            self.switch_to_default_content()


class LawnStarterTests(BaseCase, pageobjectsPO):
    
    def setUp(self):
        super().setUp()
        #self.open_start_page() 
    
    def test_recording(self):     

        #Starting the test
        self.open("https://dev-signup-web.lawnstarter.com/cart/contact-info/?address=1016 Kirk Street, Orlando, FL 32808, Orlando, FL 32808")
        self.open_if_not_url("https://dev-signup-web.lawnstarter.com/cart/contact-info/?address=1016 Kirk Street, Orlando, FL 32808, Orlando, FL 32808&name=Jay+Doe&phone=999-999-9999&intent=bushTrimming&googlePlace=true")
        self.maximize_window()   

        #Page1
        # Select Full Yard option
        self.choose_yard_location("Full Yard")

        # Select 3 (position 4) shrubs and hedges
        self.qt_shrubs_and_hedges("#react-select-2-input", 4)

        # Select 0 (position 1) shrubs and hedges
        self.qt_shrubs_and_hedges("#react-select-3-input", 1)

        # Select 0 (position 1) shrubs and hedges
        self.qt_shrubs_and_hedges("#react-select-4-input", 1)

        # Click to advance for next page
        self.click("button[data-testid='get-my-quote-btn']")
        
        #Page2
        # Assert we went to next page
        self.assert_text_visible("Pick your Bush Trimming plan")

        # Select the plan by TEXT
        self.click_button_by_text("undefined-col1", "Every 2 Weeks")

        # Using the function to click on day 10 on next month. The calendar ID is changing everytime, thats why I took by xpath instead of CSS Selector
        calendar_input = '/html/body/div[1]/div/div/section/div/section/div/div[2]/form/div[2]/div/input'
        self.select_calendar_day_next_month(calendar_input, day=10)

        # Click on CONTINUE button. We can turn into a function, but it's a simple 1 line action
        self.click('button[data-testid="button"]')

        #Page3
        # Assert we went to next page
        self.assert_text_visible("Create your account")

        # Verify if First and Last name by default are filled
        firstName = self.get_value("#firstName")
        lastName = self.get_value("#lastName")
        self.assert_equal("Jay", firstName)
        self.assert_equal("Doe", lastName)

        #The email should be different everytime
        self.fill_random_email()

        #Function to fill card data
        self.fill_credit_card_info(
            card_number="4111111111111111",
            exp_date="06/30",
            cvc="123"
        )

        #Accept terms
        self.click('div[data-testid="checkbox-0"]')

        #Go to next page
        self.click('div[data-testid="button-text"]')

        #Page4
        # Assert we went to next page
        self.assert_text_visible('What other services do you need?')

        #Choose NO THANKS and go ahead
        self.click('button[data-testid="no-thanks-btn"]')

        #Page5
        # Assert we went to next page
        self.wait_for_text_visible("Property Details")
        check_page = self.get_current_url()
        self.assert_equal("https://dev-legacy-my.lawnstarter.com/onboarding/property-info", check_page)

        #TEST FINISHED
        self.sleep(10)
