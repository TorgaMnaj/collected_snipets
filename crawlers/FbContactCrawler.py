import json
from pprint import pprint
import requests
from bs4 import BeautifulSoup as BS
import facebook

class FbBaseCrawler(object):
    
    default_headers = {
        'Accept'                    :'*/*',
        'Cache-Control'             :'no-cache',
        'upgrade-insecure-requests' :'1',
        'User-Agent'                :'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/62.0.3202.94 Chrome/62.0.3202.94 Safari/537.36'
        # or what ever User-agent you wnat 
    }
    
    _FB_API_PROFILE_CONTACT_URL = 'https://www.facebook.com/profile/async/infopage/nav/'
    
    def __init__(self,email,password,users_fbid:list=None):
        self.r              = requests.Session()
        self._user          = email
        self._pass          = password
        self._users_fbid    = users_fbid or []
        self.fbgraph        = facebook.GraphAPI('..your fb token..')
        self.r.cookies.update({
            'c_user'   : '<user_fbid>',
            ... # other attributes of the cookies
        })
    
    def crawl_now(self):
        
        print('Crawl now...')
        parsed_data = []
        for user_fbid in self._users_fbid:
            resp = self._post(self._FB_API_PROFILE_CONTACT_URL,
                              params    =self._param_query(user_fbid),
                              data      =self._data_payload(user_fbid),
                              headers   ={'Content-Type':'application/x-www-form-urlencoded'})
            json_resp = json.loads(resp.text[9:])
            html = json_resp.get('domops',[[{}]])[0][-1].get('__html')
            
            if not html:
                print('Id error %s'%user_fbid)
                continue
                
            data = self._extract_contract_data_from_html(html)
            data.update({
                'name'  :self.fbgraph.get_object(user_fbid).get('name','')
            })
            parsed_data.append(data)
        
        print('Export now...')
        self._export_to_csv(parsed_data)
        print('Export done')

    def _export_to_csv(self,data):
        import csv
        with open('data_output.csv', 'w') as csv_file:
            fieldnames = ['name','email','job', 'address', 'phone', 'website']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for dat in data:
                writer.writerow(dat)

    def _extract_contract_data_from_html(self,html):
        tree = self.parser(html)
        email = tree.select_one("span._50f9._50f7") or tree.select_one("span._c24._2ieq a[href^='mailto']")
        address = tree.select_one("span.fsm")
        phone = tree.select_one('span[dir="ltr"]')
        website = tree.select_one('a[rel="me noopener nofollow"]')
        job = tree.select_one('div._c24._50f4')
        return {
            'email'     :email.text if email else '',
            'address'   :address.text.strip() if address else '',
            'phone'     :phone.text if phone else '',
            'website'   :website.text if website else '',
            'job'       :job.text.lstrip() if job else '',
        }
    
    def _get(self,url,params=None,headers=None,cookies=None):
        if params is None:
            params = {}
        if cookies is None:
            cookies = {}
        h=self.default_headers
        if headers:
            h.update(headers)
        return self.r.get(url,params=params,headers=h,cookies=cookies,timeout=10)
    
    
    def _post(self,url,params=None,data=None,headers=None):
        h=self.default_headers
        if headers is not None:
            h.update(headers)
        return self.r.post(url,params=params,data=data,headers=h,allow_redirects=False,timeout=10)
    
    def _fblink(self,link):
        return 'https://www.facebook.com%s' % str(link)
    
    def parser(self, html):
        return BS(html, 'html.parser')
    
    def _login_fb(self):
        
        print('Fresh login')
        try:
            self._get('https://www.facebook.com')
            data = {
                'email': self._user,
                'pass': self._pass,
            }
            login = self._post('https://www.facebook.com/login.php?login_attempt=1&amp;lwv=110', data=data, headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            })
        except Exception as e:
            print('Error login')
            raise e
        self._user_fbid = self.r.cookies.get('c_user')
        return login.status_code == 302 and self._user_fbid
    
    def _data_payload(self,profile_id):
        return {
            '__user'  : '<user_fbid>',
            '__a'     : '1',
            '__req'   : 'bg',
            '__be'    : '1',
            '__pc'    : 'PHASED:DEFAULT',
            'fb_dtsg' : 'AQEOmmADmczS:',
            '__spin_b': 'trunk',
        }
    def _param_query(self,profile_id):
        return {
            'viewer_id'     : '<user_fbid>', #self._user_fbid,
            'profile_id'    : '%s'%profile_id, #profile_id,
            'dom_section_id': 'u_fetchstream_21_0',
            'section'       : 'overview',
            'dpr'           : '1',
            'lst'           : '<user_fbid>:%s:<current_timestamp>'%profile_id,
        }


crawler = FbBaseCrawler(
    email='xxx',
    password='yyy',
    users_fbid=['10000xxx'] # list of profile facebook ids
)
crawler.crawl_now()

