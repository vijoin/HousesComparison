import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from write_json import write_to_json_file


class Spider:

    def __init__(self) -> None:
        self.base_url = "https://listado.mercadolibre.com.uy/inmuebles/{}/{}/{}/{}/_Desde_{}_PriceRange_{}UYU-{}UYU_NoIndex_True"
        self.property_type = 'casas'
        self.contract_type = 'alquiler'
        self.rooms = '3-dormitorios'
        self.city = 'canelones'
        self.min_price = 19500
        self.max_price = 19500
        self.driver = self.get_driver()

    def main(self):
        property_links = self.get_all_links()

        res_data = []
        for property_link in property_links:
            res_data.append(self.parse_page(property_link))
        
        write_to_json_file('meli_20220411.json', res_data)
        
        self.driver.close()

    def get_page_url(self, page_number):
        return self.base_url.format(
            self.property_type,
            self.contract_type,
            self.rooms,
            self.city,
            str(48*page_number+1),
            self.min_price,
            self.max_price,
        )

    def get_all_links(self):
        links = []
        for page in range(0, 1):
            page_link = self.get_page_url(page)
            self.driver.get(page_link)
            time.sleep(1)
            try:
                links_elem = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//ol/li//a[@class="ui-search-link"]'))
                )
                links.extend([link.get_attribute('href') for link in links_elem])
                print('\n\n # of links:{} \n\n'.format(len(links)))
            except TimeoutException:
                break
        return links
    
    def parse_page(self, page_link):
        self.driver.get(page_link)
        total_area, rooms, bathrooms  = [feat.text for feat in self.driver.find_elements(By.XPATH, '//div[@class="ui-pdp-highlighted-specs-res__icon-label"]')]
        name = self.driver.find_element(By.XPATH, '//h1[@class="ui-pdp-title"]').text
        price = int(self.driver.find_element(By.XPATH, '//span[@class="andes-money-amount__fraction"]').text.replace('.', ''))
        address = self.driver.find_element(By.XPATH, '//figure[@class="ui-pdp-media__figure"]/following-sibling::div/p').text

        return {
            'name': name,
            'price': price,
            'property_type': self.property_type,
            'url': page_link,
            'features': {
                'total_area': total_area,
                'rooms': rooms,
                'bathrooms': bathrooms,
            },
            'location': {
                # 'state': str,
                'city': self.city,
                'address': address,
            },
        }

    def get_driver(self):
        options = Options()
        ua = UserAgent()
        userAgent = ua.random
        options.add_argument(f'user-agent={userAgent}')
        return webdriver.Chrome('chromedriver', chrome_options=options,)

if __name__ == '__main__':
    Spider().main()

# d = {
        #     'name': str,
        #     'ref': str,
        #     'price': float,
        #     'common_expenses': int,
        #     'location': {
        #         'state': str,
        #         'city': str,
        #         'address': str,
        #     },
        #     'features': {
        #         'rooms': int,
        #         'total_area': int,
        #         'bathrooms': int,
        #     },
        #     'property_type': str,
        #     'supported_insurance_companies': list,
        #     'real_state_agency': {
        #         'name': str,
        #         'phone': str,
        #     },
        #     'url': str,

        # }